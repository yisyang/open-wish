"""Structural checks; product alignment and evidence quality require reasoning."""

from datetime import date, datetime
import re

from .model import CHANGE_STATES, CURRENCY, MODES, RELATIONS, TASK_STATES, topological_order
from .repository import repository_snapshot
from .storage import SCHEMA_VERSION, WishError, contained, repository_file


def string_list(value):
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def header_value(value):
    return (isinstance(value, (str, bool, int))
            or (isinstance(value, list) and all(header_value(v) for v in value))
            or (isinstance(value, dict) and all(isinstance(k, str) and header_value(v) for k, v in value.items())))


def relation_errors(key, meta, needs):
    relations = meta.get("relations", [])
    if not isinstance(relations, list):
        return [f"{key}: relations must be an array of kind/need/reason tables"]
    errors, seen = [], set()
    for relation in relations:
        if (not isinstance(relation, dict) or set(relation) != {"kind", "need", "reason"}
                or relation.get("kind") not in RELATIONS or not nonempty(relation.get("need"))
                or not nonempty(relation.get("reason"))):
            errors.append(f"{key}: each relation needs kind (requires or constrains), need ID, and reason")
            continue
        target, kind = relation["need"], relation["kind"]
        if target == key:
            errors.append(f"{key}: a need relation cannot target itself")
        if (kind, target) in seen:
            errors.append(f"{key}: duplicate {kind} relation to {target}")
        seen.add((kind, target))
        if target not in needs:
            errors.append(f"{key}: unknown relation target {target}")
        elif meta.get("currency") == "current" and needs[target]["meta"].get("currency") == "retired":
            errors.append(f"{key}: reconcile relation to retired need {target} before use")
    return errors


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
    require(type(config.get("version")) is int and config["version"] == SCHEMA_VERSION,
            f"config: unsupported schema version (expected {SCHEMA_VERSION})")
    require(nonempty(config.get("product")), "config: product is required")
    require(type(config.get("needs_token_budget")) is int and config["needs_token_budget"] > 0,
             "config: needs_token_budget must be a positive integer")
    require(type(config.get("source_hard_limit", 0)) is int and config.get("source_hard_limit", 0) >= 0,
            "config: source_hard_limit must be a nonnegative integer (0 disables enforcement)")
    exceptions = config.get("code_exceptions")
    require(isinstance(exceptions, list), "config: code_exceptions must be an array")
    for exception in exceptions if isinstance(exceptions, list) else []:
        require(isinstance(exception, dict) and nonempty(exception.get("path"))
                and nonempty(exception.get("reason"))
                and exception.get("kind") in ("data", "low-complexity"),
                "config: each code exception needs path, reason, and kind (data or low-complexity)")

    base = project["root"] / "openwish"
    for path in (base / "needs").glob("*"):
        contained(project["root"], path.relative_to(project["root"]))
        require(path.is_file() and path.suffix == ".md" and path.stem in project["needs"],
                f"Unrecognized need artifact: {path.name}; needs must be flat needs/N-NNN.md files.")
    for path in (base / "changes").glob("*"):
        contained(project["root"], path.relative_to(project["root"]))
        require(path.is_dir() and path.name in project["changes"],
                f"Unrecognized change artifact: {path.name}; preserve and reconcile it before use.")

    for kind in ("needs", "changes"):
        for key, record in project[kind].items():
            require(all(header_value(value) for value in record["meta"].values()),
                    f"{key}: header values must be strings, booleans, integers, arrays, or inline tables")

    visible_references = None
    for key, record in project["needs"].items():
        meta = record["meta"]
        errors.extend(relation_errors(key, meta, project["needs"]))
        references = meta.get("references", [])
        require(string_list(references), f"{key}: references must be an array of repository file paths")
        for relative in references if string_list(references) else []:
            try:
                path = repository_file(project["root"], relative)
                if visible_references is None:
                    visible_references = set(repository_snapshot(project["root"])["files"])
                require(path in visible_references,
                        f"{key}: durable reference is ignored or excluded from repository inspection: {relative}")
                require(not relative.startswith("openwish/changes/"),
                        f"{key}: durable references cannot target disposable changes")
            except WishError as error:
                errors.append(f"{key}: {error}")
        for field in ("title", "actor", "outcome"):
            require(nonempty(meta.get(field)), f"{key}: {field} is required")
        require(meta.get("currency") in CURRENCY, f"{key}: invalid currency")
        require("ask" not in meta, f"{key}: persist the need, not an ask field")
        require(string_list(meta.get("acceptance")) and bool(meta.get("acceptance")),
                f"{key}: acceptance must contain observable satisfaction conditions")
        confirmed = meta.get("confirmed_at", "")
        try:
            if not isinstance(confirmed, str):
                raise ValueError()
            if confirmed:
                date.fromisoformat(confirmed)
        except ValueError:
            errors.append(f"{key}: confirmed_at must be an ISO date string or empty")

    for key, record in project["changes"].items():
        meta = record["meta"]
        require(nonempty(meta.get("title")), f"{key}: title is required")
        links(meta, "needs", project["needs"], key)
        require(bool(meta.get("needs")), f"{key}: link at least one need")
        require(meta.get("status") in CHANGE_STATES, f"{key}: invalid change status")
        require(meta.get("mode") in MODES, f"{key}: invalid mode")
        require(nonempty(record["body"]), f"{key}: purpose, approach, and verification are required")
        if meta.get("status") == "closed":
            require(meta.get("closed_by") in ("human", "fast-forward"), f"{key}: missing closure provenance")
            require(meta.get("closed_by") != "fast-forward" or meta.get("mode") == "fast-forward",
                    f"{key}: fast-forward closure requires explicit change mode")
            try:
                datetime.fromisoformat(meta.get("closed_at", ""))
            except (TypeError, ValueError):
                errors.append(f"{key}: closed_at must be an ISO timestamp")

    task_ids = set()
    for task in project["tasks"]:
        key = task.get("id")
        valid_id = isinstance(key, str) and re.fullmatch(rf"{task['change']}/T-[0-9]{{3,}}", key)
        require(valid_id, f"{task['change']}: task ID must be {task['change']}/T-NNN")
        if isinstance(key, str):
            require(key not in task_ids, f"Duplicate task ID: {key}")
            task_ids.add(key)
        require(task.get("status") in TASK_STATES, f"{key}: invalid task status")
        require(task.get("kind", "agent") in ("agent", "manual"), f"{key}: kind must be agent or manual")
        for field in ("title", "acceptance"):
            require(nonempty(task.get(field)), f"{key}: {field} is required")
        require(string_list(task.get("files", [])), f"{key}: files must be an array of paths")
        require(isinstance(task.get("evidence", ""), str), f"{key}: evidence must be a string")
        if task.get("status") == "done":
            require(nonempty(task.get("evidence")), f"{key}: completed tasks need direct evidence")
        if project["changes"][task["change"]]["meta"].get("status") == "closed":
            require(task.get("status") == "done", f"{key}: closed changes cannot contain unfinished work")
    for task in project["tasks"]:
        links(task, "depends_on", task_ids, task.get("id"), optional=True)
    if errors:
        return errors

    tasks = {task["id"]: task for task in project["tasks"]}
    try:
        topological_order({key: task.get("depends_on", []) for key, task in tasks.items()})
    except WishError as error:
        errors.append(str(error))
    for task in tasks.values():
        for dep in task.get("depends_on", []):
            prerequisite = tasks[dep]
            require(prerequisite["change"] == task["change"],
                    f"{task['id']}: prerequisites must stay within the change so it can be disposed independently")
            if task["status"] == "done":
                require(prerequisite["status"] == "done", f"{task['id']}: prerequisite {dep} is unfinished")
    return errors
