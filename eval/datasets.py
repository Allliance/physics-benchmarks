"""Load the immutable dataset snapshots shipped with :mod:`eval`."""

import base64
import json
from pathlib import Path

from .storage import read_rows

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(__file__).parent / 'data'
MANIFEST = DATA_ROOT / 'manifest.json'
ALIASES = {'hle': 'hle-physics', 'prism-physics': 'prism'}
AUDITED = {'phybench', 'prism', 'ugphysics', 'hle-physics'}


def normalize(row, base):
    """Accept audit exports, CMT, CritPt, HLE, UGPhysics, PHYBench, or generic rows."""
    if 'problem_id' in row:
        qid, question, answer = row['problem_id'], row['problem_statement'], row['reference_solution']
    elif 'challenge_id' in row:
        raw = row['challenge_id']
        if isinstance(raw, bool) or not str(raw).isdigit() or not 1 <= int(raw) <= 70:
            raise ValueError(f'Invalid CritPt challenge ID: {raw!r}')
        qid, question, answer = f'{int(raw):02d}', row['problem'], row['ground_truth']
    elif 'prompt' in row and 'index' in row:
        if type(row['index']) is not int or row['index'] < 0:
            raise ValueError('CMT index must be a nonnegative integer')
        qid, question, answer = row['index'], row['prompt'], row['solution']
    elif '_eval_id' in row and 'problem' in row:
        qid, question = row['_eval_id'], row['problem']
        answer = f"{row['solution']}\n\nReference answer:\n{row['answers']}"
    elif 'content' in row and 'id' in row:
        qid, question, answer = row['id'], row['content'], row.get('solution') or row.get('answer')
    else:
        qid, question = row['id'], row['question']
        answer = row.get('reference_answer', row.get('answer'))
    if isinstance(qid, bool) or not isinstance(qid, (str, int)) or not str(qid).strip():
        raise ValueError('Every question needs a nonempty string/integer ID')
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f'{qid}: missing question')
    # Null CritPt references are explicitly unavailable; literal "undefined" is valid.
    if answer is not None and (not isinstance(answer, str) or not answer.strip()):
        raise ValueError(f'{qid}: reference must be a nonempty string or null')
    result = {'id': str(qid), 'question': question, 'reference_answer': answer,
              'category': row.get('category', row.get('type', row.get('subject', '')))}
    image = row.get('image')
    if image:
        if not isinstance(image, str):
            raise ValueError(f'{qid}: image must be a local path or data URL')
        if image.startswith('data:'):
            base64.b64decode(image.split(',', 1)[1], validate=True)
        else:
            if image.startswith(('http://', 'https://')):
                raise ValueError('Image must be a local path or data URL')
            image = str((base / image).resolve())
            if not Path(image).is_file():
                raise FileNotFoundError(image)
        result['image'] = image
    return result


def load_dataset(dataset, *, data=None, split='post-audit'):
    """Load a normalized pre- or post-audit snapshot.

    Built-in datasets never reach into other repository directories; the
    reviewed selection is already frozen in ``eval/data``.
    """
    dataset = ALIASES.get(dataset.lower(), dataset.lower())
    if split not in {'pre-audit', 'post-audit'}:
        raise ValueError("split must be 'pre-audit' or 'post-audit'")
    manifest = None
    if data is not None:
        source = Path(data).resolve()
    elif dataset in {*AUDITED, 'cmt', 'critpt'}:
        manifest = json.loads(MANIFEST.read_text())['benchmarks'][dataset][split.replace('-', '_')]
        source = DATA_ROOT / manifest['file']
    else:
        raise ValueError('Unknown dataset; use --dataset NAME --data JSON/JSONL/PARQUET')
    rows = [normalize(row, source.parent) for row in read_rows(source)]
    ids = [row['id'] for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Dataset must contain unique question IDs and at least one row')
    excluded = list(manifest.get('excluded', [])) if manifest else []
    excluded_ids = {item['id'] for item in excluded}
    retained = []
    for row in rows:
        reason = 'MISSING_REFERENCE' if row['reference_answer'] is None else None
        if reason:
            if row['id'] not in excluded_ids:
                excluded.append({'id': row['id'], 'reason': reason})
                excluded_ids.add(row['id'])
        else:
            retained.append(row)
    if not retained:
        raise ValueError('No questions with available references remain')
    return retained, {
        'dataset': dataset, 'split': split, 'source': str(source),
        'source_count': manifest['source_count'] if manifest else len(ids), 'snapshot_ids': ids,
        'retained_count': len(retained), 'retained_ids': [row['id'] for row in retained],
        'excluded': excluded,
        'correction_policy': (
            'use the frozen reviewed/repaired snapshot' if manifest and split == 'post-audit'
            else 'use the frozen original-data snapshot' if manifest
            else 'use supplied dataset'
        ),
    }


def predictor_input(row):
    return {key: row[key] for key in ('id', 'question', 'image') if key in row}
