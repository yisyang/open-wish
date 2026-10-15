"""Prepare, run and grade OW skill evaluations in a workspace outside this checkout.

  python3 evals/run.py prepare --workspace DIR [--ids 15 23 24] [--arms skills baseline] [--agent codex]
  python3 evals/run.py run --workspace DIR [--agent codex|claude|"COMMAND" --harness H]
  python3 evals/run.py grade --workspace DIR

Agents are presets with a pinned model and planning-level reasoning (`codex`, the
default, and `claude`), or a custom command that may use {work} and {stage_dir}; the
prompt is appended as the last argument. Presets run with an isolated agent home that
links only the user's credentials, so personal instructions, memories, plugins and
settings cannot leak into results. A workspace serves one agent.

Arms: `skills` installs this checkout's OW (skills plus an `ow` shim on PATH);
`baseline` gives the same task, without OW, to evals that define a baseline prompt.
Each stage runs as a fresh agent session. Grading runs external acceptance checks
and reruns the product's retained tests against an evaluator-only reference and its
seeded mutants: only tests that pass on the reference grade the mutants, and a mutant
counts as killed only when one of them fails an assertion. Dry-run evals get an
assertion checklist for human or model grading.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "evals/probe.py"
ARMS = ("skills", "baseline")
SKIP = shutil.ignore_patterns(".git", "__pycache__", ".venv", "node_modules", ".pytest_cache")
# Agents write only in the working directory, plus the stage directory for response.md.
AGENTS = {
    "codex": {"harness": "codex", "home": ("CODEX_HOME", "~/.codex", "auth.json"),
              "command": "codex exec --json --ignore-user-config -m gpt-6.1-sol -c 'model_reasoning_effort=\"high\"' "
                         "--skip-git-repo-check --ephemeral --sandbox workspace-write --add-dir {stage_dir}"},
    "claude": {"harness": "claude", "home": ("CLAUDE_CONFIG_DIR", "~/.claude", ".credentials.json"),
               # Variadic options (--add-dir, --allowedTools) must not be last, or they swallow the prompt.
               "command": "claude -p --model claude-opus-5-5 --effort high --strict-mcp-config "
                          "--add-dir {stage_dir} --allowedTools Bash,Read,Write,Edit,Glob,Grep,Skill "
                          "--permission-mode acceptEdits --output-format json"},
}
SETUP_DIRECTORIES = {"openwish", ".claude", ".agents", ".opencode", "__pycache__", ".git", ".venv"}


def load_evals(ids):
    evals = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))["evals"]
    if ids:
        known = {item["id"] for item in evals}
        missing = set(ids) - known
        if missing:
            raise SystemExit(f"Unknown eval IDs: {sorted(missing)}")
        evals = [item for item in evals if item["id"] in ids]
    return evals


def stages(item):
    if "scenario" in item:
        return json.loads((ROOT / item["scenario"]).read_text(encoding="utf-8"))["stages"]
    stage = {"prompt": item["prompt"]}
    if "baseline_prompt" in item:
        stage["baseline_prompt"] = item["baseline_prompt"]
    return [stage]


def arms_for(item, arms):
    return [arm for arm in arms if arm == "skills" or all("baseline_prompt" in s for s in stages(item))]


def arm_dir(workspace, item, arm):
    return workspace / f"{item['id']:02d}-{item['name']}" / arm


def work_dir(item, directory):
    # Staged scenarios work inside the evolving product; others get an output directory.
    return directory / ("product" if "scenario" in item else "work")


def shim(workspace):
    path = workspace / "bin/ow"
    path.parent.mkdir(parents=True, exist_ok=True)
    # OW_EVAL_LOG, set per stage, records each invocation so grading can see the workflow an agent used.
    path.write_text(f'#!/bin/sh\n[ -n "$OW_EVAL_LOG" ] && printf \'%s\\n\' "$*" >> "$OW_EVAL_LOG"\n'
                    f'PYTHONPATH="{ROOT / "src"}${{PYTHONPATH:+:$PYTHONPATH}}" '
                    f'exec "{sys.executable}" -m openwish "$@"\n', encoding="utf-8")
    path.chmod(0o755)
    return path


def resolve_agent(agent, harness):
    """A preset name or a custom command; custom commands must name their harness."""
    if agent in AGENTS:
        return {"name": agent, **AGENTS[agent], "harness": harness or AGENTS[agent]["harness"]}
    if not harness:
        raise SystemExit("A custom --agent command needs --harness.")
    return {"name": "custom", "command": agent, "harness": harness}


def claim_workspace(workspace, agent):
    """Refuse to mix agents in one workspace: arms and stages are reused by existence."""
    record = workspace / "agent.json"
    identity = {"command": agent["command"], "harness": agent["harness"]}
    if record.exists():
        if json.loads(record.read_text(encoding="utf-8")) != identity:
            raise SystemExit(f"{workspace} was prepared for another agent ({record}); use a new workspace.")
    else:
        workspace.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")


def agent_environment(workspace, agent):
    """An isolated agent home holding only a link to the user's credentials."""
    if "home" not in agent:
        return {}
    variable, default, credentials = agent["home"]
    source = Path(os.environ.get(variable) or default).expanduser() / credentials
    if not source.exists():
        raise SystemExit(f"Sign in to {agent['name']} first: {source} not found.")
    home = workspace / "agent-home" / agent["name"]
    home.mkdir(parents=True, exist_ok=True)
    link = home / credentials
    if not link.is_symlink():
        link.symlink_to(source)
    return {variable: str(home)}


