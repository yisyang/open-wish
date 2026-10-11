"""Human-facing need → change → result projections, never a second ledger."""

from functools import cache

from .model import change_tasks, estimate_tokens, needs_context, retention_data, select_changes
from .storage import WishError, read_json
from .workflow import review_path, source_fingerprint, validate_review


def change_data(project, key, *, snapshot=None):
    change = project["changes"][key]["meta"]
    tasks = change_tasks(project, key)
    review = "missing"
    path = review_path(project, key)
    if path.exists():
        try:
            if read_json(path).get("verdict") == "blocked":
                review = "blocked"
            else:
                active = change["status"] != "closed"
                source = snapshot() if active and snapshot is not None else None
                validate_review(project, key, fresh=active, source=source)
                review = "historical" if change["status"] == "closed" else "fresh"
        except (OSError, WishError):
            review = "stale"
    return {**change, "done": sum(t["status"] == "done" for t in tasks), "tasks": len(tasks), "review": review}


def change_rows(project, keys):
    # One lazy filesystem snapshot per projection, never reused across commands.
    @cache
    def snapshot():
        return source_fingerprint(project)

    return [change_data(project, key, snapshot=snapshot) for key in keys]


def status_data(project):
    by_need = {key: [] for key in project["needs"]}
    for key, change in project["changes"].items():
        if change["meta"]["status"] != "closed":
            for need in change["meta"]["needs"]:
                by_need[need].append(key)
    needs = [{**need["meta"], "changes": by_need[key]}
             for key, need in project["needs"].items()]
    return {"product": project["config"]["product"], "needs": needs,
            "changes": change_rows(project, project["changes"]), "retention": retention_data(project),
            "needs_tokens_estimate": estimate_tokens(needs_context(project))}


def summary(project, keys):
    lines = []
    for key in keys:
        if key in project["needs"]:
            need = project["needs"][key]["meta"]
            lines.extend([f"{key} — {need['title']} [{need['currency']}]", f"Outcome: {need['outcome']}", ""])
    for change in change_rows(project, select_changes(project, keys)):
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
            if change["review"] in ("fresh", "historical"):
                label = "Historical check" if change["status"] == "closed" else "Verified"
                lines.extend(f"{label}: {check}" for check in review["checks"])
            else:
                lines.append("Resolve findings and refresh verification before closure.")
        if change["status"] == "closed":
            lines.append(f"Closed by {change['closed_by']} at {change['closed_at']}; eligible for cleanup.")
        lines.append("")
    return "\n".join(lines)
