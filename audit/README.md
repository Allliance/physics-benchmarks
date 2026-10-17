# Expert audit records

These files document audit labels and corrections. Evaluation commands read the
original and corrected question/reference datasets in `../eval/data/`.

| File | Purpose |
|---|---|
| `audits.csv` | 250 final audits for PHYBench, PRISM, UGPhysics and HLE-Physics |
| `dataset_ids.json` | Question IDs for all six datasets, plus audited IDs for the first four |
| `cmt.json` | CMT issue labels, correction status and review notes for all 50 questions |
| `critpt/reviewer_notes.json` | 59 reviewer form submissions for the 56 reviewed CritPt challenges |
| `critpt/adjudications.json` | Final problem/model attributions and rationales for the 56 reviewed CritPt challenges |
| `critpt/verdicts.json` | Correct, repairable, unrepairable and not-reviewed CritPt challenge IDs |
| [`critpt/`](critpt/README.md) | Expert solutions and final answers for the reviewed CritPt challenges |

`audits.csv` has one record per audited question:

| Column | Meaning |
|---|---|
| `source_problem_id` | Question ID in the original benchmark |
| `dataset` | Benchmark |
| `category` | Subject area |
| `pass` | Review pass (`1` or `2`) whose label and note were kept |
| `label` | `PROBLEM_FAILURE`, `GRADER_FAILURE` or `MODEL_FAILURE` |
| `note` | Reviewer note; may be empty |

`PROBLEM_FAILURE`, `GRADER_FAILURE` and `MODEL_FAILURE` mean benchmark, grader
and model errors. Benchmark errors take precedence in attribution.

`dataset_ids.json` contains:

- `all_ids`: the selected questions for the first four benchmarks, all 50 CMT
  questions, and the 56 reviewed CritPt challenges.
- `audited_ids`: for the first four benchmarks only, the questions rejected by
  the original grader in the audit-collection run and sent for expert audit;
  these IDs match `audits.csv`.

CMT and CritPt were reviewed in full rather than through this rejection-based
selection.

| Benchmark | Audited | Benchmark errors | Grader errors | Model errors |
|---|---:|---:|---:|---:|
| PHYBench | 56 | 13 | 40 | 3 |
| PRISM | 74 | 26 | 48 | 0 |
| UGPhysics | 22 | 18 | 3 | 1 |
| HLE-Physics | 98 | 86 | 4 | 8 |
| CMT | 50 | 30 | — | 2 |
| CritPt | 56 | 21 | — | 5 |

Grader-error counts are unavailable for CMT and CritPt, not zero. In the first
four audit sets, 196 questions had two reviews and 54 had one; of the 196 label
pairs, 140 initially agreed and 56 disagreed.

CMT repairs 29 benchmark errors and excludes index `14`. CMT's `audit_status` is
`red` for benchmark errors and `green` otherwise; `correction_state` is
`corrected` for repaired rows, `unchanged` for rows without a benchmark error,
and `original_retained` for the excluded index `14`.

CritPt identifies 21 benchmark errors, repairs 19, and excludes the unrepairable
`41` and `46`, matching Table 3 and Appendix B.2.3 of the paper. Its five model
errors are `06`, `16`, `18`, `58`, and `60`.

`critpt/adjudications.json` preserves the final expert decisions and their
rationales. `critpt/verdicts.json` groups these decisions across challenges
`01`–`70`: `correct_problems` means no benchmark error under the final
adjudication, including manageable issues; it does not imply an unchanged
statement or a correct model response. `repairable_problems` and
`unrepairable_problems` are benchmark errors, and `not_reviewed_problems` lists
the rest. See [the CritPt notes](critpt/README.md) for the distinction between
statement revisions and error attribution. Reviewer form submissions are
numbered within each challenge; reviewer identities are omitted.
