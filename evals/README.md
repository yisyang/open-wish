# Workflow skill evaluations

`evals.json` is the semantic regression set for the shipped skills. Deterministic
tests in `tests/` protect the CLI; these scenarios check whether agents using the
skills behave well, and whether OW beats working without it.

## Running

`run.py` prepares an isolated workspace (always outside this checkout), runs an
agent command for every stage, and grades what it can mechanically:

```sh
python3 evals/run.py run --workspace /tmp/ow-evals --ids 15 23 24
python3 evals/run.py grade --workspace /tmp/ow-evals --ids 15 23 24
```

OW is meant to be judged against the most popular coding agents, each pinned to
its current flagship model at a reasoning level suited to planning. `--agent`
selects a preset, and OW is installed for its harness:

| Preset | Agent | Model | Reasoning |
| --- | --- | --- | --- |
| `codex` (default) | Codex CLI, `codex exec` | `gpt-6.1-sol` | `high` |
| `claude` | Claude Code, `claude -p` | `claude-opus-5-5` | `high` |

```sh
python3 evals/run.py run --workspace /tmp/ow-evals-claude --agent claude --ids 15 23 24
```

Presets run in an isolated agent home (`CODEX_HOME` or `CLAUDE_CONFIG_DIR` under
`WORKSPACE/agent-home/`) that links only your existing sign-in credentials, so your
global instructions, memories, plugins, MCP servers and settings cannot change the
results. Sign in to each agent once beforehand. A custom command is also accepted
(`--agent "COMMAND" --harness H`); it runs with your own configuration. Update the
presets when a newer flagship model ships, and do not compare scores across models.

- **Arms.** `skills` installs this checkout's skills into the working directory
  and puts an `ow` shim for this checkout on `PATH`. `baseline` runs the same task
  without OW; only evals with a `baseline_prompt` have this arm (15, 23, 24, 30).
- **Seeds.** An eval's `seed` (`fixtures/seeds/*`) materializes the state its prompt
  describes: `files/` is copied after `ow init` (baselines get everything except
  `openwish/`), then `setup.json` runs real `ow` commands, such as recording a passing
  review, so `ow context` agrees with the scenario. `tests/test_eval_seeds.py` keeps
  every seed valid. Unseeded dry runs tell the agent the described project is absent.
  Make sure no other `ow` is on `PATH` for baseline runs.
- **Stages.** Scenario evals (23, 24) run each stage as a separate agent process
  over the retained product, so a later session cannot remember the earlier
  prompt. The runner warns if the product gains Git history, which could leak
  deleted plans.
- **Records.** Each stage directory keeps `prompt.md`, `transcript.txt`,
  `metrics.json`, `ow-calls.log` (every `ow` invocation in the skills arm, counted as
  `ow_calls`) and a `snapshot/` of the work. Metrics hold wall time and exit
  code, plus token `usage` and `tool_calls` from Codex's JSONL events, or
  `usage`, `total_cost_usd` and `num_turns` from Claude's JSON result.
- **Agents.** The prompt is appended as the final argument, which fits
  `codex exec`, `claude -p` and `opencode run`. `{work}` and `{stage_dir}` in the
  command are replaced per stage; the agent must be able to write both (the
  response goes in the stage directory). Stdin is closed. A workspace records its
  agent in `agent.json` and refuses another, because arms and stages are reused.

`grade` writes `results.json` and prints one line per eval, arm and stage:

- **Acceptance.** External checks of the public contract for that stage
  (`fixtures/*/acceptance_test.py`). They receive `ARM`, `OW_CALLS` and `OW`, so a
  scenario can also check the workflow, as 30 does for direct versus managed delivery.
- **Own suite.** The product's retained tests, run as the product left them.
- **Mutation.** For 23 and 24, the retained tests are rerun with the target module
  replaced by an evaluator-only reference (`fixtures/*/reference.py`), then once per
  seeded mutant. Only tests that pass on the reference grade the mutants; the rest
  check choices the contract leaves open (input validation, extension APIs,
  internals) and are listed with their failures. A mutant is killed only when a test
  fails an assertion; errors and timeouts count as `errored`, not as protection.
  Read the compatible fraction alongside the kill count. Mutation is graded only when
  the product's own suite passes.
