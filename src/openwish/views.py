"""Human-facing need → change → result projections, never a second ledger."""

from .model import change_tasks, estimate_tokens, needs_context, select_changes
from .storage import WishError, read_json
from .workflow import review_path, validate_review


def change_data(project, key):
    change = project["changes"][key]["meta"]
    tasks = change_tasks(project, key)
    review = "missing"
    path = review_path(project, key)
    if path.exists():
        try:
            if read_json(path).get("verdict") == "blocked":
                review = "blocked"
            else:
                validate_review(project, key, fresh=change["status"] != "closed")
                review = "historical" if change["status"] == "closed" else "fresh"
        except (OSError, WishError):
            review = "stale"
    return {**change, "done": sum(t["status"] == "done" for t in tasks), "tasks": len(tasks), "review": review}


def status_data(project):
    needs = [{**need["meta"], "changes": [cid for cid in select_changes(project, [key])
                                         if project["changes"][cid]["meta"]["status"] != "closed"]}
             for key, need in project["needs"].items()]
    return {"product": project["config"]["product"], "needs": needs,
            "changes": [change_data(project, key) for key in project["changes"]],
            "needs_tokens_estimate": estimate_tokens(needs_context(project))}


def summary(project, keys):
    lines = []
    for key in keys:
        if key in project["needs"]:
            need = project["needs"][key]["meta"]
            lines.extend([f"{key} — {need['title']} [{need['currency']}]", f"Outcome: {need['outcome']}", ""])
    for key in select_changes(project, keys):
        change = change_data(project, key)
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
