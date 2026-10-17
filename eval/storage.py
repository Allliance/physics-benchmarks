"""Dataset reading and atomic checkpoints."""

import json
import hashlib
from pathlib import Path
import tempfile


def source_fingerprint():
    """Invalidate checkpoints when the evaluation implementation or prompts change."""
    root = Path(__file__).resolve().parents[1]
    paths = [p for directory in ('eval', 'utils') for p in (root / directory).rglob('*')
             if p.is_file() and p.suffix in {'.py', '.txt', '.json'}
             and not any(part in {'tests', 'data', '__pycache__', 'artifacts'} for part in p.relative_to(root).parts)
             and not p.name.startswith('test_')]
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()


def read_rows(path):
    path = Path(path)
    if path.suffix == '.parquet':
        import pyarrow.parquet as pq
        rows = pq.read_table(path).to_pylist()
    elif path.suffix == '.json':
        rows = json.loads(path.read_text())
    else:
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f'{path}: expected a list of objects')
    return rows


def atomic_json(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write('\n')
            handle.flush()
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    temporary.replace(path)


def require_checkpoint(path, expected):
    if path.exists():
        if json.loads(path.read_text()) != expected:
            raise ValueError(f'Inputs/configuration changed: choose a new output directory ({path})')
    else:
        atomic_json(path, expected)
