# CritPt expert solutions

Expert solutions and final answers for the 56 reviewed CritPt challenges:
47 full solutions and 54 final answers. Unrepairable challenges have no
solution or final answer. Files are LaTeX sources; some are complete documents
and others are fragments. Figures and bibliography files used by solutions 56
and 57 are included.

The evaluator uses `reference_answer` in
[the corrected dataset](../../eval/data/post_audit/critpt.jsonl).

## Audit attribution and statement revisions

The paper's 56 reviewed challenges contain 21 benchmark errors: 19 repaired
challenges and two excluded challenges (`41` and `46`). Five other challenges
have model errors: `06`, `16`, `18`, `58`, and `60`.
[Final adjudications](adjudications.json) record the problem/model decisions and
their rationales; [verdicts](verdicts.json) group the problem decisions by ID.

Problem attribution and statement revision are separate records. Under the final
adjudication policy, a manageable issue can be assigned no benchmark error even
when the expert edits the statement. The `correct_problems` group therefore
does not mean that the released statement is identical to the original or that
the model answered correctly. The original and corrected snapshots preserve
both versions. Of the 32 retained statements that differ, 19 are assigned
repairable benchmark errors and 13 are assigned no benchmark error.

| Challenge | Final attribution | Adjudication rationale |
|---|---|---|
| 06 | Model error | The numerical-constant typo is recoverable; the model's result is incorrect under the expert's accepted correction. |
| 16 | Model error | The printed momentum-diagonal Hamiltonian is valid; the model instead solves an on-site real-space Hubbard model. |
| 17 | No benchmark or model error | The model identifies the missing entropy minus sign; the final adjudication treats it as a manageable issue. |
| 45 | No benchmark or model error | Equal relaxation times were already specified; the additional transport-regime clarification was accepted as manageable. |
| 51 | No benchmark or model error | The reviewer accepted the original solution and treated the statement changes as small clarifications. The released version explicitly allows a non-elementary answer. |

The reviewer submissions remain in [reviewer_notes.json](reviewer_notes.json).
Final attribution follows the adjudications rather than inferring a label from
whether the expert edited a statement.

## Expert solution index

