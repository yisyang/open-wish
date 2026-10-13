"""Need and change mentions derived from repository files; code stays the record."""

from pathlib import PurePosixPath
import re

from .budgets import CODE_SUFFIXES
from .model import select_needs
from .storage import read_json

NEED_ID = re.compile(r"\bN-[0-9]{3,}\b")
CHANGE_ID = re.compile(r"\bC-[0-9]{3,}\b")
DOC_SUFFIXES = {".md", ".markdown", ".rst", ".txt", ".adoc"}
RECORD_SUFFIXES = {".json", ".toml", ".yaml", ".yml"}
CHECK_DIRECTORIES = {"test", "tests", "spec", "specs", "__tests__", "e2e"}
MAX_BYTES = 2_000_000


def is_check(relative):
    """Recognize conventional test locations across languages."""
    path = PurePosixPath(relative)
    name = path.name.lower()
    return (bool(CHECK_DIRECTORIES.intersection(part.lower() for part in path.parts[:-1]))
            or name.startswith("test_") or path.stem.lower().endswith(("_test", "_spec"))
            or ".test." in name or ".spec." in name)


def installed_guidance(project):
    guidance = {"openwish/policy.md", "openwish/artifacts.md", "openwish/installation.json"}
    manifest = project["root"] / "openwish/installation.json"
    if manifest.exists():
        guidance.update(read_json(manifest).get("files", {}))
    return guidance


def text_files(project, files, *, managed=False):
    """Yield (relative path, text) for code and prose; installed OW guidance is excluded."""
    guidance = installed_guidance(project)
    suffixes = CODE_SUFFIXES | DOC_SUFFIXES | (RECORD_SUFFIXES if managed else set())
    for path in files:
        relative = path.relative_to(project["root"]).as_posix()
        if (relative in guidance or path.suffix not in suffixes
                or (not managed and relative.startswith("openwish/"))):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            yield relative, path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue


def mentions(project, files):
    """Map product files to the need and change IDs they mention."""
    found = {}
    for relative, text in text_files(project, files):
        needs, changes = set(NEED_ID.findall(text)), set(CHANGE_ID.findall(text))
        if needs or changes:
            found[relative] = {"needs": needs, "changes": changes}
    return found


def trace_data(project, files, keys=()):
    """Derive need → check/file links on demand; absence never proves a need is unprotected."""
    found = mentions(project, files)
    selected = select_needs(project, keys) if keys else sorted(project["needs"])
    needs = []
    for key in selected:
        cited = sorted(relative for relative, ids in found.items() if key in ids["needs"])
        needs.append({"id": key, "title": project["needs"][key]["meta"]["title"],
                      "currency": project["needs"][key]["meta"]["currency"],
                      "checks": [relative for relative in cited if is_check(relative)],
                      "files": [relative for relative in cited if not is_check(relative)]})
    changes = {relative: sorted(ids["changes"]) for relative, ids in sorted(found.items()) if ids["changes"]}
    return {"needs": needs,
            "untraced_current": [need["id"] for need in needs
                                 if need["currency"] == "current" and not need["checks"]],
            "change_mentions": changes,
            "warnings": reference_warnings(project, found),
            "note": "Derived from need IDs mentioned in code, tests and docs. Missing traces do not "
                    "prove a need is unprotected; all current needs remain binding."}


def reference_warnings(project, found):
    warnings = []
    for relative, ids in sorted(found.items()):
        for key in sorted(ids["needs"]):
            if key not in project["needs"]:
                warnings.append(f"{relative}: mentions unknown need {key}")
            elif project["needs"][key]["meta"].get("currency") == "retired":
                warnings.append(f"{relative}: mentions retired need {key}; point to current intent")
    return warnings
