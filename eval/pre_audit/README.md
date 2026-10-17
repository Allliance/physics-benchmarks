# Pre-audit evaluation

This package evaluates the frozen original question sets in `../data/pre_audit/`.
PHYBench, PRISM and UGPhysics use pinned upstream graders; HLE uses its upstream
judge prompt/schema. CMT and CritPt contracts are self-contained in `cmt.py`,
`critpt.py` and `prompts/`. No preparation scripts or response exports are needed.

```bash
python -m eval pre-audit run --dataset all --model claude-fable-5 \
  --judge-model gpt-5.6-sol --attempts 4 --output outputs/pre --dry-run
```

Run from the repository root. Remove `--dry-run` to run; use `--max-pending 1`
for a smoke run. Identical commands resume. Inputs never expose reference
answers to the evaluated model. Generation and judging use no tools.

The local CritPt route grades 54 of the 70 archived challenges with independently
established references; 16 missing references are excluded. This is distinct
from the paper's externally reported Artificial Analysis `mean@5` on 70 challenges.
See [the root README](../../README.md) for counts, results and protocol scope,
and [evaluation usage](../README.md) for stages, outputs and external responses.