| Challenge | Full solution | Final answer |
|---|---|---|
| 01 | [solution.tex](solutions/01/solution.tex) | [final_answer.tex](solutions/01/final_answer.tex) |
| 02 | [solution.tex](solutions/02/solution.tex) | [final_answer.tex](solutions/02/final_answer.tex) |
| 03 | [solution.tex](solutions/03/solution.tex) | [final_answer.tex](solutions/03/final_answer.tex) |
| 04 | [solution.tex](solutions/04/solution.tex) | [final_answer.tex](solutions/04/final_answer.tex) |
| 05 | [solution.tex](solutions/05/solution.tex) | [final_answer.tex](solutions/05/final_answer.tex) |
| 06 | [solution.tex](solutions/06/solution.tex) | [final_answer.tex](solutions/06/final_answer.tex) |
| 07 | [solution.tex](solutions/07/solution.tex) | [final_answer.tex](solutions/07/final_answer.tex) |
| 08 | [solution.tex](solutions/08/solution.tex) | [final_answer.tex](solutions/08/final_answer.tex) |
| 09 | — | [final_answer.tex](solutions/09/final_answer.tex) |
| 10 | [solution.tex](solutions/10/solution.tex) | [final_answer.tex](solutions/10/final_answer.tex) |
| 12 | [solution.tex](solutions/12/solution.tex) | [final_answer.tex](solutions/12/final_answer.tex) |
| 13 | [solution.tex](solutions/13/solution.tex) | [final_answer.tex](solutions/13/final_answer.tex) |
| 14 | — | [final_answer.tex](solutions/14/final_answer.tex) |
| 16 | [solution.tex](solutions/16/solution.tex) | [final_answer.tex](solutions/16/final_answer.tex) |
| 17 | [solution.tex](solutions/17/solution.tex) | [final_answer.tex](solutions/17/final_answer.tex) |
| 18 | [solution.tex](solutions/18/solution.tex) | [final_answer.tex](solutions/18/final_answer.tex) |
| 19 | [solution.tex](solutions/19/solution.tex) | [final_answer.tex](solutions/19/final_answer.tex) |
| 20 | [solution.tex](solutions/20/solution.tex) | [final_answer.tex](solutions/20/final_answer.tex) |
| 22 | [solution.tex](solutions/22/solution.tex) | [final_answer.tex](solutions/22/final_answer.tex) |
| 23 | [solution.tex](solutions/23/solution.tex) | [final_answer.tex](solutions/23/final_answer.tex) |
| 26 | — | [final_answer.tex](solutions/26/final_answer.tex) |
| 28 | [solution.tex](solutions/28/solution.tex) | [final_answer.tex](solutions/28/final_answer.tex) |
| 29 | [solution.tex](solutions/29/solution.tex) | [final_answer.tex](solutions/29/final_answer.tex) |
| 30 | [solution.tex](solutions/30/solution.tex) | [final_answer.tex](solutions/30/final_answer.tex) |
| 31 | [solution.tex](solutions/31/solution.tex) | [final_answer.tex](solutions/31/final_answer.tex) |
| 32 | — | [final_answer.tex](solutions/32/final_answer.tex) |
| 33 | [solution.tex](solutions/33/solution.tex) | [final_answer.tex](solutions/33/final_answer.tex) |
| 35 | [solution.tex](solutions/35/solution.tex) | [final_answer.tex](solutions/35/final_answer.tex) |
| 39 | [solution.tex](solutions/39/solution.tex) | [final_answer.tex](solutions/39/final_answer.tex) |
| 40 | [solution.tex](solutions/40/solution.tex) | [final_answer.tex](solutions/40/final_answer.tex) |
| 41 | — | — |
| 42 | [solution.tex](solutions/42/solution.tex) | [final_answer.tex](solutions/42/final_answer.tex) |
| 44 | [solution.tex](solutions/44/solution.tex) | [final_answer.tex](solutions/44/final_answer.tex) |
| 45 | [solution.tex](solutions/45/solution.tex) | [final_answer.tex](solutions/45/final_answer.tex) |
| 46 | — | — |
| 47 | [solution.tex](solutions/47/solution.tex) | [final_answer.tex](solutions/47/final_answer.tex) |
| 48 | [solution.tex](solutions/48/solution.tex) | [final_answer.tex](solutions/48/final_answer.tex) |
| 49 | [solution.tex](solutions/49/solution.tex) | [final_answer.tex](solutions/49/final_answer.tex) |
| 50 | — | [final_answer.tex](solutions/50/final_answer.tex) |
| 51 | [solution.tex](solutions/51/solution.tex) | [final_answer.tex](solutions/51/final_answer.tex) |
| 53 | [solution.tex](solutions/53/solution.tex) | [final_answer.tex](solutions/53/final_answer.tex) |
| 55 | — | [final_answer.tex](solutions/55/final_answer.tex) |
| 56 | [solution.tex](solutions/56/solution.tex) | [final_answer.tex](solutions/56/final_answer.tex) |
| 57 | [solution.tex](solutions/57/solution.tex) | [final_answer.tex](solutions/57/final_answer.tex) |
| 58 | [solution.tex](solutions/58/solution.tex) | [final_answer.tex](solutions/58/final_answer.tex) |
| 59 | [solution.tex](solutions/59/solution.tex) | [final_answer.tex](solutions/59/final_answer.tex) |
| 60 | [solution.tex](solutions/60/solution.tex) | [final_answer.tex](solutions/60/final_answer.tex) |
| 61 | [solution.tex](solutions/61/solution.tex) | [final_answer.tex](solutions/61/final_answer.tex) |
| 62 | [solution.tex](solutions/62/solution.tex) | [final_answer.tex](solutions/62/final_answer.tex) |
| 64 | [solution.tex](solutions/64/solution.tex) | [final_answer.tex](solutions/64/final_answer.tex) |
| 65 | — | [final_answer.tex](solutions/65/final_answer.tex) |
| 66 | [solution.tex](solutions/66/solution.tex) | [final_answer.tex](solutions/66/final_answer.tex) |
| 67 | [solution.tex](solutions/67/solution.tex) | [final_answer.tex](solutions/67/final_answer.tex) |
| 68 | [solution.tex](solutions/68/solution.tex) | [final_answer.tex](solutions/68/final_answer.tex) |
| 69 | [solution.tex](solutions/69/solution.tex) | [final_answer.tex](solutions/69/final_answer.tex) |
| 70 | [solution.tex](solutions/70/solution.tex) | [final_answer.tex](solutions/70/final_answer.tex) |
