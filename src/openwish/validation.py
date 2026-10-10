"""Structural checks, separate from the agent's semantic alignment review."""

from datetime import date
import re

from .model import CURRENCY, GATES, IMPLEMENTATION, TASK_STATES, need_scope, topological_order
from .storage import WishError


def string_list(value):
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(project):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def links(meta, field, targets, label, *, optional=False):
        value = meta.get(field, [] if optional else None)
        if not string_list(value):
            errors.append(f"{label}: {field} must be an array of non-empty IDs")
            return
        require(len(set(value)) == len(value), f"{label}: duplicate {field} links")
        for key in value:
            require(key in targets, f"{label}: unknown {field} reference {key}")

    config = project["config"]
    legacy = project["root"] / "openwish/changes"
    require(not (legacy.exists() and any(legacy.rglob("*"))),
            "Legacy change records remain; reconcile durable needs using docs/migration.md.")
    require(config.get("version") == 2, "config: unsupported schema version (expected 2)")
    require(nonempty(config.get("product")), "config: product is required")
    for field in ("needs_token_budget", "epic_limit"):
        require(type(config.get(field)) is int and config[field] > 0,
                f"config: {field} must be a positive integer")
    exceptions = config.get("code_exceptions")
    require(isinstance(exceptions, list), "config: code_exceptions must be an array")
    for exception in exceptions if isinstance(exceptions, list) else []:
        require(isinstance(exception, dict) and nonempty(exception.get("path"))
                and nonempty(exception.get("reason"))
                and exception.get("kind") in ("data", "low-complexity"),
                "config: each code exception needs path, reason, and kind (data or low-complexity)")

    for kind in ("needs", "specs", "epics"):
        for key, record in project[kind].items():
            meta = record["meta"]
            require(nonempty(meta.get("title")), f"{key}: title is required")
            if kind != "epics":
                require(meta.get("implementation") in IMPLEMENTATION,
                        f"{key}: invalid implementation status")
            if kind == "needs":
                require(meta.get("currency") in CURRENCY, f"{key}: invalid currency")
                require("ask" not in meta, f"{key}: persist the need, not an ask field")
                for field in ("actor", "outcome"):
                    require(nonempty(meta.get(field)), f"{key}: {field} is required")
                require(string_list(meta.get("acceptance")) and bool(meta.get("acceptance")),
                        f"{key}: acceptance must contain observable satisfaction conditions")
                for field in ("confirmed_at", "verified_at"):
                    value = meta.get(field)
                    try:
                        if not isinstance(value, str):
                            raise ValueError()
                        if value:
                            date.fromisoformat(value)
                    except ValueError:
                        errors.append(f"{key}: {field} must be an ISO date string or empty")
            elif kind == "specs":
                design = record["design"]
                require(design["meta"].get("id") == key, f"{key}: design ID must match its spec")
                links(design["meta"], "needs", project["needs"], f"{key} design")
                require(bool(design["meta"].get("needs")), f"{key}: design must link at least one need")
                require("needs" not in meta, f"{key}: keep authoritative need references in design.md")
                require(nonempty(design["body"]), f"{key}: technical design is required")
                links(meta, "depends_on", project["specs"], key)
                parent = meta.get("parent", "")
                require(isinstance(parent, str), f"{key}: parent must be an ID or empty string")
                if isinstance(parent, str) and parent:
                    require(parent in project["specs"], f"{key}: unknown parent {parent}")
                require((record["path"].parent / "design.md").is_file(), f"{key}: design.md is missing")
                require(nonempty(record["body"]), f"{key}: behavioral contract is required")
            else:
                links(meta, "specs", project["specs"], key)
                require(bool(meta.get("specs")), f"{key}: link at least one spec")
                require(nonempty(record["body"]), f"{key}: implementation design is required")

    task_ids = set()
    for task in project["tasks"]:
        key = task.get("id")
        valid_id = isinstance(key, str) and re.fullmatch(rf"{task['epic']}/T-[0-9]{{3,}}", key)
        require(valid_id, f"{task['epic']}: task ID must be {task['epic']}/T-NNN")
        if isinstance(key, str):
            require(key not in task_ids, f"Duplicate task ID: {key}")
            task_ids.add(key)
        for field in ("group", "order"):
            require(type(task.get(field)) is int and task[field] > 0,
                    f"{key}: {field} must be a positive integer")
        require(task.get("status") in TASK_STATES, f"{key}: invalid task status")
        require(task.get("kind") in ("agent", "manual"), f"{key}: kind must be agent or manual")
        for field in ("title", "acceptance"):
            require(nonempty(task.get(field)), f"{key}: {field} is required")
        require(string_list(task.get("files")), f"{key}: files must be an array of paths")
        require(isinstance(task.get("evidence"), str), f"{key}: evidence must be a string")
        if task.get("status") == "done":
            require(nonempty(task.get("evidence")), f"{key}: completed tasks need direct evidence")
    for task in project["tasks"]:
        links(task, "depends_on", task_ids, task.get("id"))

    for key, need in project["needs"].items():
        state = need["state"]
        require(type(state.get("revision")) is int and state["revision"] > 0, f"{key}: revision must be positive")
        require(state.get("mode") in ("default", "fast-forward"), f"{key}: invalid mode")
        require(isinstance(state.get("no_work_reason"), str), f"{key}: no_work_reason must be a string")
        require(set(state).issubset({"revision", "mode", "no_work_reason", "gates"}),
                f"{key}: need state only stores revision, mode, no_work_reason, and gates")
        gates = state.get("gates")
        if not isinstance(gates, dict):
            errors.append(f"{key}: gates must be an object")
            continue
        for gate, record in gates.items():
            require(gate in GATES and isinstance(record, dict), f"{key}: invalid gate {gate}")
            if isinstance(record, dict):
                require(record.get("by") in ("human", "fast-forward"), f"{key}/{gate}: invalid approver")
                require(nonempty(record.get("fingerprint")), f"{key}/{gate}: missing fingerprint")
                require(nonempty(record.get("at")), f"{key}/{gate}: missing timestamp")

    if errors:
        return errors
    # Only operate on graphs after all input types and references are sound.
    for relation in ("depends_on", "parent"):
        graph = {}
        for key, spec in project["specs"].items():
            value = spec["meta"].get(relation)
            graph[key] = value if isinstance(value, list) else ([value] if value else [])
        try:
            topological_order(graph)
        except WishError as error:
            errors.append(f"Specs ({relation}): {error}")
    tasks = {task["id"]: task for task in project["tasks"]}
    try:
        topological_order({key: task["depends_on"] for key, task in tasks.items()})
    except WishError as error:
        errors.append(str(error))
    for task in tasks.values():
        for dep in task["depends_on"]:
            prerequisite = tasks[dep]
            require((prerequisite["group"], prerequisite["order"]) < (task["group"], task["order"]),
                    f"{task['id']}: prerequisite {dep} must have a lower group/order")
            if task["status"] == "done":
                require(prerequisite["status"] == "done", f"{task['id']}: prerequisite {dep} is unfinished")
    for key in project["needs"]:
        scope = need_scope(project, [key])
        scoped = [t for t in tasks.values() if t["epic"] in scope["epics"]]
        ordinals = [(t["group"], t["order"]) for t in scoped]
        require(len(set(ordinals)) == len(ordinals), f"{key}: task group/order pairs must be unique")
    return errors
