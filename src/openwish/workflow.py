"""One disposable review per change, followed by explicit closure and cleanup."""

from datetime import datetime, timezone
import hashlib
import json

from .handoff import handoff_content, validate_handoff
from .model import MODES, TASK_STATES, change_tasks, review_needs
from .repository import project_files, repository_snapshot
from .storage import WishError, contained, document, read_json, write_json, write_text
from .trace import CHANGE_ID, text_files

SHOWN_PATHS = 8


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def require_change(project, key, *, active=True):
    if key not in project["changes"]:
        raise WishError(f"Unknown change: {key}")
    change = project["changes"][key]
    if active and change["meta"]["status"] == "closed":
        raise WishError(f"{key} is closed. Create a new change for further work, or clean this one.")
    return change


def review_path(project, key):
    return contained(project["root"], f"openwish/changes/{key}/review.json")


def source_inputs(project, snapshot=None):
    """Per-file digests of product content, so staleness can name what changed."""
    snapshot = snapshot or repository_snapshot(project["root"])
    files = {}
    for path in project_files(project["root"], snapshot):
        relative = path.relative_to(project["root"]).as_posix()
        if relative.startswith("openwish/"):
            continue
        with path.open("rb") as source:
            content = hashlib.file_digest(source, "sha256").hexdigest()[:16]
        executable = path.stat().st_mode & 0o111
        files[relative] = content + (f"+{executable:o}" if executable else "")
    return {"files": files, "components": digest(snapshot["components"])}


def review_inputs(project, key, *, snapshot=None, handoff=()):
    """Everything a pending result depends on; any difference makes the review stale."""
    change = project["changes"][key]
    policy = contained(project["root"], "openwish/policy.md")
    return {
        # Lifecycle and sequencing metadata do not change what was reviewed.
        "change": digest({"meta": {k: v for k, v in change["meta"].items()
                                   if k not in ("status", "closed_at", "closed_by", "after")},
                          "body": change["body"]}),
        # Open items do not bind, so recording a question leaves pending reviews fresh.
        "needs": {nid: digest({"meta": {k: v for k, v in project["needs"][nid]["meta"].items() if k != "open"},
                               "body": project["needs"][nid]["body"]})
                  for nid in review_needs(project, key)},
        "tasks": digest(change_tasks(project, key)),
        "handoff": digest(handoff),
        "destinations": handoff_content(project, handoff),
        "config": digest(project["config"]),
        "policy": digest(policy.read_text(encoding="utf-8") if policy.exists() else ""),
        "source": source_inputs(project, snapshot),
    }


def stale_reasons(recorded, current):
    """Explain a freshness difference in terms a reviewer can act on."""
    if not isinstance(recorded, dict):
        return ["review has no recorded inputs"]
    reasons = [label for name, label in (("change", "change purpose/approach/needs/mode"),
                                         ("tasks", "task definitions or evidence"),
                                         ("handoff", "handoff assessment"), ("config", "project config"),
                                         ("policy", "project policy"))
               if recorded.get(name) != current[name]]

    def keyed(label, before, after):
        before = before if isinstance(before, dict) else {}
        changed = [f"{k} modified" for k in sorted(before.keys() & after.keys()) if before[k] != after[k]]
        changed += [f"{k} added" for k in sorted(after.keys() - before.keys())]
        changed += [f"{k} removed" for k in sorted(before.keys() - after.keys())]
        if len(changed) > SHOWN_PATHS:
            changed = changed[:SHOWN_PATHS] + [f"{len(changed) - SHOWN_PATHS} more {label}"]
        return changed

    reasons += keyed("needs", recorded.get("needs"), current["needs"])
    reasons += keyed("destinations", recorded.get("destinations"), current["destinations"])
    source = recorded.get("source") if isinstance(recorded.get("source"), dict) else {}
    reasons += keyed("files", source.get("files"), current["source"]["files"])
    if source.get("components") != current["source"]["components"]:
        reasons.append("submodule revisions")
    # A product-file destination also appears among source files; report it once.
    return list(dict.fromkeys(reasons))


def change_update(change, **fields):
    meta = {**change["meta"], **fields}
    text = document(meta, change["body"])
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
        # The old review remains visible, but its inputs are now stale.
        save_change(change, mode=mode, status="in-progress")


