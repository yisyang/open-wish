"""Check package identity/version before building or publishing a release."""

import argparse
import ast
from pathlib import Path
import re
import sys
import tomllib


NUMBER = r"(?:0|[1-9][0-9]*)"
VERSION = re.compile(rf"({NUMBER}\.{NUMBER}\.{NUMBER})(?:rc([1-9][0-9]*))?")


def cli_version(version):
    """The SemVer the CLI stamps for a package version: 1.0.0rc1 is 1.0.0-rc.1, below 1.0.0."""
    match = VERSION.fullmatch(version)
    if not match:
        raise ValueError("Releases require MAJOR.MINOR.PATCH, or MAJOR.MINOR.PATCHrcN for a release candidate.")
    release, candidate = match.groups()
    return f"{release}-rc.{candidate}" if candidate else release


def check_version(root, tag=""):
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project.get("name") != "openwish":
        raise ValueError("The published package name must be openwish.")
    version = project.get("version", "")
    if not isinstance(version, str):
        raise ValueError("pyproject.toml must declare a string version.")
    expected = cli_version(version)
    module = ast.parse((root / "src/openwish/__init__.py").read_text(encoding="utf-8"))
    versions = [ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)]
    if versions != [expected]:
        raise ValueError(f"pyproject.toml version {version} requires the CLI __version__ {expected}, "
                         f"found {versions}.")
    if tag and tag != f"v{version}":
        raise ValueError(f"Release tag {tag!r} must be v{version}.")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="", help="Optional release tag, e.g. v0.5.0 or v1.0.0rc1")
    args = parser.parse_args()
    try:
        print(check_version(Path(__file__).resolve().parents[1], args.tag))
    except (OSError, ValueError, SyntaxError, KeyError) as error:
        print(f"Release check: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
