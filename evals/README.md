# Workflow skill evaluations

`evals.json` is the current semantic regression set for the need-first workflow.
Run each prompt in a fresh session with the listed skills and project policy;
compare with a snapshot of the previous skills when assessing a revision.

| Scenario | Behaviors to check |
| --- | --- |
| Already-satisfied monthly trends versus a conflicting upload request | Preserve current intent; avoid duplicate needs and request records; use numbered A/B/C clarification choices; discuss only the current decision |
| Final fast-forward review | Operate on need IDs; skip final confirmation; explain the spec and its user outcomes; preserve evidence provenance |
| Independent work waiting on a manual observation | Continue ready tasks; hand off with need/spec context and lettered choices; retain unfinished verification honestly |

Grade the actual human-facing response, not the agent's claim that it followed
the policy. The preferred option must start with `(Recommended)` after its
letter, and a Propose confirmation must not advertise future approval gates.

These are instruction-following dry runs, not live product execution or proof
of reliability across harnesses. Keep direct response evidence in the temporary
evaluation workspace; avoid accumulating review histories in the product's OW
knowledge tree. Do not reuse the v0.1 evaluation scores for this revised prompt set.

Human feedback can be supplied directly in chat. A browser review submission is
not received until its actual feedback data is available to the agent.