def set_task(project, task_id, status, evidence=None):
    """Update one task in place; starting or reopening work marks the change in progress."""
    key = task_id.split("/", 1)[0]
    change = require_change(project, key)
    if status not in TASK_STATES:
        raise WishError(f"Unknown task status: {status}")
    path = contained(project["root"], f"openwish/changes/{key}/tasks.json")
    data = read_json(path)
    tasks = {task.get("id"): task for task in data["tasks"]}
    if task_id not in tasks:
        raise WishError(f"Unknown task: {task_id}")
    task = tasks[task_id]
    task["status"] = status
    if evidence is not None:
        task["evidence"] = evidence
    if status == "done":
        if not isinstance(task.get("evidence"), str) or not task["evidence"].strip():
            raise WishError("Completed tasks need direct evidence (--evidence).")
        unfinished = [dep for dep in task.get("depends_on", []) if tasks.get(dep, {}).get("status") != "done"]
        if unfinished:
            raise WishError(f"{task_id}: prerequisites are unfinished: " + ", ".join(unfinished))
    write_json(path, data)
    if change["meta"]["status"] in ("open", "review"):
        save_change(change, status="in-progress")


def review_fields(summary, checks, affected, unaffected, verdict):
    if not isinstance(summary, str) or not summary.strip():
        raise WishError("Provide a concise outcome summary.")
    if not isinstance(checks, list) or not checks or not all(isinstance(c, str) and c.strip() for c in checks):
        raise WishError("Provide direct verification results.")
    for value in (affected, unaffected):
        if not isinstance(value, list) or not all(isinstance(n, str) and n for n in value):
            raise WishError("Provide arrays of affected and unaffected need IDs.")
    if verdict not in ("pass", "blocked"):
        raise WishError("Review verdict must be pass or blocked.")


def record_review(project, key, summary, checks, affected=(), verdict="pass", *, handoff=None):
    """Record the latest result. Linked needs are always affected; every other current
    need is recorded as assessed and unaffected, which the reviewer must actually judge."""
    change = require_change(project, key)
    affected = sorted(set(change["meta"]["needs"]) | set(affected))
    unknown = set(affected).difference(project["needs"])
    if unknown:
        raise WishError("Review names unknown need IDs: " + ", ".join(sorted(unknown)))
    unaffected = sorted(set(review_needs(project, key)).difference(affected))
    review_fields(summary, checks, affected, unaffected, verdict)
    if verdict == "pass" and any(task["status"] != "done" for task in change_tasks(project, key)):
        raise WishError("Unfinished work or manual verification remains; continue ready work before review.")
    handoff = [] if handoff is None else handoff
    snapshot = repository_snapshot(project["root"]) if verdict == "pass" else None
    validate_handoff(project, key, handoff, passing=verdict == "pass", destinations=verdict == "pass",
                     snapshot=snapshot)
    record = {"verdict": verdict, "summary": summary, "checks": checks,
              "affected": affected, "unaffected": unaffected, "handoff": handoff,
              "inputs": review_inputs(project, key, snapshot=snapshot, handoff=handoff) if verdict == "pass" else None,
              "at": datetime.now(timezone.utc).isoformat()}
    write_json(review_path(project, key), record)
    save_change(change, status="review" if verdict == "pass" else "in-progress")
    return record


def validate_review(project, key, *, fresh=True, snapshot=None):
    review = read_json(review_path(project, key))
    review_fields(review.get("summary"), review.get("checks"), review.get("affected"),
                  review.get("unaffected"), review.get("verdict"))
    if review["verdict"] != "pass" or any(task["status"] != "done" for task in change_tasks(project, key)):
        raise WishError("Review is not passing, or unfinished work/manual verification remains.")
    try:
        datetime.fromisoformat(review.get("at", ""))
    except (TypeError, ValueError) as error:
        raise WishError("Review needs a valid verification timestamp.") from error
    if not fresh:
        validate_handoff(project, key, review.get("handoff"), destinations=False)
        return review
    snapshot = snapshot or repository_snapshot(project["root"])
    validate_handoff(project, key, review.get("handoff"), snapshot=snapshot)
    missing = set(review_needs(project, key)).difference(review["affected"] + review["unaffected"])
    if missing:
        raise WishError("Review is missing current/linked needs: " + ", ".join(sorted(missing)))
    reasons = stale_reasons(review.get("inputs"), review_inputs(project, key, snapshot=snapshot,
                                                                 handoff=review["handoff"]))
    if reasons:
        raise WishError("Review is stale; refresh affected verification and review before closing. "
                        "Changed: " + "; ".join(reasons))
    return review


