"""Pure projections and local task scheduling for durable needs and changes."""

import json
import math

from .storage import WishError

CURRENCY = ("current", "retired")
CHANGE_STATES = ("open", "in-progress", "review", "closed")
TASK_STATES = ("open", "in-progress", "blocked", "done")
MODES = ("default", "fast-forward")


def select_needs(project, keys):
    keys = [keys] if isinstance(keys, str) else list(keys)
    if not keys:
        raise WishError("Select at least one need ID.")
    for key in keys:
        if key not in project["needs"]:
            raise WishError(f"Unknown need: {key}")
    return sorted(set(keys))


def select_changes(project, keys):
    """Accept changes or needs as a convenience; an empty selection means all."""
    keys = [keys] if isinstance(keys, str) else list(keys)
    if not keys:
        return sorted(project["changes"])
    selected = set()
    for key in keys:
        if key in project["changes"]:
            selected.add(key)
        elif key in project["needs"]:
            selected.update(cid for cid, change in project["changes"].items()
                            if key in change["meta"]["needs"])
        else:
            raise WishError(f"Unknown need or change: {key}")
    return sorted(selected)


def change_tasks(project, key):
    return [task for task in project["tasks"] if task["change"] == key]


def review_needs(project, key):
    """All current intent constrains a change, including needs outside its purpose."""
    return sorted(set(project["changes"][key]["meta"]["needs"]) |
                  {nid for nid, need in project["needs"].items()
                   if need["meta"]["currency"] == "current"})


def needs_context(project):
    lines = ["# Current needs (binding after delivery)", ""]
    for key, need in sorted(project["needs"].items()):
        meta = need["meta"]
        if meta.get("currency") != "current":
            continue
        lines.extend([
            f"## {key}: {meta.get('title', '')}",
            f"Actor: {meta.get('actor', '')}",
            f"Outcome: {meta.get('outcome', '')}",
            f"Acceptance: {json.dumps(meta.get('acceptance', []), ensure_ascii=False)}",
            f"Confirmed: {meta.get('confirmed_at') or 'unconfirmed'}",
        ])
        extra = {name: value for name, value in meta.items() if name not in
                 {"id", "title", "currency", "actor", "outcome", "acceptance", "confirmed_at"}}
        if extra:
            lines.append("Additional intent: " + json.dumps(extra, ensure_ascii=False))
        if need["body"]:
            lines.append(need["body"])
        lines.append("")
    return "\n".join(lines)


def estimate_tokens(text):
    """Conservative budgeting heuristic, not a model-specific tokenizer."""
    return math.ceil(len(text.encode("utf-8")) / 3)


def topological_order(nodes):
    remaining = {key: set(deps) for key, deps in nodes.items()}
    ordered = []
    while remaining:
        ready = sorted(key for key, deps in remaining.items() if not deps)
        if not ready:
            raise WishError("Dependency cycle or missing prerequisite: " + ", ".join(sorted(remaining)))
        ordered.extend(ready)
        remaining = {key: deps.difference(ready) for key, deps in remaining.items() if key not in ready}
    return ordered


def ready_tasks(project, keys=()):
    """List readiness, not permission. Conversation authority belongs to the harness."""
    selected = set(select_changes(project, keys))
    tasks = {task["id"]: task for task in project["tasks"]}
    ready, waiting = [], []
    for task in project["tasks"]:
        change = project["changes"][task["change"]]["meta"]
        if task["change"] not in selected or change["status"] == "closed" or task["status"] == "done":
            continue
        needs = [{"id": nid, "title": project["needs"][nid]["meta"]["title"],
                  "outcome": project["needs"][nid]["meta"]["outcome"]} for nid in change["needs"]]
        item = {**task, "needs": needs}
        unfinished = [dep for dep in task.get("depends_on", []) if tasks[dep]["status"] != "done"]
        if unfinished:
            item["blocker"] = "Unfinished prerequisites: " + ", ".join(unfinished)
        elif task.get("kind", "agent") == "manual":
            item["blocker"] = "Manual observation required"
        elif task["status"] == "blocked":
            item["blocker"] = task.get("evidence") or "Resolve the task's blocker"
        (waiting if "blocker" in item else ready).append(item)
    return ready, waiting