def prepare(workspace, evals, arms, agent):
    if workspace.resolve().is_relative_to(ROOT):
        raise SystemExit("Use a workspace outside the source checkout.")
    claim_workspace(workspace, agent)
    harness = agent["harness"]
    ow = shim(workspace)
    for item in evals:
        for arm in arms_for(item, arms):
            directory = arm_dir(workspace, item, arm)
            if directory.exists():
                continue
            work = work_dir(item, directory)
            work.mkdir(parents=True)
            for relative in item.get("files", []):
                source = ROOT / relative
                target = directory / "inputs" / source.name
                if source.is_dir():
                    shutil.copytree(source, target, ignore=SKIP)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
            if arm == "skills":
                subprocess.run([str(ow), "init", str(work), "--harness", harness], check=True,
                               capture_output=True, text=True, timeout=60)
            if "seed" in item:
                apply_seed(ROOT / item["seed"], work, ow if arm == "skills" else None)
    print(f"Prepared {workspace}")


def apply_seed(seed, work, ow):
    """Materialize the records a scenario describes: copy `files/`, then run `setup.json`'s
    ow commands so reviews and other derived state are real. Baselines get no OW records."""
    for source in sorted((seed / "files").rglob("*")):
        relative = source.relative_to(seed / "files")
        if source.is_dir() or (ow is None and relative.parts[0] == "openwish"):
            continue
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    setup = seed / "setup.json"
    if ow is None or not setup.exists():
        return
    for step in json.loads(setup.read_text(encoding="utf-8")):
        stdin = json.dumps(step["stdin"]) if "stdin" in step else None
        result = subprocess.run([str(ow), *step["args"]], cwd=work, input=stdin, capture_output=True,
                                text=True, timeout=60)
        if result.returncode:
            raise SystemExit(f"Seed {seed.name} failed at {step['args'][:2]}: {result.stdout}{result.stderr}")


def prompt_for(item, arm, number, stage, directory):
    work = work_dir(item, directory)
    inputs = sorted(str(p) for p in (directory / "inputs").iterdir()) if (directory / "inputs").exists() else []
    response = directory / f"stage-{number}/response.md"
    role = "the product directory" if "scenario" in item else "the assigned output directory"
    header = (f"Evaluation setup from the coordinator:\n- Your working directory {work} is {role}.\n"
              f"- Supplied read-only inputs: {', '.join(inputs) or 'none'}.\n")
    if "seed" in item:
        header += ("- The working directory holds the project's records and representative files. Code, "
                   "evidence and decisions the task states but the directory lacks are given facts.\n")
    elif "scenario" not in item and "grading" not in item:
        installed = " beyond the installed OW guidance and empty records" if arm == "skills" else ""
        header += ("- The task describes a project you cannot see. Its stated needs, changes, code, evidence "
                   f"and decisions are given facts; the working directory holds none of them{installed}. "
                   "Do not report their absence as a finding.\n")
    header += f"- Save response.md to {response}.\n\n"
    return header + stage["baseline_prompt" if arm == "baseline" else "prompt"]


