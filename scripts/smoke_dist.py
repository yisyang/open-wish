"""Install the actual release distributions with uv and exercise their CLI/assets."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HARNESSES = ("opencode", "claude", "codex", "generic")
SKILLS = ("propose", "align", "plan", "implement", "review", "consolidate", "fast-forward", "onboard")


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
        if run(ow, "--version").strip() != f"OpenWish {version}":
            raise RuntimeError("The installed CLI version does not match the release.")
        project = root / "product"
        run(ow, "init", str(project), "--harness", *HARNESSES)
        result = json.loads(run(ow, "--root", str(project), "check", "--json"))
        if result != {"errors": [], "warnings": []}:
            raise RuntimeError(f"Initialized project failed validation: {result}")
        for directory in (".opencode", ".claude", ".agents"):
            for skill in SKILLS:
                path = project / directory / f"skills/ow-{skill}/SKILL.md"
                if f'openwish-version: "{version}"' not in path.read_text(encoding="utf-8"):
                    raise RuntimeError(f"Missing or incorrectly versioned packaged skill: {path}")
        for relative in (".opencode/commands/fast-forward.md", ".opencode/commands/onboard.md",
                         ".claude/skills/fast-forward/SKILL.md", ".claude/skills/onboard/SKILL.md",
                         ".agents/skills/ow-fast-forward/agents/openai.yaml",
                         "openwish/policy.md", "openwish/artifacts.md"):
            if not (project / relative).read_text(encoding="utf-8").strip():
                raise RuntimeError(f"Missing installed asset: {relative}")
        before = snapshot(project)
        run(ow, "init", str(project), "--harness", *HARNESSES)
        if snapshot(project) != before:
            raise RuntimeError("Reinitializing at the same version modified project files.")
    print(f"PASS {artifact.name}: uv install, CLI version, all harnesses/assets, validation, and no-op reinitialization")


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
