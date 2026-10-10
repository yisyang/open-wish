"""One disposable review per change, followed by explicit closure and cleanup."""

from datetime import datetime, timezone
import hashlib
import json

from .budgets import project_files
from .model import MODES, change_tasks, review_needs
from .storage import WishError, check_text, contained, document, read_json, write_json, write_text


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def require_change(project, key, *, active=True):
    if key not in project["changes"]:
        raise WishError(f"Unknown change: {key}")
    change = project["changes"][key]
    if active and change["meta"]["status"] == "closed":
        raise WishError(f"{key} is closed. Create a new change for further work, or clean this one.")
    return change


def review_path(project, key):
    return contained(project["root"], f"openwish/changes/{key}/review.json")


def source_fingerprint(project):
    records = {}
    for path in project_files(project["root"]):
        relative = path.relative_to(project["root"]).as_posix()
        if relative.startswith("openwish/"):
            continue
        with path.open("rb") as source:
            records[relative] = hashlib.file_digest(source, "sha256").hexdigest()
    return digest(records)


def review_fingerprint(project, key):
    """Protect a pending result from stale checks, without stage authorization gates."""
    change = project["changes"][key]
    policy = contained(project["root"], "openwish/policy.md")
    return digest({
        "change": {"meta": {k: v for k, v in change["meta"].items()
                             if k not in ("status", "closed_at", "closed_by")}, "body": change["body"]},
        "needs": {nid: {"meta": project["needs"][nid]["meta"], "body": project["needs"][nid]["body"]}
                  for nid in review_needs(project, key)},
        "tasks": change_tasks(project, key),
        "config": project["config"],
        "policy": policy.read_text(encoding="utf-8") if policy.exists() else "",
        "source": source_fingerprint(project),
    })


def change_update(change, **fields):
    meta = {**change["meta"], **fields}
    text = document(meta, change["body"])
    check_text(change["path"], text)
    return meta, text


def save_change(change, **fields):
    meta, text = change_update(change, **fields)
    write_text(change["path"], text)
    change["meta"] = meta


def set_mode(project, key, mode):
    change = require_change(project, key)
    if mode not in MODES:
        raise WishError(f"Unknown mode: {mode}")
    if mode != change["meta"]["mode"]:
        # The old review remains visible, but its fingerprint is now stale.
        save_change(change, mode=mode, status="in-progress")


def review_fields(summary, checks, needs, verdict):
    if not isinstance(summary, str) or not summary.strip():
        raise WishError("Provide a concise outcome summary.")
    if not isinstance(checks, list) or not checks or not all(isinstance(c, str) and c.strip() for c in checks):
        raise WishError("Provide direct verification results.")
    if not isinstance(needs, list) or not all(isinstance(n, str) and n for n in needs):
        raise WishError("Provide an array of reviewed need IDs.")
    if verdict not in ("pass", "blocked"):
        raise WishError("Review verdict must be pass or blocked.")


def record_review(project, key, summary, checks, needs, verdict="pass"):
    change = require_change(project, key)
    review_fields(summary, checks, needs, verdict)
    if set(needs).difference(project["needs"]):
        raise WishError("Review contains unknown need IDs.")
    if verdict == "pass":
        if any(task["status"] != "done" for task in change_tasks(project, key)):
            raise WishError("Unfinished work or manual verification remains; continue ready work before review.")
        missing = set(review_needs(project, key)).difference(needs)
        if missing:
            raise WishError("Assess these current/linked needs too: " + ", ".join(sorted(missing)))
    record = {"verdict": verdict, "summary": summary, "checks": checks, "needs": sorted(set(needs)),
              "fingerprint": review_fingerprint(project, key), "at": datetime.now(timezone.utc).isoformat()}
    status = "review" if verdict == "pass" else "in-progress"
    change_update(change, status=status)
    write_json(review_path(project, key), record)
    save_change(change, status=status)


def validate_review(project, key, *, fresh=True):
    review = read_json(review_path(project, key))
    review_fields(review.get("summary"), review.get("checks"), review.get("needs"), review.get("verdict"))
    if review["verdict"] != "pass" or any(task["status"] != "done" for task in change_tasks(project, key)):
        raise WishError("Review is not passing, or unfinished work/manual verification remains.")
    try:
        datetime.fromisoformat(review.get("at", ""))
    except (TypeError, ValueError) as error:
        raise WishError("Review needs a valid verification timestamp.") from error
    if fresh:
        if set(review_needs(project, key)).difference(review["needs"]):
            raise WishError("Review is missing current/linked needs.")
        if review.get("fingerprint") != review_fingerprint(project, key):
            raise WishError("Review is stale: needs, approach, tasks, policy, or repository files changed. "
                            "Refresh verification and AI review before closing.")
    return review


def close_changes(project, keys, by):
    if by not in ("human", "fast-forward"):
        raise WishError("Closure must be attributed to human or explicit fast-forward.")
    pending = []
    for key in dict.fromkeys(keys):
        change = require_change(project, key)
        if by == "fast-forward" and change["meta"]["mode"] != "fast-forward":
            raise WishError(f"{key}: fast-forward closure requires explicitly enabling this change's mode.")
        validate_review(project, key)
        meta, text = change_update(change, status="closed", closed_by=by,
                                   closed_at=datetime.now(timezone.utc).isoformat())
        pending.append((change, meta, text))
    for change, meta, text in pending:
        write_text(change["path"], text)
        change["meta"] = meta
    # Closing an increment does not establish that every linked need is fully
    # satisfied. Needs and confirmation dates are deliberately untouched.


def clean_changes(project, keys):
    """Preflight the full selection and remove only known files of closed changes."""
    pending = []
    for key in dict.fromkeys(keys):
        change = require_change(project, key, active=False)
        if change["meta"]["status"] != "closed":
            raise WishError(f"{key}: only closed changes can be disposed; review and close it first.")
        validate_review(project, key, fresh=False)
        directory = contained(project["root"], f"openwish/changes/{key}")
        paths = []
        for path in sorted(directory.iterdir()):
            path = contained(project["root"], path.relative_to(project["root"]))
            if path.name not in ("change.md", "tasks.json", "review.json") or not path.is_file():
                raise WishError(f"Unknown file preserved: {path}. Move useful knowledge before cleanup.")
            paths.append(path)
        pending.append((key, directory, paths))
    for key, directory, paths in pending:
        for path in paths:
            path.unlink()
        directory.rmdir()
        del project["changes"][key]
        project["tasks"] = [t for t in project["tasks"] if t["change"] != key]
    return [key for key, _, _ in pending]