def usage(stdout):
    """Usage from Claude's single JSON result or Codex's JSONL `turn.completed` events."""
    try:
        value = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        value = None
    if isinstance(value, dict):
        return {key: value[key] for key in ("usage", "total_cost_usd", "num_turns") if key in value}
    totals, tool_calls = {}, 0
    for line in (stdout or "").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "turn.completed":
            for key, count in (event.get("usage") or {}).items():
                if isinstance(count, int):
                    totals[key] = totals.get(key, 0) + count
        elif event.get("type") == "item.completed" and (event.get("item") or {}).get("type") != "agent_message":
            tool_calls += 1
    return {"usage": totals, "tool_calls": tool_calls} if totals else {}


def run(workspace, evals, arms, agent, timeout):
    isolated = agent_environment(workspace, agent)
    for item in evals:
        for arm in arms_for(item, arms):
            directory = arm_dir(workspace, item, arm)
            if not directory.exists():
                raise SystemExit(f"Run prepare first: {directory}")
            work = work_dir(item, directory)
            environment = {**os.environ, **isolated}
            if arm == "skills":
                environment["PATH"] = f"{workspace / 'bin'}{os.pathsep}{environment.get('PATH', '')}"
            for number, stage in enumerate(stages(item), 1):
                stage_dir = directory / f"stage-{number}"
                if (stage_dir / "metrics.json").exists():
                    continue
                stage_dir.mkdir(exist_ok=True)
                prompt = prompt_for(item, arm, number, stage, directory)
                (stage_dir / "prompt.md").write_text(prompt, encoding="utf-8")
                calls = stage_dir / "ow-calls.log"
                if arm == "skills":
                    environment["OW_EVAL_LOG"] = str(calls)
                command = [part.replace("{work}", str(work)).replace("{stage_dir}", str(stage_dir))
                           for part in shlex.split(agent["command"])]
                started = time.monotonic()
                try:
                    result = subprocess.run([*command, prompt], cwd=work, env=environment, stdin=subprocess.DEVNULL,
                                            capture_output=True, text=True, timeout=timeout)
                    code, stdout, stderr = result.returncode, result.stdout, result.stderr
                except subprocess.TimeoutExpired as error:
                    code, stdout, stderr = "timeout", error.stdout or "", error.stderr or ""
                    stdout, stderr = (s.decode() if isinstance(s, bytes) else s for s in (stdout, stderr))
                metrics = {"seconds": round(time.monotonic() - started, 1), "exit_code": code, **usage(stdout)}
                if calls.exists():
                    metrics["ow_calls"] = len(calls.read_text(encoding="utf-8").splitlines())
                if "scenario" in item and (work / ".git").exists():
                    metrics["warning"] = "Product has Git history; later sessions may recover earlier context."
                (stage_dir / "transcript.txt").write_text(stdout + "\n--- stderr ---\n" + stderr, encoding="utf-8")
                shutil.copytree(work, stage_dir / "snapshot", ignore=SKIP)
                (stage_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
                print(f"{item['id']:>2} {arm:<8} stage {number}: exit {code} in {metrics['seconds']}s")


def retained_tests(project):
    return sorted(p.relative_to(project).as_posix() for p in project.rglob("*.py")
                  if (p.name.startswith("test") or p.stem.endswith("_test"))
                  and not SETUP_DIRECTORIES.intersection(p.relative_to(project).parts))


def probe(project, tests, only=None, timeout=300):
    """Each retained test's outcome (pass/fail/error/skip) in a fresh interpreter."""
    started = time.monotonic()
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    environment.pop("PYTHONPATH", None)
    selection = ["--only", *only, "--"] if only else []
    try:
        result = subprocess.run([sys.executable, str(PROBE), *selection, *tests], cwd=project, env=environment,
                                capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "outcomes": {}, "messages": {}, "seconds": timeout}
    seconds = round(time.monotonic() - started, 2)
    _, marker, data = result.stdout.rpartition("--- ow-probe ---\n")
    if not marker:
        return {"status": "crashed", "outcomes": {}, "messages": {}, "seconds": seconds,
                "tail": (result.stdout + result.stderr).strip().splitlines()[-5:]}
    return {"status": "ran", **json.loads(data), "seconds": seconds}


def summary(run):
    counts = {}
    for outcome in run["outcomes"].values():
        counts[outcome] = counts.get(outcome, 0) + 1
    passed = run["status"] == "ran" and counts.get("pass", 0) > 0 and not counts.get("fail") and not counts.get("error")
    return {"passed": passed, "status": run["status"], "counts": counts, "seconds": run["seconds"],
            "problems": {key: run["messages"].get(key, outcome) for key, outcome in run["outcomes"].items()
                         if outcome in ("fail", "error")}}


def mutation(project, grading, stage):
    """Retained tests that pass on the reference contract should fail each seeded mutant.

    Tests failing on the reference check choices the contract leaves open (input
    validation, extension APIs, internals); they are reported and left out rather than
    making the whole grade inconclusive. A mutant is killed only by an assertion
    failure: errors, crashes and timeouts are not evidence that a rule is protected.
    """
    tests = retained_tests(project)
    if not tests:
        return {"status": "no retained Python tests found"}
    reference = ROOT / grading["reference"]
    spec = importlib.util.spec_from_file_location("ow_eval_reference", reference)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def substituted(mutant, only=None):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "product"
            shutil.copytree(project, copy, ignore=SKIP)
            (copy / grading["target"]).write_text(
                "import importlib.util as _util\n"
                f"_spec = _util.spec_from_file_location('ow_eval_reference', {str(reference)!r})\n"
                "_module = _util.module_from_spec(_spec)\n_spec.loader.exec_module(_module)\n"
                f"globals().update(_module.build({stage}, {mutant!r}))\n", encoding="utf-8")
            return probe(copy, tests, only)

    control = substituted(None)
    compatible = sorted(key for key, outcome in control["outcomes"].items() if outcome == "pass")
    report = {"tests": tests, "reference": summary(control),
              "compatible": f"{len(compatible)}/{len(control['outcomes'])} tests pass on the reference"}
    if not compatible:
        return {"status": "inconclusive: no retained test passes on the reference contract", **report}
    outcomes = {}
    for mutant in module.MUTANTS.get(stage, []):
        run = substituted(mutant, compatible)
        failed = sorted(key for key, outcome in run["outcomes"].items() if outcome == "fail")
        errored = sorted(key for key, outcome in run["outcomes"].items() if outcome == "error")
        status = "killed" if failed else "errored" if errored or run["status"] != "ran" else "survived"
        outcomes[mutant] = {"status": status, "by": {key: run["messages"].get(key, "") for key in failed or errored}}
    return {"status": "graded", **report, "mutants": outcomes,
            "killed": sum(value["status"] == "killed" for value in outcomes.values()), "total": len(outcomes)}


def intent_metrics(work):
    needs = sorted((work / "openwish/needs").glob("*.md")) if (work / "openwish/needs").exists() else []
    changes = sorted((work / "openwish/changes").glob("*/change.md")) if (work / "openwish/changes").exists() else []
    return {"needs": len(needs), "needs_bytes": sum(p.stat().st_size for p in needs),
            "needs_digest": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in needs},
            "remaining_changes": len(changes)}


