"""Check package identity/version before building or publishing a release."""

import argparse
import ast
from pathlib import Path
import re
import sys
import tomllib


def check_version(root, tag=""):
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project.get("name") != "openwish":
        raise ValueError("The published package name must be openwish.")
    version = project.get("version", "")
    if not isinstance(version, str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version):
        raise ValueError("Releases currently require a stable MAJOR.MINOR.PATCH version.")
    module = ast.parse((root / "src/openwish/__init__.py").read_text(encoding="utf-8"))
    versions = [ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)]
    if versions != [version]:
        raise ValueError(f"pyproject.toml version {version} does not match the CLI __version__ {versions}.")
    if tag and tag != f"v{version}":
        raise ValueError(f"Release tag {tag!r} must be v{version}.")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="", help="Optional GitHub release tag, e.g. v0.3.1")
    args = parser.parse_args()
    try:
        print(check_version(Path(__file__).resolve().parents[1], args.tag))
    except (OSError, ValueError, SyntaxError, KeyError) as error:
        print(f"Release check: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
