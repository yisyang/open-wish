# Workflow skill evaluations

`evals.json` is the current semantic regression set for the need-first workflow.
Run each prompt in a fresh session with the listed skills and project policy;
compare with a snapshot of the previous skills when assessing a revision.

| Scenario | Behaviors to check |
| --- | --- |
| Already-satisfied monthly trends versus a conflicting upload request | Preserve current intent; avoid duplicate needs and request records; use numbered A/B/C clarification choices; discuss only the current decision |
| Final fast-forward review | Operate on need IDs; skip final confirmation; explain the spec and its user outcomes; preserve evidence provenance |
| Independent work waiting on a manual observation | Continue ready tasks; hand off with need/spec context and lettered choices; retain unfinished verification honestly |
| Routine command alias under a shared spec | No gates, new needs, reopen cycle, epics, spec split, or final acceptance prompt |
| Technical repair of a shared-spec execution scope | Narrow the epic's execution needs; preserve regression coverage; reuse existing authority |
| New export format versus auditor accountability | Reuse the existing outcome for a mechanism; recognize a genuinely independent outcome |
| Explicit plan-only request | Prepare without stage prompts; stop before authorization/implementation |
| Explicit OW opt-out in the OW source tree | Work directly; product assets do not self-activate the workflow |
| Explicit fast-forward for a routine alias | Finish after direct verification/reporting; do not fall through into structured lifecycle steps |

Grade the actual human-facing response, not the agent's claim that it followed
the policy. The preferred option must start with `(Recommended)` after its
letter when a real question is needed. A routine change must not prompt at all;
structured preparation must not manufacture per-stage confirmation questions.

These are instruction-following dry runs, not live product execution or proof
of reliability across harnesses. Keep direct response evidence in the temporary
evaluation workspace rather than this source checkout. Do not reuse older
evaluation scores for this revised prompt set.

Human feedback can be supplied directly in chat. A browser review submission is
not received until its actual feedback data is available to the agent.
