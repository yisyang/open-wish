"""Pure projections and local task scheduling for durable needs and changes."""

import json
import math

from .storage import WishError

CURRENCY = ("current", "retired")
CHANGE_STATES = ("open", "in-progress", "review", "closed")
TASK_STATES = ("open", "in-progress", "blocked", "done")
MODES = ("default", "fast-forward")
RELATIONS = ("requires", "constrains")
# What lets a change's `after` successors start: a passing review, or human/delegated closure.
SEQUENCE_GATES = ("review", "acceptance")
# Investigation ends in findings and a decision or proposal, never delivered behavior, so it may
# run before its change's predecessors pass: learning late is what sequencing would otherwise cost.
TASK_KINDS = ("agent", "manual", "investigate")


def need_graph(project, keys=()):
    """Derive a sparse intent graph once from a validated snapshot; never a ledger.

    A selection returns incident edges and their endpoints, not a claim of complete
    impact or transitive execution order. Retirement remains visible on nodes.
    """
    selected = set(select_needs(project, keys)) if keys else set(project["needs"])
    edges = [{"source": key, "target": relation["need"], "kind": relation["kind"],
              "reason": relation["reason"]}
             for key, need in sorted(project["needs"].items())
             for relation in need["meta"].get("relations", [])
             if key in selected or relation["need"] in selected]
    included = selected | {edge[end] for edge in edges for end in ("source", "target")}
    nodes = [{"id": key, "title": project["needs"][key]["meta"]["title"],
              "currency": project["needs"][key]["meta"]["currency"]} for key in sorted(included)]
    return {"needs": nodes, "relations": sorted(edges, key=lambda e: (e["source"], e["kind"], e["target"]))}


def retention_data(project):
    """Expose retained work without guessing abandonment or supplying authority."""
    blocked = {task["change"] for task in project["tasks"]
               if task["status"] == "blocked" or (task.get("kind") == "manual" and task["status"] != "done")}
    return {
        "cleanup_candidates": [key for key, change in project["changes"].items()
                               if change["meta"]["status"] == "closed"],
        "awaiting_acceptance": [key for key, change in project["changes"].items()
                                if change["meta"]["status"] == "review"],
        "blocked_changes": sorted(blocked),
        "retired_needs": [key for key, need in project["needs"].items()
                          if need["meta"]["currency"] == "retired"],
    }


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
                 {"id", "title", "currency", "actor", "outcome", "acceptance", "confirmed_at", "open"}}
        if extra:
            lines.append("Additional intent: " + json.dumps(extra, ensure_ascii=False))
        if meta.get("open"):
            lines.append("Open (not binding): " + json.dumps(meta["open"], ensure_ascii=False))
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


def change_sequence(project):
    """Changes in `after` order; independent changes keep ID order."""
    return topological_order({key: change["meta"].get("after", [])
                              for key, change in project["changes"].items()})


def waiting_on(project, key):
    """Predecessors that do not yet satisfy the project's sequence gate."""
    gate = project["config"].get("successors_wait_for", "review")
    satisfied = ("closed",) if gate == "acceptance" else ("review", "closed")
    return [f"{dep} ({project['changes'][dep]['meta']['status']})"
            for dep in project["changes"][key]["meta"].get("after", [])
            if project["changes"][dep]["meta"]["status"] not in satisfied]


def delivery_tasks(project, key):
    return [task for task in change_tasks(project, key) if task.get("kind", "agent") != "investigate"]


def unplanned_changes(project, keys=()):
    """Active changes without delivery tasks; investigations alone do not plan a change.
    Whether their prerequisites exist is still a code question."""
    selected = set(select_changes(project, keys))
    return [{"id": key, "title": project["changes"][key]["meta"]["title"],
             "needs": project["changes"][key]["meta"]["needs"], "waiting_on": waiting_on(project, key)}
            for key in change_sequence(project)
            if key in selected and project["changes"][key]["meta"]["status"] in ("open", "in-progress")
            and not delivery_tasks(project, key)]


def ready_tasks(project, keys=()):
    """List readiness, not permission. Conversation authority belongs to the harness."""
    selected = set(select_changes(project, keys))
    tasks = {task["id"]: task for task in project["tasks"]}
    position = {key: index for index, key in enumerate(change_sequence(project))}
    ready, waiting = [], []
    for task in sorted(project["tasks"], key=lambda task: position[task["change"]]):
        change = project["changes"][task["change"]]["meta"]
        if task["change"] not in selected or change["status"] == "closed" or task["status"] == "done":
            continue
        needs = [{"id": nid, "title": project["needs"][nid]["meta"]["title"],
                  "outcome": project["needs"][nid]["meta"]["outcome"]} for nid in change["needs"]]
        item = {**task, "needs": needs}
        unfinished = [dep for dep in task.get("depends_on", []) if tasks[dep]["status"] != "done"]
        kind = task.get("kind", "agent")
        predecessors = [] if kind == "investigate" else waiting_on(project, task["change"])
        if predecessors:
            item["blocker"] = "Change waits for " + ", ".join(predecessors)
        elif unfinished:
            item["blocker"] = "Unfinished prerequisites: " + ", ".join(unfinished)
        elif kind == "manual":
            item["blocker"] = "Manual observation required"
        elif task["status"] == "blocked":
            item["blocker"] = task.get("evidence") or "Resolve the task's blocker"
            if kind == "investigate":
                item["ask"] = True  # a question awaiting a human, batched with the others
        (waiting if "blocker" in item else ready).append(item)
    return ready, waiting
