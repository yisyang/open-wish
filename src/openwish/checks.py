"""Run one check, keep its full log and write the short evidence record that tasks and reviews cite."""

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import subprocess
import time

from .repository import git, is_repository
from .storage import WishError, write_json

TAIL_LINES = 30
FLAKY_EXIT = 4


def evidence_directory(root, value):
    """Logs inside the repository would count as product files and make every pending review stale."""
    directory = Path(value).resolve()
    if directory.is_relative_to(root):
        try:
            # The trailing slash matters: a directory pattern such as `evidence/` does not
            # match a path that does not exist yet unless git is told it is a directory.
            git(root, "check-ignore", "-q", f"{directory}/")
        except (OSError, subprocess.SubprocessError) as error:
            raise WishError("Keep check evidence outside the repository or in a directory it ignores; "
                            "logs inside it would make pending reviews stale.") from error
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def revision(root):
    if not is_repository(root):
        return None
    try:
        return {"head": git(root, "rev-parse", "HEAD").decode().strip(),
                "dirty": bool(git(root, "status", "--porcelain").strip())}
    except (OSError, subprocess.SubprocessError):
        return None


def now():
    return datetime.now(timezone.utc).isoformat()


def run_check(root, name, evidence, command, attempts=1):
    """Return (exit code, text to print). A failure followed by a pass is FLAKY, never PASS."""
    if not re.fullmatch(r"[\w.-]+", name):
        raise WishError("Check names use letters, digits, '.', '_' and '-'.")
    if attempts < 1:
        raise WishError("--attempts must be at least 1.")
    directory = evidence_directory(root, evidence)
    base, number = directory / name, 2
    while Path(f"{base}.json").exists():
        base, number = directory / f"{name}-{number}", number + 1
    record_path = Path(f"{base}.json")
    record = {"name": name, "command": command, "cwd": os.getcwd(), "started_at": now(),
              "status": "RUNNING", "pid": os.getpid(), "revision": revision(root)}
    write_json(record_path, record)  # visible while running; RUNNING with a dead pid means it was killed
    runs = []
    for attempt in range(1, attempts + 1):
        log = Path(f"{base}.log" if attempt == 1 else f"{base}.attempt-{attempt}.log")
        started = time.monotonic()
        try:
            with log.open("wb") as output:
                code = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=output,
                                      stderr=subprocess.STDOUT).returncode
        except OSError as error:
            log.write_text(f"Cannot start {command[0]}: {error}\n", encoding="utf-8")
            code = 127
        runs.append({"exit_code": code, "seconds": round(time.monotonic() - started, 1), "log": str(log)})
        if code == 0:
            break
    first, last = runs[0], runs[-1]
    status = "PASS" if first["exit_code"] == 0 else "FLAKY" if last["exit_code"] == 0 else "FAIL"
    exit_code = 0 if status == "PASS" else FLAKY_EXIT if status == "FLAKY" else last["exit_code"]
    if not 0 <= exit_code < 256:
        exit_code = 1  # killed by a signal
    record.update({"ended_at": now(), "seconds": round(sum(run["seconds"] for run in runs), 1),
                   "status": status, "exit_code": exit_code, "log": first["log"]})
    if attempts > 1:
        record["attempts"] = runs
    write_json(record_path, record)
    state = record["revision"]
    at = f" at {state['head'][:12]}{' (dirty)' if state['dirty'] else ''}" if state else ""
    tries = f" on attempt {len(runs)} of {attempts}" if attempts > 1 else ""
    lines = [f"{status} {name}: exit {exit_code}{tries} in {record['seconds']}s{at}", f"record {record_path}"]
    if status != "PASS":
        # A flaky run shows its first failure, which is what needs fixing.
        shown = Path(first["log"] if status == "FLAKY" else last["log"])
        lines.extend(shown.read_text(encoding="utf-8", errors="replace").splitlines()[-TAIL_LINES:])
    return exit_code, "\n".join(lines)
