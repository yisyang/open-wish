# Workflow skill evaluations

`evals.json` is the semantic regression set for the schema-3 workflow. Run each
prompt in a fresh session with the listed skills and project policy. Compare with
a snapshot of previous skills when assessing a revision.

| Scenario | Behaviors to check |
| --- | --- |
| Existing monthly trends versus conflicting upload request | Preserve current intent; clarify the actual choice; avoid duplicate needs |
| Final fast-forward results | Review/close/clean the change; retain needs; scope delegation; preserve evidence provenance |
| Independent work around manual observation | Continue ready tasks; retain manual checks and completed task evidence |
| Routine alias | Implement and verify directly without records or acceptance ceremony |
| Working design repair | Revise the disposable approach/tasks; use code/tests/layout; reuse existing authority |
| New format versus accountability | Distinguish mechanism from independently valuable outcome |
| Plan-only | Prepare change and local tasks, then stop before implementation |
| Explicit opt-out | Source templates do not impose self-adoption |
| Fast-forward routine work | Finish after verification/reporting without structured records |
| Disposal with unique knowledge and active blockers | Preserve useful facts in repo docs; retain unfinished work; handle unknown files deliberately |
| Default result review | Retain change/tasks until actual human acceptance |

Grade actual responses rather than claims of compliance. A real decision uses
numbered A/B/C choices with `(Recommended)` before preferred text; routine work
needs no question. Prefer concise need → outcome → evidence communication.

These are instruction-following dry runs, not product execution or proof of
reliability across harnesses. Keep outputs and comparative scores in a temporary
workspace rather than this source checkout. Do not reuse scores from earlier
versions of the prompts. Human feedback can be supplied directly in chat or via
the skill-creator review viewer; a submission is received only when its data is available.