- **Intent.** Need count and size per stage, needs changed since the previous
  stage, and change directories left behind.
- **Dry-run evals** get a `grading.md` checklist of their assertions for a
  human or model grader. Grade actual responses and edits, not claims of
  compliance. Their prompts describe a project the agent cannot see; the
  coordinator header says so, so an empty working directory is not evidence
  against the described state.

## What to compare

Compare arms, and compare skill revisions, on identical prompts in fresh sessions.
Report non-discriminating cases honestly. Useful signals, in rough priority:

1. Acceptance and mutation results of the executable scenarios (15, 23, 24, 30),
   skills versus baseline.
2. Lost or invented rules across stages (read the stage responses and needs).
3. Cost: wall time and tokens per stage, skills versus baseline.
4. Checklist grades of the dry-run scenarios.

Small samples do not prove reliability across models or harnesses; run cases
whose guidance changed several times before claiming an improvement. Do not reuse
scores from earlier prompt versions. Keep workspaces, transcripts and scores out of
this checkout.

## Scenarios

| ID | Scenario | Behaviors to check |
| --- | --- | --- |
| 1 | Existing on-device trends vs. upload request | Preserve current intent; ask the real choice; no duplicate need |
| 2 | Fast-forward final results | Review, close and clean the change; keep needs; scope delegation; attribute evidence |
| 3 | Independent work around a manual observation | Continue ready tasks; keep manual checks and evidence |
| 4 | Routine alias | Implement and verify directly, no records or acceptance step |
| 5 | Working design repair | Revise approach and tasks under existing authority |
| 6 | New format vs. accountability | Mechanism reuses a need; independent outcome may be new |
| 7 | Plan-only | Prepare change and tasks, then stop |
| 8 | Explicit opt-out | Installed skills do not impose adoption |
| 9 | Fast-forward routine work | Finish directly without change records |
| 10 | Disposal with unique knowledge and blockers | Preserve facts in docs; keep unfinished work; handle unknown files |
| 12 | Default result review | Keep the change until actual human acceptance |
| 13 | Brownfield shop-a | Find real architectural friction; propose incremental refactoring; seek approval |
| 14 | Brownfield shop-b | Recognize good boundaries and recommend keeping them |
| 15 | Greenfield reconciliation, then CSV | Real code; shared core; small meaningful retained checks (baseline arm) |
| 16 | Need sizing, relations, retention | Reuse/split/merge carefully; sparse relations; preserve knowledge |
| 17 | Strategic test selection | Reuse stable checks; protect against data loss; avoid brittle assertions |
| 18 | Explicit coverage contract | Honor a scoped coverage requirement without equating it with correctness |
| 19 | Large modernization | Detect subsystem-sized tasks; scope reviewable increments |
| 20 | Growing scope, stale blockers | Preserve obligations and evidence; reconcile decisions; keep plans usable |
| 21 | Narrow change, many needs | Keep a coherent cross-cutting increment; partial vs. complete delivery |
| 22 | Material policy and handoff | Resolve missing policy; retain deferred detail; size is not a reason to lose meaning |
| 23 | Fresh-session handoff (2 stages) | Recover approved future rules after disposal; mutation-graded (baseline arm) |
| 24 | Long-horizon lending (4 stages) | Rules survive sessions, a revision and a rewrite; intent stays proportionate (baseline arm) |
| 25 | Bike-share need | Structural rules in needs, calibration in its home |
| 26 | Event-ticketing sequence | Plan a successor on a reviewed predecessor's delivered code |
| 27 | School timetable open items | Open items do not bind until decided |
| 28 | Meal-planner printable list | Direct delivery for bounded cross-file work, with intent and review |
| 29 | Housekeeping badge | Promote direct work to a change when coordination appears |
| 30 | Garden watering (3 stages) | Direct delivery, then managed work with deferral and delayed acceptance, then continuing that change; mechanically graded (baseline arm) |

Fixtures are evaluation inputs, not OW's implementation. Scenario prompts and the
skills' worked examples deliberately use different domains so that passing a case
reflects transferable behavior rather than recall of an example; keep it that way
when adding either.
