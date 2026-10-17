"""Exercise the real OpenAI SDK against a local Responses API HTTP fixture."""

import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from eval.backends import FINAL_ANSWER_SCHEMA, make_judge, make_predictor, validate_model_pair
from eval.post_audit import parser, run
from eval.pre_audit.pipeline import JudgeSettings, _make_adapted_judge, _ugphysics_auxiliary_judge, Problem
from utils.openai_api import generate
from utils.openai_compatible import generate as compatible_generate, OutputTruncatedError


VERDICT = {'extracted_final_answer': '2', 'reasoning': 'Equivalent.',
           'correct': 'yes', 'confidence': 100, 'strict': True}


def response(model='gpt-5.6-sol', text='2'):
    return {'id': 'resp_test', 'object': 'response', 'created_at': 0,
            'model': model, 'status': 'completed', 'error': None, 'incomplete_details': None,
            'output': [{'type': 'message', 'id': 'msg_test', 'role': 'assistant',
                        'status': 'completed', 'content': [
                            {'type': 'output_text', 'text': text, 'annotations': []}]}],
            'usage': {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}}


class OpenAIAPITests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.reply = None
        self.http_status = 200
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                owner.requests.append((self.path, payload))
                schema = payload.get('text', {}).get('format', {}).get('schema', {})
                answer = (json.dumps({k: VERDICT[k] for k in schema['required']}) if 'correct' in schema.get('properties', {}) else
                          json.dumps({'final_answer': '2'}) if schema else '2')
                default = (response(payload['model'], answer) if self.path.endswith('/responses') else
                           {'model': payload['model'], 'choices': [
                               {'finish_reason': 'stop', 'message': {'content': '2'}}]})
                data = json.dumps(owner.reply or default).encode()
                self.send_response(owner.http_status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.shutdown)
        self.environment = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'local-test-key',
            'OPENAI_BASE_URL': f'http://127.0.0.1:{self.server.server_port}/v1',
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def call(self, **kwargs):
        return generate('QUESTION', model='gpt-5.6-sol', system_prompt='SYSTEM',
                        reasoning_effort='high', max_output_tokens=1234, timeout=5, **kwargs)

    def test_wire_contract_and_provenance(self):
        result = self.call(output_schema=FINAL_ANSWER_SCHEMA)
        path, payload = self.requests[0]
        self.assertEqual(path, '/v1/responses')
        self.assertEqual(payload['model'], 'gpt-5.6-sol')
        self.assertEqual(payload['max_output_tokens'], 1234)
        self.assertEqual(payload['reasoning'], {'effort': 'high'})
        self.assertEqual(payload['instructions'], 'SYSTEM')
        self.assertEqual(payload['tools'], [])
        self.assertFalse(payload['store'])
        self.assertTrue(payload['text']['format']['strict'])
        self.assertEqual(result['actual_model'], 'gpt-5.6-sol')
        self.assertEqual(result['usage']['total_tokens'], 15)

    def test_image_is_embedded(self):
        image = self.root / 'image.png'
        image.write_bytes(b'\x89PNG\r\n\x1a\nlocal-test')
        self.call(image=str(image))
        block = self.requests[0][1]['input'][0]['content'][0]
        self.assertEqual(block['type'], 'input_image')
        self.assertTrue(block['image_url'].startswith('data:image/png;base64,'))

    def test_incomplete_empty_and_tool_outputs_remain_pending(self):
        for value in [
            {**response(), 'status': 'incomplete', 'incomplete_details': {'reason': 'max_output_tokens'}},
            response(text=''),
            {**response(), 'output': [{'type': 'function_call', 'name': 'unexpected',
                                      'call_id': 'call_test', 'arguments': '{}'}]},
        ]:
            self.reply = value
            before = len(self.requests)
            with self.assertRaises(ValueError):
                self.call()
            self.assertEqual(len(self.requests), before + 1)

    def test_model_substitution_is_rejected(self):
        self.reply = response(model='different-model')
        with self.assertRaisesRegex(ValueError, 'model mismatch'):
            self.call()

    def test_refusal_is_a_model_outcome_but_judge_refusal_is_pending(self):
        self.reply = response()
        self.reply['output'][0]['content'] = [{'type': 'refusal', 'refusal': 'Cannot answer.'}]
        self.assertTrue(self.call()['refused'])
        args = parser().parse_args(['--dataset', 'cmt', '--output', str(self.root),
                                   '--judge-openai-backend', 'api'])
        with self.assertRaisesRegex(ValueError, 'judge refused'):
            make_judge(args)({'question': 'Q', 'reference_answer': 'A'}, {'response': '2'})

    def test_authentication_error_is_not_retried(self):
        self.http_status = 401
        self.reply = {'error': {'message': 'Invalid test key', 'type': 'authentication_error'}}
        from openai import AuthenticationError

        with self.assertRaises(AuthenticationError):
            self.call()
        self.assertEqual(len(self.requests), 1)

    def test_generation_routing_and_reference_separation(self):
        args = parser().parse_args(['--dataset', 'cmt', '--output', str(self.root),
                                   '--model', 'gpt-5.6-sol', '--judge-model', 'gpt-6-astra',
                                   '--openai-backend', 'api'])
        predict = make_predictor(args, None)
        self.assertEqual(predict({'question': 'QUESTION'})['response'], '2')
        self.assertNotIn('reference_answer', json.dumps(self.requests[0][1]))

    def test_all_adapted_judges_and_ugphysics_use_selected_api(self):
        settings = JudgeSettings(openai_backend='api', reasoning_effort='low')
        problem = Problem('test', 'Q', 'REFERENCE', 'Q')
        for dataset in ('hle-physics', 'cmt', 'critpt'):
            result = _make_adapted_judge(dataset, settings)(problem, '2')
            self.assertEqual(result.get('correct', result.get('judgment', {}).get('correct')), 'yes')
            self.assertEqual(self.requests[-1][1]['reasoning']['effort'], 'low')
        with patch('eval.pre_audit.native.auxiliary_prompt', return_value='JUDGE'), patch(
                'utils.openai_api.generate', return_value={
                    'response': '## Equivalence Judgement\nTRUE', 'refused': False}) as request:
            result = _ugphysics_auxiliary_judge(problem, '2', settings)
        self.assertTrue(result['correct'])
        self.assertEqual(request.call_args.kwargs['reasoning_effort'], 'low')

    def test_full_pipeline_repeated_attempts_resume_and_backend_invalidation(self):
        data = self.root / 'data.json'
        data.write_text(json.dumps([{'id': str(i), 'question': 'Q', 'answer': 'REFERENCE'} for i in range(2)]))
        output = self.root / 'run'
        args = parser().parse_args(['--dataset', 'custom', '--data', str(data),
                                   '--output', str(output), '--attempts', '2', '--workers', '1',
                                   '--model', 'gpt-5.6-sol', '--judge-model', 'gpt-6-astra',
                                   '--openai-backend', 'api'])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run(args), 0)
            count = len(self.requests)
            self.assertEqual(run(args), 0)
        self.assertEqual(len(self.requests), count)
        self.assertEqual(count, 8)
        summary = json.loads((output / 'summary.json').read_text())['benchmarks']['custom']
        self.assertEqual(summary['mean@2'], 1)
        self.assertEqual(summary['pass@2'], 1)
        for _, payload in self.requests:
            if payload['model'] == 'gpt-5.6-sol':
                self.assertNotIn('REFERENCE', json.dumps(payload))
        args.openai_backend = 'codex'
        with self.assertRaisesRegex(ValueError, 'manifest'):
            run(args)

    def test_arbitrary_openai_compatible_endpoint(self):
        with patch.dict(os.environ, {'OPENAI_COMPAT_BASE_URL': os.environ['OPENAI_BASE_URL'],
                                     'OPENAI_COMPAT_MODEL': 'custom-physics-model'}):
            args = parser().parse_args(['--dataset', 'cmt', '--output', str(self.root),
                                       '--model', 'openai-compatible'])
            result = make_predictor(args, None)({'question': 'QUESTION'})
        self.assertEqual(result['actual_model'], 'custom-physics-model')
        path, payload = self.requests[-1]
        self.assertEqual(path, '/v1/chat/completions')
        self.assertNotIn('temperature', payload)
        self.assertNotIn('top_p', payload)

    def test_compatible_model_cannot_judge_itself_through_an_alias(self):
        args = parser().parse_args(['--dataset', 'cmt', '--output', str(self.root),
                                   '--model', 'openai-compatible'])
        for model in ('gpt-5.6-sol', 'openai/gpt-5.6-sol', 'gpt-5.6', 'gpt-5.6-sol-2026-07-01'):
            with patch.dict(os.environ, {'OPENAI_COMPAT_MODEL': model}):
                with self.assertRaisesRegex(ValueError, 'judge different'):
                    validate_model_pair(args)

    def test_compatible_truncation_refusal_and_unexpected_tools(self):
        for text in ('', 'partial answer'):
            self.reply = {'model': 'test', 'choices': [
                {'finish_reason': 'length', 'message': {'content': text}}]}
            before = len(self.requests)
            with patch.dict(os.environ, {'OPENAI_COMPAT_BASE_URL': os.environ['OPENAI_BASE_URL']}):
                with self.assertRaises(OutputTruncatedError):
                    compatible_generate('Q', system_prompt='S', reasoning_effort='high',
                                        max_output_tokens=10, timeout=5)
            self.assertEqual(len(self.requests), before + 1)
        self.reply = {'model': 'test', 'choices': [
            {'finish_reason': 'stop', 'message': {'content': None, 'refusal': 'Cannot answer.'}}]}
        with patch.dict(os.environ, {'OPENAI_COMPAT_BASE_URL': os.environ['OPENAI_BASE_URL']}):
            result = compatible_generate('Q', system_prompt='S', reasoning_effort='high',
                                         max_output_tokens=10, timeout=5)
            self.assertTrue(result['refused'])
            self.reply['choices'][0]['message'] = {'content': '2', 'tool_calls': [{'id': 'call'}]}
            with self.assertRaisesRegex(RuntimeError, 'Unexpected tool use'):
                compatible_generate('Q', system_prompt='S', reasoning_effort='high',
                                    max_output_tokens=10, timeout=5)


if __name__ == '__main__':
    unittest.main()
