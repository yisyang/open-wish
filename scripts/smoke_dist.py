"""Install the actual release distributions with uv and exercise their CLI/assets."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from check_release import cli_version

HARNESSES = ("opencode", "claude", "codex", "generic")
SKILLS = ("core", "propose", "align", "plan", "implement", "review", "consolidate", "fast-forward", "onboard", "assess",
          "coordinate")


def snapshot(root):
    return {path.relative_to(root): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in root.rglob("*") if path.is_file()}


def smoke(artifact, version):
    with tempfile.TemporaryDirectory(prefix="openwish-dist-") as directory:
        root = Path(directory)
        environment = {**os.environ, "UV_TOOL_DIR": str(root / "tools"),
                       "UV_TOOL_BIN_DIR": str(root / "bin")}
        environment.pop("PYTHONPATH", None)

        def run(*command):
            result = subprocess.run(command, cwd=root, env=environment, capture_output=True,
                                    text=True, timeout=120)
            if result.returncode:
                raise RuntimeError(f"{command!r} failed:\n{result.stdout}\n{result.stderr}")
            return result.stdout

        run("uv", "tool", "install", "--python", sys.executable, str(artifact))
        ow = str(root / "bin" / ("ow.exe" if os.name == "nt" else "ow"))
        openwish = str(root / "bin" / ("openwish.exe" if os.name == "nt" else "openwish"))
        for executable in (ow, openwish):
            if run(executable, "--version").strip() != f"OpenWish {cli_version(version)}":
                raise RuntimeError(f"The installed {Path(executable).name} version does not match the release.")
        project = root / "product"
        run(ow, "init", str(project), "--harness", *HARNESSES)
        result = json.loads(run(ow, "--root", str(project), "check", "--json"))
        if result != {"errors": [], "warnings": []}:
            raise RuntimeError(f"Initialized project failed validation: {result}")
        for directory in (".opencode", ".claude", ".agents"):
            for skill in SKILLS:
                path = project / directory / f"skills/ow-{skill}/SKILL.md"
                if f'openwish-version: "{cli_version(version)}"' not in path.read_text(encoding="utf-8"):
                    raise RuntimeError(f"Missing or incorrectly versioned packaged skill: {path}")
        for relative in (".opencode/commands/fast-forward.md", ".opencode/commands/onboard.md",
                         ".claude/skills/fast-forward/SKILL.md", ".claude/skills/onboard/SKILL.md",
                         ".agents/skills/ow-fast-forward/agents/openai.yaml",
                         ".agents/skills/ow-core/artifacts.md", "openwish/policy.md"):
            if not (project / relative).read_text(encoding="utf-8").strip():
                raise RuntimeError(f"Missing installed asset: {relative}")
        before = snapshot(project)
        run(ow, "init", str(project), "--harness", *HARNESSES)
        if snapshot(project) != before:
            raise RuntimeError("Reinitializing at the same version modified project files.")

        # Exercise the installed implementation rather than importing from source.
        def command(*args):
            return run(ow, "--root", str(project), *args)

        command("new", "need", "N-001", "--title", "Local reconciliation")
        need = project / "openwish/needs/N-001.md"
        text = need.read_text(encoding="utf-8")
        text = text.replace('actor = ""', 'actor = "Operations staff"')
        text = text.replace('outcome = ""', 'outcome = "Reconcile records locally"')
        text = text.replace('acceptance = []', 'acceptance = ["Records stay on device"]')
        need.write_text(text, encoding="utf-8")
        command("new", "change", "C-001", "--title", "Verify local behavior", "--need", "N-001", "--fast-forward")
        command("check")
        ready = json.loads(command("ready", "N-001", "--json"))
        unplanned = [(change["id"], change["waiting_on"]) for change in ready["unplanned"]]
        if ready["ready"] or ready["waiting"] or unplanned != [("C-001", [])]:
            raise RuntimeError(f"Verification-only change invented work or lost visibility: {ready}")
        handoff = root / "handoff.json"
        handoff.write_text(json.dumps({"handoff": [{
            "requirement": "Retain local-only intent through disposal in this structural smoke fixture",
            "disposition": "retained", "destinations": ["openwish/needs/N-001.md"],
            "evidence": "Need content inspected; this smoke scenario claims no delivered product behavior"
        }]}), encoding="utf-8")
        command("record-review", "C-001", "--summary", "Distribution workflow smoke scenario",
                "--check", "Synthetic fixture: artifact validation passed; no product behavior claimed",
                "--handoff", str(handoff))
        command("close", "C-001", "--by", "fast-forward")
        preview = json.loads(command("clean", "C-001", "--dry-run", "--json"))
        if not preview["handoff"]["C-001"] or not (project / "openwish/changes/C-001").is_dir():
            raise RuntimeError("Cleanup preview lost its handoff or modified the change.")
        command("clean", "C-001")
        status = json.loads(command("status", "--json"))
        if status["changes"] or need.read_text(encoding="utf-8") != text:
            raise RuntimeError("Change disposal failed to retain durable intent unchanged.")
        command("check")
    print(f"PASS {artifact.name}: uv install, aliases, harness assets, no-op init, and change lifecycle/disposal")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    expected = {f"openwish-{args.expected_version}-py3-none-any.whl", f"openwish-{args.expected_version}.tar.gz"}
    try:
        actual = {path.name for path in directory.iterdir() if path.name != ".gitignore"}
        if actual != expected:
            raise RuntimeError(f"Expected only {sorted(expected)} in {directory}; found {sorted(actual)}.")
        for name in sorted(expected):
            smoke(directory / name, args.expected_version)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Distribution smoke test: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
