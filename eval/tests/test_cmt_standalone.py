"""Keep CMT judging independent of preparation code and verify resume settings."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from eval import backends
from eval.pre_audit import cmt
from eval.pre_audit.__main__ import parser
from eval.pre_audit.pipeline import JudgeSettings, _judge_args, load_benchmark
from eval.pre_audit.runner import run


JUDGMENT = {"extracted_final_answer": "2", "reasoning": "Equivalent.",
            "correct": "yes", "confidence": 100, "strict": True}


class CMTStandaloneTests(unittest.TestCase):
    def test_codex_receives_the_preserved_contract_without_analysis_imports(self):
        captured = {}

        def complete(prompt, *, output_schema, **kwargs):
            captured.update(prompt=prompt, schema=json.loads(output_schema.read_text()))
            return SimpleNamespace(text=json.dumps(JUDGMENT), usage={},
                                   events=[{"type": "turn.completed"}])

        client = MagicMock()
        client.complete.side_effect = complete
        forbidden = {"cmt_eval": None, "cmt_eval.scoring": None, "cmt_eval.backends": None}
        with patch.dict("sys.modules", forbidden), \
                patch.object(backends, "CodexLLM", return_value=client) as constructor:
            pipeline = load_benchmark("cmt", judge_settings=JudgeSettings(codex_bin="test-codex"))
            problem = pipeline.problems[0]
            result = pipeline.evaluate(problem.id, "candidate")
        prompt = (cmt.PROMPTS / "cmt_judge.txt").read_text()
        self.assertEqual(captured["prompt"], prompt.format(
            question=problem.question, correct_answer=problem.reference_answer, response="candidate"))
        self.assertEqual(captured["schema"], json.loads(
            (cmt.PROMPTS / "cmt_judge_schema.json").read_text()))
        self.assertEqual(constructor.call_args.kwargs["system_prompt"],
                         (cmt.PROMPTS / "cmt_judge_system.txt").read_text())
        self.assertEqual(constructor.call_args.kwargs["codex_bin"], "test-codex")
        self.assertTrue(constructor.call_args.kwargs["strict_no_tools"])
        self.assertTrue(result.correct)
        self.assertEqual(result.details["model_answer"], "2")

    def test_fable_judge_rejects_invalid_outputs_and_handles_refusal(self):
        client = MagicMock()
        message = client.messages.stream.return_value.__enter__.return_value.get_final_message.return_value
        raw = {"model": "claude-fable-5", "stop_reason": "end_turn", "usage": {},
               "content": [{"type": "text", "text": json.dumps(JUDGMENT)}]}
        settings = JudgeSettings(model="claude-fable-5", fable_model="claude-fable-5")
        with patch.object(backends, "make_fable_client", return_value=client):
            pipeline = load_benchmark("cmt", judge_settings=settings)
            problem = pipeline.problems[0]
            message.model_dump.return_value = raw
            self.assertTrue(pipeline.evaluate(problem.id, "candidate").correct)
            for invalid in ({}, {**JUDGMENT, "strict": False}, {**JUDGMENT, "confidence": True}):
                message.model_dump.return_value = {
                    **raw, "content": [{"type": "text", "text": json.dumps(invalid)}]}
                with self.assertRaises(ValueError):
                    pipeline.evaluate(problem.id, "candidate")
            message.model_dump.return_value = {**raw, "stop_reason": "refusal"}
            with self.assertRaisesRegex(ValueError, "refused"):
                pipeline.evaluate(problem.id, "candidate")

    def test_evaluated_model_refusal_is_incorrect_without_judge_call(self):
        client = MagicMock()
        with patch.object(backends, "CodexLLM", return_value=client):
            judge = cmt.make_judge(_judge_args(JudgeSettings()))
            result = judge({"question": "Q"}, {"response": "", "refused": True}, "2")
        self.assertEqual(result["correct"], "no")
        client.complete.assert_not_called()

    def test_checkpoint_rejects_changed_judge_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            args = parser().parse_args([
                "run", "--dataset", "cmt", "--output", directory, "--stage", "prepare",
                "--model", "gpt-5.6-sol", "--judge-model", "claude-fable-5"])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run(args), 0)
                args.judge_max_output_tokens += 1
                with self.assertRaisesRegex(ValueError, "Inputs/configuration changed"):
                    run(args)


if __name__ == "__main__":
    unittest.main()
