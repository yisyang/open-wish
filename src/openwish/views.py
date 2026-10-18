"""Human-facing need → change → result projections, never a second ledger."""

from functools import cache

from .handoff import validate_handoff
from .model import change_tasks, estimate_tokens, needs_context, retention_data, select_changes
from .repository import pin_mismatches, repository_snapshot
from .storage import WishError, read_json
from .workflow import review_path, validate_review


def change_data(project, key, *, snapshot=None):
    change = project["changes"][key]["meta"]
    tasks = change_tasks(project, key)
    review, reason = "missing", ""
    path = review_path(project, key)
    if path.exists():
        try:
            if read_json(path).get("verdict") == "blocked":
                review = "blocked"
            else:
                active = change["status"] != "closed"
                validate_review(project, key, fresh=active,
                                snapshot=snapshot() if active and snapshot is not None else None)
                review = "fresh" if active else "historical"
        except (OSError, WishError) as error:
            review, reason = "stale", str(error)
    return {**change, "done": sum(t["status"] == "done" for t in tasks), "tasks": len(tasks),
            "review": review, **({"review_issue": reason} if reason else {})}


def lazy_snapshot(project):
    # One repository snapshot per projection, never reused across commands.
    return cache(lambda: repository_snapshot(project["root"]))


def change_rows(project, keys, snapshot=None):
    snapshot = snapshot or lazy_snapshot(project)
    return [change_data(project, key, snapshot=snapshot) for key in keys]


def status_data(project):
    by_need = {key: [] for key in project["needs"]}
    for key, change in project["changes"].items():
        if change["meta"]["status"] != "closed":
            for need in change["meta"]["needs"]:
                by_need[need].append(key)
    needs = [{**need["meta"], "changes": by_need[key]}
             for key, need in project["needs"].items()]
    snapshot = lazy_snapshot(project)
    return {"product": project["config"]["product"], "needs": needs,
            "changes": change_rows(project, project["changes"], snapshot), "retention": retention_data(project),
            "needs_tokens_estimate": estimate_tokens(needs_context(project)),
            "repository_warnings": snapshot()["warnings"]}


def summary(project, keys):
    lines = []
    snapshot = lazy_snapshot(project)
    for key in keys:
        if key in project["needs"]:
            need = project["needs"][key]["meta"]
            lines.extend([f"{key} — {need['title']} [{need['currency']}]", f"Outcome: {need['outcome']}", ""])
    for change in change_rows(project, select_changes(project, keys), snapshot):
        key = change["id"]
        lines.append(f"{key} — {change['title']} [{change['status']}]")
        for nid in change["needs"]:
            need = project["needs"][nid]["meta"]
            lines.append(f"Need: {nid} — {need['title']}; outcome: {need['outcome']}")
        lines.append(f"Work: {change['done']}/{change['tasks']} tasks complete; review: {change['review']}")
        path = review_path(project, key)
        if path.exists():
            review = read_json(path)
            lines.append(f"Result: {review.get('summary', '')}")
            if isinstance(review.get("affected"), list) and isinstance(review.get("unaffected"), list):
                lines.append("Needs affected: " + (", ".join(review["affected"]) or "none")
                             + "; assessed unaffected: " + (", ".join(review["unaffected"]) or "none"))
            try:
                assessment = review.get("handoff", [])
                validate_handoff(project, key, assessment, passing=False, destinations=False)
                for item in assessment:
                    lines.append(f"Handoff ({item['disposition']}): {item['requirement']} → "
                                 + ", ".join(item["destinations"]))
            except WishError as error:
                lines.append(f"Invalid handoff: {error}")
            if change["review"] in ("fresh", "historical"):
                label = "Historical check" if change["status"] == "closed" else "Verified"
                lines.extend(f"{label}: {check}" for check in review["checks"])
            else:
                lines.append(change.get("review_issue") or "Resolve findings and refresh verification before closure.")
        if change["status"] == "closed":
            after = (" once the human has responded to the result" if change["closed_by"] == "fast-forward" else "")
            lines.append(f"Closed by {change['closed_by']} at {change['closed_at']}; eligible for cleanup{after}.")
        else:
            lines.extend("WARN " + warning for warning in pin_mismatches(snapshot()))
        lines.append("")
    return "\n".join(lines)
