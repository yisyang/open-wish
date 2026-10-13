"""Prepare, run and grade OW skill evaluations in a workspace outside this checkout.

  python3 evals/run.py prepare --workspace DIR [--ids 15 23 24] [--arms skills baseline]
  python3 evals/run.py run --workspace DIR --agent "claude -p --output-format json --permission-mode acceptEdits"
  python3 evals/run.py grade --workspace DIR

Arms: `skills` installs this checkout's OW (skills plus an `ow` shim on PATH);
`baseline` gives the same task, without OW, to evals that define a baseline prompt.
Each stage runs as a fresh agent session. Grading runs external acceptance checks
and reruns the product's retained tests against an evaluator-only reference and its
seeded mutants. Dry-run evals get an assertion checklist for human or model grading.
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
ARMS = ("skills", "baseline")
SKIP = shutil.ignore_patterns(".git", "__pycache__", ".venv", "node_modules", ".pytest_cache")
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
    path.write_text(f'#!/bin/sh\nPYTHONPATH="{ROOT / "src"}${{PYTHONPATH:+:$PYTHONPATH}}" '
                    f'exec "{sys.executable}" -m openwish "$@"\n', encoding="utf-8")
    path.chmod(0o755)
    return path


def prepare(workspace, evals, arms, harness):
    if workspace.resolve().is_relative_to(ROOT):
        raise SystemExit("Use a workspace outside the source checkout.")
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
    print(f"Prepared {workspace}")


def prompt_for(item, arm, number, stage, directory):
    work = work_dir(item, directory)
    inputs = sorted(str(p) for p in (directory / "inputs").iterdir()) if (directory / "inputs").exists() else []
    response = directory / f"stage-{number}/response.md"
    role = "the product directory" if "scenario" in item else "the assigned output directory"
    header = (f"Evaluation setup from the coordinator:\n- Your working directory {work} is {role}.\n"
              f"- Supplied read-only inputs: {', '.join(inputs) or 'none'}.\n"
              f"- Save response.md to {response}.\n\n")
    return header + stage["baseline_prompt" if arm == "baseline" else "prompt"]


def usage(stdout):
    try:
        value = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(value, dict):
        return {}
    return {key: value[key] for key in ("usage", "total_cost_usd", "num_turns") if key in value}


def run(workspace, evals, arms, agent, timeout):
    command = shlex.split(agent)
    for item in evals:
        for arm in arms_for(item, arms):
            directory = arm_dir(workspace, item, arm)
            if not directory.exists():
                raise SystemExit(f"Run prepare first: {directory}")
            work = work_dir(item, directory)
            environment = dict(os.environ)
            if arm == "skills":
                environment["PATH"] = f"{workspace / 'bin'}{os.pathsep}{environment.get('PATH', '')}"
            for number, stage in enumerate(stages(item), 1):
                stage_dir = directory / f"stage-{number}"
                if (stage_dir / "metrics.json").exists():
                    continue
                stage_dir.mkdir(exist_ok=True)
                prompt = prompt_for(item, arm, number, stage, directory)
                (stage_dir / "prompt.md").write_text(prompt, encoding="utf-8")
                started = time.monotonic()
                try:
                    result = subprocess.run([*command, prompt], cwd=work, env=environment,
                                            capture_output=True, text=True, timeout=timeout)
                    code, stdout, stderr = result.returncode, result.stdout, result.stderr
                except subprocess.TimeoutExpired as error:
                    code, stdout, stderr = "timeout", error.stdout or "", error.stderr or ""
                    stdout, stderr = (s.decode() if isinstance(s, bytes) else s for s in (stdout, stderr))
                metrics = {"seconds": round(time.monotonic() - started, 1), "exit_code": code, **usage(stdout)}
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


def unittest_run(project, tests, timeout=300):
    started = time.monotonic()
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    environment.pop("PYTHONPATH", None)
    try:
        result = subprocess.run([sys.executable, "-m", "unittest", *tests], cwd=project, env=environment,
                                capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"passed": False, "ran": None, "seconds": timeout, "tail": "timeout"}
    output = result.stdout + result.stderr
    ran = next((int(line.split()[1]) for line in output.splitlines() if line.startswith("Ran ")), 0)
    return {"passed": result.returncode == 0 and ran > 0, "ran": ran,
            "seconds": round(time.monotonic() - started, 2), "tail": output.strip().splitlines()[-1:]}


def mutation(project, grading, stage):
    """Retained tests should pass on the reference contract and fail on each seeded mutant."""
    tests = retained_tests(project)
    if not tests:
        return {"status": "no retained Python tests found"}
    reference = ROOT / grading["reference"]
    spec = importlib.util.spec_from_file_location("ow_eval_reference", reference)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def substituted(mutant):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "product"
            shutil.copytree(project, copy, ignore=SKIP)
            (copy / grading["target"]).write_text(
                "import importlib.util as _util\n"
                f"_spec = _util.spec_from_file_location('ow_eval_reference', {str(reference)!r})\n"
                "_module = _util.module_from_spec(_spec)\n_spec.loader.exec_module(_module)\n"
                f"globals().update(_module.build({stage}, {mutant!r}))\n", encoding="utf-8")
            return unittest_run(copy, tests)

    own = unittest_run(project, tests)
    baseline = substituted(None)
    if not baseline["passed"]:
        return {"status": "inconclusive: retained tests fail on the reference contract (they may depend on internals)",
                "tests": tests, "own_suite": own, "reference": baseline}
    outcomes = {mutant: "killed" if not substituted(mutant)["passed"] else "survived"
                for mutant in module.MUTANTS.get(stage, [])}
    return {"status": "graded", "tests": tests, "own_suite": own, "mutants": outcomes,
            "killed": sum(v == "killed" for v in outcomes.values()), "total": len(outcomes)}


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
                environment = {**os.environ, "PROJECT_DIR": str(project), "STAGE": str(number)}
                check = subprocess.run([sys.executable, str(ROOT / grading["acceptance"])], env=environment,
                                       capture_output=True, text=True, timeout=300)
                row["acceptance"] = "pass" if check.returncode == 0 else "fail"
                row["acceptance_tail"] = check.stderr.strip().splitlines()[-3:]
                if "reference" in grading:
                    row["mutation"] = mutation(project, grading, number)
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
        killed = (f"{mutation_row['killed']}/{mutation_row['total']} mutants killed"
                  if mutation_row.get("status") == "graded" else mutation_row.get("status", ""))
        tokens = row.get("usage", {})
        tokens = f"{tokens.get('input_tokens', 0) + tokens.get('output_tokens', 0)} tok" if tokens else ""
        seconds = f"{row['seconds']}s" if "seconds" in row else ""
        print(" ".join(str(part) for part in (f"{row['id']:>2} {row['arm']:<8} stage {row.get('stage', '-')}:",
                                              row.get("acceptance", row.get("status")), killed, seconds, tokens) if part))
    print(f"Wrote {workspace / 'results.json'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("prepare", "run", "grade"))
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--ids", type=int, nargs="+", default=[])
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    parser.add_argument("--harness", default="claude", choices=("opencode", "claude", "codex", "generic"))
    parser.add_argument("--agent", help="Agent command; the prompt is appended as its final argument")
    parser.add_argument("--timeout", type=int, default=3600, help="Seconds per stage")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    evals = load_evals(args.ids)
    if args.command == "prepare":
        prepare(workspace, evals, args.arms, args.harness)
    elif args.command == "run":
        if not args.agent:
            raise SystemExit("--agent is required for run")
        prepare(workspace, evals, args.arms, args.harness)
        run(workspace, evals, args.arms, args.agent, args.timeout)
    else:
        grade(workspace, evals, args.arms)


if __name__ == "__main__":
    main()
