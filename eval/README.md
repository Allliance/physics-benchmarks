# Evaluation

Run from the repository root after installing `requirements-lock.txt` and initializing
its four benchmark submodules. [The root README](../README.md) contains the
quick start, paper figures and results, dataset statistics and protocol differences.

```bash
python -m eval pre-audit run --dataset all --model claude-fable-5 \
  --judge-model gpt-5.6-sol --attempts 4 --output outputs/pre --dry-run
python -m eval post-audit --dataset all --model claude-fable-5 \
  --judge-model gpt-5.6-sol --attempts 4 --output outputs/post --dry-run
```

Remove `--dry-run` to generate answers and score them. Add `--max-pending 1` for a
bounded smoke run, then rerun without that limit to finish. Generation and
judging are no-tool. Select a different model for the judge.

## Inputs and graders

All built-in inputs are frozen in `data/`; `data/manifest.json` records their
counts and exclusions. `datasets.py` and `pre_audit/pipeline.py`
load these snapshots without reading audit response exports or preparation code.

CritPt's corrected snapshot has 54 questions; unrepairable questions `41` and
`46` are excluded. The pre-audit snapshot has 54 gradeable questions.

| Benchmark | Pre-audit evaluator | Post-audit evaluator |
|---|---|---|
| PHYBench | Released EED; correct iff EED = 100 | Unified HLE-adapted judge |
| PRISM | Released final-answer DAG grader | Unified HLE-adapted judge |
| UGPhysics | Released rule grader plus auxiliary LLM judge | Unified HLE-adapted judge |
| HLE-Physics | Released HLE judge prompt/schema | Unified HLE-adapted judge |
| CMT | Preserved CMT HLE-adapted judge | Unified HLE-adapted judge |
| CritPt | Preserved local CritPt HLE-adapted judge | Unified HLE-adapted judge |

The adapters in `pre_audit/native.py` isolate upstream imports, retain presentation
normalization and bound scoring processes. Grader commits and run settings are recorded in run manifests. Upstream checkouts remain
unmodified. CMT and CritPt judging have no analysis-folder dependency.

## Options and outputs

- `--dataset NAME|all`: `phybench`, `prism`, `ugphysics`, `hle-physics` (alias `hle`), `cmt`, `critpt`.
- `--attempts N`: independent attempts, default 1; use 4 for `mean@4`/`pass@4`.
- `--stage prepare|generate|score|summary|all` for pre-audit; use `judge` instead of `score` for post-audit.
- `--workers`, `--score-workers` (pre-audit), `--timeout`, `--grade-timeout` (pre-audit) and token limits control execution.
- `--max-pending N` bounds work in each stage and attempt; `--dry-run` validates without writes or calls.
- `--openai-backend codex|api` selects the GPT generation and judge transport;
  `--judge-openai-backend codex|api` overrides only the judge. API mode requires
  `OPENAI_API_KEY` and optionally uses `OPENAI_BASE_URL` for a Responses gateway.
- `--model openai-compatible` selects an arbitrary Chat Completions server via
  `OPENAI_COMPAT_BASE_URL`, `OPENAI_COMPAT_MODEL` and optionally `OPENAI_COMPAT_API_KEY`.

Each attempt writes a manifest, dataset, predictions, scores/judgments, errors
and summary under `BENCHMARK/attempt-N/`. Batch `summary.json` reports `mean@N`
and `pass@N` only when all required judgments are present. A single-attempt,
single-benchmark post-audit run writes directly into its output directory.
Rerun the same command to resume; changed data or settings require
a new output directory. Model refusals are incorrect outcomes; failed calls
remain pending. Generated outputs are ignored by Git.
Partial smoke runs return status `2`; a null accuracy preserves the full dataset
denominator. Direct API transports enforce token limits. Codex does not enforce
the CLI token-limit settings; this is recorded in backend metadata.
Backend settings, evaluation code/prompt hashes, and pre-audit native input hashes
prevent resuming across incompatible configurations.

Post-audit accepts `--data PATH` for custom JSON/JSONL rows containing `id`,
`question` and `reference_answer`; Parquet also works with the optional `pyarrow`
package. `--data` cannot be combined with `--dataset all`. Local images or data
URLs can be supplied with `image` for supported backends.

Pre-audit can export questions and score externally generated responses:

```bash
mkdir -p outputs
python -m eval pre-audit export --dataset prism --without-references --output outputs/questions.jsonl
python -m eval pre-audit evaluate --dataset prism \
  --responses outputs/responses.jsonl --output outputs/scores.jsonl --require-all
```

Input response records contain `id` and `response`. PHYBench requires a response
string containing a JSON object with only `final_answer`; other routes use raw
answer text. References and audit labels are excluded from generation inputs.

## Serving providers

### Direct OpenAI API

Set `OPENAI_API_KEY` in the environment and use `--openai-backend api` for both
GPT generation and GPT judging. No Codex installation is needed in this mode.
`OPENAI_BASE_URL` optionally selects a Responses-compatible gateway; the default
is `https://api.openai.com/v1`.

```bash
python -m eval post-audit --dataset cmt --model gpt-5.6-sol \
  --judge-model gpt-6-astra --openai-backend api \
  --max-pending 1 --workers 1 --output ../physics-evaluations/openai-smoke
```

`--judge-openai-backend` overrides only the GPT judge transport, allowing Codex
generation with API judging or the reverse. For external pre-audit answers,
`pre-audit evaluate` accepts `--judge-openai-backend api`.

Direct OpenAI API responses retain the requested/returned model IDs and token
usage. Model substitutions, incomplete responses, and unexpected tool calls are
rejected. SDK retries are disabled; failed rows remain pending for an explicit
checkpoint resume. Model refusals are incorrect outcomes; judge refusals remain
pending.

### Codex, Anthropic, and Gemini

GPT models use an authenticated `codex` executable on `PATH` by default. Supply
`--codex-bin PATH` to choose another executable. Generation and judging disable
tools and web search. Codex does not enforce the output-token cap flags;
manifests record `max_output_tokens_enforced: false` for this transport.

Fable uses `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` (with `CLAUDE_API_KEY`
also accepted). `--fable-model` selects an endpoint-specific model ID, and
`ANTHROPIC_BASE_URL` optionally selects a custom endpoint. Fable uses adaptive
thinking with the selected effort. Gemini needs `GOOGLE_API_KEY` or
`GEMINI_API_KEY`.

### OpenAI-compatible Chat Completions servers

```bash
export OPENAI_COMPAT_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_COMPAT_MODEL=your-served-model-id
# Export OPENAI_COMPAT_API_KEY if the server requires authentication.
python -m eval post-audit --dataset cmt --model openai-compatible \
  --judge-model gpt-5.6-sol --judge-openai-backend api \
  --max-pending 1 --workers 1 --output ../physics-evaluations/compatible-smoke
```

The server must accept `reasoning_effort` and `max_tokens`, plus JSON-schema
output for pre-audit PHYBench. OpenRouter uses its `reasoning` field and accepts
`OPENROUTER_API_KEY`. The served model ID must differ from the judge model.
Truncated outputs remain pending, including when partial text is present.

## Paper comparison settings

The defaults are High reasoning effort, 32,768 generation output tokens, 8,192
judge output tokens, and one attempt. Set `--attempts 4` for `mean@4`/`pass@4`.
For the paper's Sol/Fable CritPt generation setting, select `--reasoning-effort max`.
The included runners remain no-tool; they do not implement all tool-assisted
paper experiments.

## Validation

```bash
python -m unittest discover -s eval/tests -p 'test_*.py'
python -m unittest utils.test_gemini_backend
```