def close_changes(project, keys, by):
    if by not in ("human", "fast-forward"):
        raise WishError("Closure must be attributed to human or explicit fast-forward.")
    pending = []
    snapshot = None
    keys = list(dict.fromkeys(keys))
    for key in keys:
        change = require_change(project, key)
        # Acceptance follows the sequence, so nothing is accepted on top of unaccepted work.
        unaccepted = [dep for dep in change["meta"].get("after", [])
                      if project["changes"][dep]["meta"]["status"] != "closed" and dep not in keys]
        if unaccepted:
            raise WishError(f"{key}: close its predecessors first, or in the same batch: {', '.join(unaccepted)}")
        if by == "fast-forward" and change["meta"]["mode"] != "fast-forward":
            raise WishError(f"{key}: fast-forward closure requires explicitly enabling this change's mode.")
        snapshot = snapshot or repository_snapshot(project["root"])
        validate_review(project, key, snapshot=snapshot)
        meta, text = change_update(change, status="closed", closed_by=by,
                                   closed_at=datetime.now(timezone.utc).isoformat())
        pending.append((change, meta, text))
    for change, meta, text in pending:
        write_text(change["path"], text)
        change["meta"] = meta
    # Closing an increment does not establish that every linked need is fully
    # satisfied. Needs and confirmation dates are deliberately untouched.


def cleanup_plan(project, keys):
    """Validate the full batch, retained handoffs, and incoming references before deletion."""
    keys = list(dict.fromkeys(keys))
    snapshot = repository_snapshot(project["root"])
    pending = []
    handoffs = {}
    for key in keys:
        change = require_change(project, key, active=False)
        if change["meta"]["status"] != "closed":
            raise WishError(f"{key}: only closed changes can be disposed; review and close it first.")
        review = validate_review(project, key, fresh=False)
        validate_handoff(project, key, review["handoff"], removing=keys, snapshot=snapshot)
        handoffs[key] = review["handoff"]
        directory = contained(project["root"], f"openwish/changes/{key}")
        paths = []
        for path in sorted(directory.iterdir()):
            path = contained(project["root"], path.relative_to(project["root"]))
            if path.name not in ("change.md", "tasks.json", "review.json") or not path.is_file():
                raise WishError(f"Unknown file preserved: {path}. Move useful knowledge before cleanup.")
            paths.append(path)
        pending.append((key, directory, paths))
    # Managed records remain authoritative even when a project ignores disposable work.
    for key in project["changes"].keys() - set(keys):
        path = review_path(project, key)
        if not path.exists():
            continue
        assessment = read_json(path).get("handoff", [])
        validate_handoff(project, key, assessment, passing=False, destinations=False)
        for item in assessment:
            for relative in item["destinations"]:
                if any(relative.startswith(f"openwish/changes/{target}/") for target in keys):
                    raise WishError(f"Retained handoff in {path.relative_to(project['root'])} depends on {relative}; reconcile before cleanup")
    successors = {key: [dep for dep in change["meta"].get("after", []) if dep in keys]
                  for key, change in project["changes"].items() if key not in keys}
    successors = {key: deps for key, deps in successors.items() if deps}
    warnings = []
    for relative, text in text_files(project, project_files(project["root"], snapshot), managed=True):
        if any(relative.startswith(f"openwish/changes/{key}/") for key in keys):
            continue
        owner = relative.removeprefix("openwish/changes/").removesuffix("/change.md")
        if owner in successors and relative == f"openwish/changes/{owner}/change.md":
            text = project["changes"][owner]["body"]  # its `after` entries are rewritten below
        mentioned = sorted(set(keys).intersection(CHANGE_ID.findall(text)))
        if mentioned:
            warnings.append(f"Retained reference to {', '.join(mentioned)} in {relative}; reconcile if needed")
    return pending, {"changes": keys, "remove": [p.relative_to(project["root"]).as_posix()
                                               for _, _, paths in pending for p in paths],
                     "handoff": handoffs, "successors": successors, "warnings": warnings}


def clean_changes(project, keys, *, dry_run=False):
    """Preview or dispose a preflighted batch; retained destinations survive the batch."""
    pending, report = cleanup_plan(project, keys)
    if dry_run:
        return report
    for key, removed in report["successors"].items():
        change = project["changes"][key]
        meta = {k: v for k, v in change["meta"].items() if k != "after"}
        remaining = [dep for dep in change["meta"]["after"] if dep not in removed]
        meta |= {"after": remaining} if remaining else {}
        write_text(change["path"], document(meta, change["body"]))
        change["meta"] = meta
    for key, directory, paths in pending:
        for path in paths:
            path.unlink()
        directory.rmdir()
        del project["changes"][key]
        project["tasks"] = [t for t in project["tasks"] if t["change"] != key]
    return report
