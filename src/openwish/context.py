"""Complete intent with an explicit, sized retrieval manifest and the state of selected work."""

from .budgets import check_budgets
from .model import estimate_tokens, needs_context, ready_tasks, review_needs, select_changes, unplanned_changes
from .validation import knowledge_warnings
from .views import change_rows, lazy_snapshot


def work_data(project, keys=()):
    """Changes, readiness and repository warnings in one call; readiness is not permission."""
    snapshot = lazy_snapshot(project)
    ready, waiting = ready_tasks(project, keys)
    warnings = list(snapshot()["warnings"]) + check_budgets(project, code=False)[1]
    if not snapshot()["warnings"]:
        warnings.extend(knowledge_warnings(project, snapshot()["files"]))
    return {"changes": change_rows(project, select_changes(project, keys), snapshot),
            "ready": [{"id": task["id"], "title": task["title"], "kind": task.get("kind", "agent"),
                       "status": task["status"]} for task in ready],
            "waiting": [{"id": task["id"], "title": task["title"], "kind": task.get("kind", "agent"),
                         "status": task["status"], "blocker": task["blocker"],
                         **({"ask": True} if task.get("ask") else {})} for task in waiting],
            "unplanned": unplanned_changes(project, keys), "warnings": warnings}


def context_data(project, keys=()):
    needs = needs_context(project)
    selected = select_changes(project, keys) if keys else []
    retrieve = {}

    def entry(path, category):
        relative = path.relative_to(project["root"]).as_posix()
        retrieve[relative] = {"path": relative, "category": category, "included": False,
                              "estimated_tokens": (len(path.read_bytes()) + 2) // 3}

    for key in selected:
        path = project["changes"][key]["path"]
        entry(path, "changes")
        entry(path.with_name("tasks.json"), "tasks")
    for key, need in project["needs"].items():
        if need["meta"]["currency"] == "current" or any(key in review_needs(project, cid) for cid in selected):
            if need["meta"]["currency"] != "current":
                entry(need["path"], "linked_retired_needs")
            for relative in need["meta"].get("references", []):
                entry(project["root"] / relative, "references")
    estimates = {"needs": estimate_tokens(needs)}
    for item in retrieve.values():
        category = item["category"]
        estimates[category] = estimates.get(category, 0) + item["estimated_tokens"]
    return {"needs": needs, "work": work_data(project, keys),
            "changes": [{"id": cid, "needs": project["changes"][cid]["meta"]["needs"],
                         "review_needs": review_needs(project, cid)} for cid in selected],
            "retrieve": list(retrieve.values()), "estimated_tokens": estimates,
            "estimated_loaded_and_retrievable_tokens": sum(estimates.values()),
            "note": "All current needs are included. Retrieve listed files for relevant rules and work; "
                    "their content is not included. Estimates exclude other source, conversation, and tool output."}
