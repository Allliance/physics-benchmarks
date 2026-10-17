"""Direct, no-tool OpenAI Responses API transport for generation and judging."""

import base64
import os
import re
from pathlib import Path


def backend_metadata():
    return {
        'backend': 'openai-api', 'wire_api': 'responses',
        'base_url': os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/'),
        'max_output_tokens_enforced': True,
    }


def generate(prompt, *, model, system_prompt, reasoning_effort,
             max_output_tokens, timeout, image=None, output_schema=None):
    from openai import OpenAI

    if not os.environ.get('OPENAI_API_KEY'):
        raise ValueError('Set OPENAI_API_KEY for --openai-backend api.')
    content = [{'type': 'input_text', 'text': prompt}]
    if image:
        if not image.startswith('data:'):
            from utils.fable_backend import image_block

            source = image_block(Path(image))['source']
            image = f"data:{source['media_type']};base64,{source['data']}"
        else:
            base64.b64decode(image.split(',', 1)[1], validate=True)
        content.insert(0, {'type': 'input_image', 'image_url': image})
    payload = {
        'model': model, 'instructions': system_prompt,
        'input': [{'role': 'user', 'content': content}],
        'reasoning': {'effort': reasoning_effort},
        'max_output_tokens': max_output_tokens, 'store': False, 'tools': [],
    }
    if output_schema is not None:
        payload['text'] = {'format': {
            'type': 'json_schema', 'name': 'response',
            'strict': True, 'schema': output_schema,
        }}
    # Checkpoint retries are explicit. An SDK retry could repeat a paid attempt.
    with OpenAI(timeout=timeout, max_retries=0) as client:
        response = client.responses.create(**payload)
    raw = response.model_dump(mode='json')
    actual = raw.get('model')
    if actual != model and not re.fullmatch(re.escape(model) + r'-\d{4}-\d{2}-\d{2}', actual or ''):
        raise ValueError(f'OpenAI model mismatch: requested {model!r}, received {actual!r}')
    if raw.get('status') != 'completed':
        raise ValueError(f"OpenAI response did not complete: status={raw.get('status')!r}, "
                         f"details={raw.get('incomplete_details') or raw.get('error')!r}")
    text, refusals = [], []
    for item in raw.get('output', []):
        if item.get('type') == 'reasoning':
            continue
        if item.get('type') != 'message' or item.get('role') != 'assistant':
            raise ValueError(f"Unexpected output in no-tool OpenAI response: {item.get('type')!r}")
        if item.get('status') != 'completed':
            raise ValueError('OpenAI assistant message did not complete')
        for block in item.get('content', []):
            if block.get('type') == 'output_text':
                text.append(block['text'])
            elif block.get('type') == 'refusal':
                refusals.append(block['refusal'])
            else:
                raise ValueError(f"Unexpected OpenAI content: {block.get('type')!r}")
    answer = '\n'.join(text).strip()
    if refusals:
        answer = '\n'.join(refusals).strip() or 'The model refused this request.'
    if not answer:
        raise ValueError('OpenAI returned no final answer')
    return {
        'response': answer, 'refused': bool(refusals), 'usage': raw.get('usage'),
        'requested_model': model, 'actual_model': raw.get('model'),
        'response_id': raw.get('id'), 'raw_response': raw,
        'attempts': 1, 'tool_events': [],
    }
