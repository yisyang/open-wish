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
| Brownfield shop-a | Discover architectural friction from source; propose incremental refactoring and seek approval |
| Brownfield shop-b | Recognize useful existing boundaries and recommend retaining them |
| Greenfield reconciliation, then CSV | Implement real code; retain and rerun small, meaningful checks of stable outcomes and consequential risks |
| Need sizing, relationships, and retention | Reuse/split/merge intent carefully; preserve sparse semantic facts and useful knowledge |
| Strategic test selection | Reuse stable checks, protect against consequential data loss, avoid brittle incidental assertions and unrequested targets |
| Explicit coverage contract | Honor scoped human coverage requirements without equating them with correctness |
| Large modernization | Detect subsystem-sized tasks; scope independently reviewable increments and detail the next executable work |
| Growing scope and stale blockers | Preserve obligations/evidence, reconcile resolved decisions, repair dependencies, and keep future plans usable after disposal |
| Narrow change with many needs | Retain a coherent cross-cutting increment; distinguish partial contribution, future work, and actual result acceptance |

Grade actual responses rather than claims of compliance. A real decision uses
numbered A/B/C choices with `(Recommended)` before preferred text; routine work
needs no question. Prefer concise need → outcome → evidence communication.

The original cases are instruction-following dry runs. Cases 13–14 inspect real
small repositories under `fixtures/`, without being told the architectural finding.
Case 15 builds an actual product in a temporary project and evolves it for a second
ask. Run its independent checks with:

```sh
PROJECT_DIR=/path/to/run/outputs/project python3 evals/fixtures/reconcile/acceptance_test.py -v
```

Inspect the generated source as well as test results: behavioral passes alone do
not establish discoverability, isolated effects, or proportionate architecture.
For case 15, independently run the retained suite using its documented command and
record the result and runtime in the temporary evaluation workspace. Inspect what
the tests protect: stable outcomes, important decisions, and consequential boundary
contracts. No fixed test-count target applies; justify complexity by useful evidence,
not coverage volume. Exact schema checks may be valuable while exact incidental
diagnostics or layout snapshots are brittle. Judge current runnable artifacts and
reported limitations, not unobservable historical first-slice execution order.
Historical sequencing would require separately captured harness checkpoints; it is
not established by retrospective prose or required in the product's retained files.
Case 16 assesses semantic consolidation and relationship reuse. Assertions support
human judgment; none of these small samples prove reliability across harnesses.
Cases 19–21 exercise delivery planning at different scales. Case 19 uses a supplied
modernization assessment, not a runnable game; grade attribution accordingly. Inspect
the proposed acceptance boundaries, early integration and concrete next tasks rather
than rewarding change/file counts. Case 20 checks scope growth and contradictory
decision/task state, including preservation of genuine manual blockers and delegation
boundaries. Case 21 is a control against unnecessary splitting or claims that an empty
future task list establishes completion. Compare old and revised guidance on identical
prompts in fresh sessions; report improvements and non-discriminating cases honestly.
Fixtures are evaluation inputs, not OW's product implementation. Always run/copy
them in temporary projects; never install an OW workflow into this source checkout.

Keep outputs and comparative scores in a temporary
workspace rather than this source checkout. Do not reuse scores from earlier
versions of the prompts. Human feedback can be supplied directly in chat or via
the skill-creator review viewer; a submission is received only when its data is available.