def grade(workspace, evals, arms):
    results = []
    for item in evals:
        for arm in arms_for(item, arms):
            directory = arm_dir(workspace, item, arm)
            grading = item.get("grading")
            if not directory.exists():
                continue
            if not grading:
                checklist = "\n".join(f"- [ ] {assertion}" for assertion in item["assertions"])
                (directory / "grading.md").write_text(
                    f"# {item['id']} {item['name']} ({arm})\n\nExpected: {item['expected_output']}\n\n"
                    f"{checklist}\n\nGrade the saved response and actual edits, not claims of compliance.\n",
                    encoding="utf-8")
                results.append({"id": item["id"], "arm": arm, "status": "manual: see grading.md"})
                continue
            previous = None
            for number in range(1, len(stages(item)) + 1):
                stage_dir = directory / f"stage-{number}"
                if not (stage_dir / "snapshot").exists():
                    continue
                work = stage_dir / "snapshot"
                project = work / grading.get("project_dir", ".")
                row = {"id": item["id"], "arm": arm, "stage": number,
                       **json.loads((stage_dir / "metrics.json").read_text(encoding="utf-8"))}
                environment = {**os.environ, "PROJECT_DIR": str(project), "STAGE": str(number), "ARM": arm,
                               "OW_CALLS": str(stage_dir / "ow-calls.log"), "OW": str(workspace / "bin/ow")}
                check = subprocess.run([sys.executable, str(ROOT / grading["acceptance"])], env=environment,
                                       cwd=project, capture_output=True, text=True, timeout=300)
                row["acceptance"] = "pass" if check.returncode == 0 else "fail"
                row["acceptance_tail"] = check.stderr.strip().splitlines()[-3:]
                tests = retained_tests(project) if project.exists() else []
                if tests:
                    row["own_suite"] = summary(probe(project, tests))
                if "reference" in grading:
                    # Mutant kills mean nothing from a suite that fails on its own product.
                    row["mutation"] = (mutation(project, grading, number) if row.get("own_suite", {}).get("passed")
                                       else {"status": "invalid: the product's own retained tests fail or are missing"})
                metrics = intent_metrics(work)
                if previous is not None:
                    row["needs_changed"] = sorted(name for name in metrics["needs_digest"].keys() | previous.keys()
                                                  if metrics["needs_digest"].get(name) != previous.get(name))
                previous = metrics.pop("needs_digest")
                row["intent"] = metrics
                results.append(row)
    (workspace / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for row in results:
        mutation_row = row.get("mutation", {})
        killed = (f"{mutation_row['killed']}/{mutation_row['total']} mutants killed "
                  f"({mutation_row['compatible']})"
                  if mutation_row.get("status") == "graded" else mutation_row.get("status", ""))
        own = row.get("own_suite")
        own = f"own tests {'pass' if own['passed'] else 'FAIL'}" if own else ""
        tokens = row.get("usage", {})
        cost = (f"${row['total_cost_usd']:.2f}" if "total_cost_usd" in row else
                f"{tokens.get('input_tokens', 0) + tokens.get('output_tokens', 0)} tok" if tokens else "")
        turns = (f"{row['num_turns']} turns" if "num_turns" in row else
                 f"{row['tool_calls']} tool calls" if "tool_calls" in row else "")
        turns += f", {row['ow_calls']} ow calls" if "ow_calls" in row else ""
        seconds = f"{row['seconds']}s" if "seconds" in row else ""
        print(" ".join(str(part) for part in (f"{row['id']:>2} {row['arm']:<8} stage {row.get('stage', '-')}:",
                                              row.get("acceptance", row.get("status")), own, killed, seconds,
                                              turns, cost) if part))
    print(f"Wrote {workspace / 'results.json'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("prepare", "run", "grade"))
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--ids", type=int, nargs="+", default=[])
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    parser.add_argument("--agent", default="codex",
                        help=f"Preset ({', '.join(AGENTS)}) or a command with optional {{work}} and {{stage_dir}}")
    parser.add_argument("--harness", choices=("opencode", "claude", "codex", "generic"),
                        help="OW harness to install; presets choose their own")
    parser.add_argument("--timeout", type=int, default=3600, help="Seconds per stage")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    evals = load_evals(args.ids)
    if args.command == "prepare":
        prepare(workspace, evals, args.arms, resolve_agent(args.agent, args.harness))
    elif args.command == "run":
        agent = resolve_agent(args.agent, args.harness)
        prepare(workspace, evals, args.arms, agent)
        run(workspace, evals, args.arms, agent, args.timeout)
    else:
        grade(workspace, evals, args.arms)


if __name__ == "__main__":
    main()
