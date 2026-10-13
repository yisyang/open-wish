"""Disposable requirement-to-result assessments and retained destination checks."""

import hashlib

from .repository import project_files
from .storage import WishError, repository_file

DISPOSITIONS = {"implemented", "retained", "deferred", "superseded", "unresolved"}


def validate_handoff(project, key, assessment, *, passing=True, destinations=True, removing=(), snapshot=None):
    if not isinstance(assessment, list) or (passing and not assessment):
        raise WishError("A passing review needs a nonempty handoff assessment of material requirements "
                        "(--handoff FILE, or - for stdin).")
    visible = set(project_files(project["root"], snapshot)) if destinations and assessment else set()
    excluded = {key, *removing}
    for item in assessment:
        if (not isinstance(item, dict) or set(item) != {"requirement", "disposition", "destinations", "evidence"}
                or not isinstance(item["requirement"], str) or not item["requirement"].strip()
                or not isinstance(item["evidence"], str) or not item["evidence"].strip()
                or not isinstance(item["disposition"], str) or item["disposition"] not in DISPOSITIONS
                or not isinstance(item["destinations"], list)
                or not all(isinstance(p, str) and p.strip() for p in item["destinations"])):
            raise WishError("Each handoff item needs requirement, disposition, destinations (file paths), and evidence.")
        disposition = item["disposition"]
        if passing and disposition == "unresolved":
            raise WishError("Unresolved handoff obligations prevent a passing review.")
        if disposition != "unresolved" and not item["destinations"]:
            raise WishError("Resolved handoff obligations need retained destination files.")
        if not destinations:
            continue
        for relative in item["destinations"]:
            path = repository_file(project["root"], relative)
            if path not in visible:
                raise WishError(f"Handoff destination is ignored or excluded from repository inspection: {relative}")
            parts = path.relative_to(project["root"]).parts
            if parts[:2] == ("openwish", "changes"):
                target = parts[2]
                if target in excluded:
                    raise WishError(f"Handoff destination would be disposed: {relative}")
                if disposition != "deferred" or target not in project["changes"]:
                    raise WishError(f"Only deferred work may target another retained change: {relative}")
                if project["changes"][target]["meta"]["status"] == "closed":
                    raise WishError(f"Deferred work must reference active work or its delivered repository files: {relative}")
            elif disposition == "implemented" and parts[0] == "openwish":
                raise WishError(f"Implemented behavior needs product files, not OW records: {relative}")


def handoff_content(project, assessment):
    """Include cited future work in freshness without fingerprinting every other plan."""
    content = {}
    for relative in sorted({p for item in assessment for p in item["destinations"]}):
        with repository_file(project["root"], relative).open("rb") as source:
            content[relative] = hashlib.file_digest(source, "sha256").hexdigest()[:16]
    return content
