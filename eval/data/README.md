# Frozen evaluation datasets

These JSONL snapshots are the only built-in runtime data source. `manifest.json`
records evaluation scope, exclusions and historical source
lineage. Source paths refer to the original preparation workspace; they are
provenance, not required files in this release.

| Benchmark | Pre-audit archived | Pre-audit gradeable | Post-audit |
|---|---:|---:|---:|
| PHYBench | 100 | 100 | 87 |
| PRISM | 100 | 100 | 74 |
| UGPhysics | 100 | 100 | 82 |
| HLE-Physics | 202 | 202 | 116 |
| CMT | 50 | 50 | 49 |
| CritPt | 70 | 54 | 54 |

Pre-audit rows preserve original questions, generation prompts, available
references and native scorer fields. Post-audit rows contain `id`, `question`,
`reference_answer` and `category`, with exclusions and repairs already applied.
These files contain evaluation inputs, not model generations.

For PHYBench, PRISM, UGPhysics and HLE, benchmark-error rows are excluded.
CMT retains 49 validated/repaired rows and excludes index `14`. CritPt retains
54 rows from the 56 audited challenges, excluding the unrepairable `41` and `46`.
In the CritPt pre-audit snapshot, the 16 challenges without an expert reference
are recorded as `MISSING_REFERENCE`; available references are expert-established,
not official CritPt references. The paper's CritPt pre-audit score uses
Artificial Analysis `mean@5` on 70 challenges, a separate scope from this local
route.

Keep these snapshots immutable. Intentional revisions require corresponding
manifest counts/exclusions and validation with `eval/tests/test_data_snapshots.py`.
