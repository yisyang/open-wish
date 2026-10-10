"""Pure graph, context, and task scheduling operations."""

import json
import math

from .storage import WishError

IMPLEMENTATION = ("open", "in-progress", "review", "approved")
CURRENCY = ("current", "retired")
TASK_STATES = ("open", "in-progress", "blocked", "done")
GATES = ("needs", "align", "implement", "review")


def select_needs(project, keys):
    keys = [keys] if isinstance(keys, str) else list(keys)
    if not keys:
        raise WishError("Select at least one need ID.")
    for key in keys:
        if key not in project["needs"]:
            raise WishError(f"Unknown need: {key}")
    return sorted(set(keys))


def spec_needs(project, spec):
    return project["specs"][spec]["design"]["meta"]["needs"]


def direct_specs(project, keys):
    return sorted(key for key in project["specs"] if set(keys).intersection(spec_needs(project, key)))


def epic_needs(project, key):
    """Execution scope can be narrower than the specs' regression coverage."""
    meta = project["epics"][key]["meta"]
    if "needs" in meta:
        return meta["needs"]
    # Older epics retain their original scope until deliberately narrowed.
    return sorted({nid for sid in meta["specs"] for nid in spec_needs(project, sid)})


def need_scope(project, keys):
    """Derive execution work from needs; no separate work container is persisted."""
    keys = select_needs(project, keys)
    specs = direct_specs(project, keys)
    epics = sorted(key for key in project["epics"]
                   if set(keys).intersection(epic_needs(project, key)))
    return {"needs": keys, "specs": specs, "epics": epics}


def connected_specs(project, keys):
    """Include execution contracts and their prerequisites/consumers for review."""
    scope = need_scope(project, keys)
    affected = set(scope["specs"])
    for eid in scope["epics"]:
        affected.update(project["epics"][eid]["meta"]["specs"])
    edges = {}
    for key, spec in project["specs"].items():
        meta = spec["meta"]
        links = set(meta.get("depends_on", []))
        if meta.get("parent"):
            links.add(meta["parent"])
        edges[key] = links
    while True:
        expanded = affected | {link for key in affected for link in edges.get(key, [])}
        expanded |= {key for key, links in edges.items() if links.intersection(affected)}
        if expanded == affected:
            return sorted(affected)
        affected = expanded


def needs_context(project):
    """A live projection: spec links and statuses are never copied into needs."""
    lines = ["# Current needs (including previously approved needs)", ""]
    for key, need in sorted(project["needs"].items()):
        meta = need["meta"]
        if meta.get("currency") != "current":
            continue
        specs = [f"{sid} ({s['meta'].get('implementation', 'open')})"
                 for sid, s in sorted(project["specs"].items())
                 if key in spec_needs(project, sid)]
        lines.extend([
            f"## {key}: {meta.get('title', '')}",
            f"Currency: current; implementation: {meta.get('implementation', 'open')}",
            f"Actor: {meta.get('actor', '')}",
            f"Outcome: {meta.get('outcome', '')}",
            f"Acceptance: {json.dumps(meta.get('acceptance', []), ensure_ascii=False)}",
            f"Confirmed: {meta.get('confirmed_at') or 'unconfirmed'}; "
            f"verified: {meta.get('verified_at') or 'unverified'}",
            f"Specs: {', '.join(specs) or 'none'}",
        ])
        if need["body"]:
            lines.append(need["body"])
        lines.append("")
    return "\n".join(lines)


def estimate_tokens(text):
    """Conservative budgeting heuristic, not a model-specific tokenizer."""
    return math.ceil(len(text.encode("utf-8")) / 3)


def topological_order(nodes):
    """Deterministic Kahn traversal; references are validated separately."""
    remaining = {key: set(deps) for key, deps in nodes.items()}
    ordered = []
    while remaining:
        ready = sorted(key for key, deps in remaining.items() if not deps)
        if not ready:
            raise WishError("Dependency cycle or missing prerequisite: " + ", ".join(sorted(remaining)))
        ordered.extend(ready)
        remaining = {key: deps.difference(ready) for key, deps in remaining.items() if key not in ready}
    return ordered


def task_key(task):
    return task["group"], task["order"], task["id"]


def task_lineage(project, task):
    return [{"id": key, "title": project["specs"][key]["meta"]["title"],
             "needs": [{"id": nid, "title": project["needs"][nid]["meta"]["title"],
                        "outcome": project["needs"][nid]["meta"]["outcome"]}
                       for nid in spec_needs(project, key)]}
            for key in project["epics"][task["epic"]]["meta"]["specs"]]


def ready_tasks(project, keys):
    tasks = {task["id"]: task for task in project["tasks"]}
    scope = set(need_scope(project, keys)["epics"])
    ready, waiting = [], []
    for task in sorted(project["tasks"], key=task_key):
        if task["epic"] not in scope or task["status"] == "done":
            continue
        dependencies_done = all(tasks[dep]["status"] == "done" for dep in task["depends_on"])
        item = {**task, "lineage": task_lineage(project, task),
                "execution_needs": epic_needs(project, task["epic"])}
        if task["kind"] == "agent" and dependencies_done and task["status"] != "blocked":
            ready.append(item)
        else:
            waiting.append(item)
    return ready, waiting
