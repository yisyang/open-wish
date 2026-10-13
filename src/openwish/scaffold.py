"""Safe initialization and small, editable need/change templates."""

from pathlib import Path

from .integrations import asset, install_skills
from .storage import (SCHEMA_VERSION, WishError, contained, document, identifier,
                      load_project, project_config, write_json, write_text)


def initialize(root, harnesses="generic", *, confirm_downgrade=None):
    root = Path(root).resolve()
    config = contained(root, "openwish/config.json")
    if config.exists():
        project_config(root)
        report = install_skills(root, harnesses, confirm_downgrade=confirm_downgrade)
        return {"root": root, "initialized": False, **report}
    outputs = {"openwish/policy.md": asset("policy.md"),
               "openwish/artifacts.md": asset("artifacts.md")}
    for relative in outputs:
        if contained(root, relative).exists():
            raise WishError(f"Existing artifact preserved: {relative}")
    # A missing config must not turn existing knowledge into a new project.
    for relative in ("needs", "changes"):
        path = contained(root, f"openwish/{relative}")
        if path.exists():
            raise WishError(f"Existing artifacts preserved: {path}. Restore the project config first.")
    report = install_skills(root, harnesses, confirm_downgrade=confirm_downgrade)
    for relative, content in outputs.items():
        write_text(contained(root, relative), content, create=True)
    write_json(config, {"version": SCHEMA_VERSION, "product": root.name, "needs_token_budget": 24000,
                        "source_hard_limit": 0, "code_exceptions": []}, create=True)
    return {"root": root, "initialized": True, **report}


def new_artifact(root, kind, key, title, *, needs=(), fast_forward=False):
    if kind not in ("need", "change"):
        raise WishError(f"Unknown artifact kind: {kind}")
    project = load_project(root)
    identifier(key, {"need": "N", "change": "C"}[kind])
    if not title.strip():
        raise WishError("A non-empty title is required.")
    if kind == "need" and (fast_forward or needs):
        raise WishError("--need and --fast-forward apply only to changes.")
    meta = {"id": key, "title": title}
    extras = {}
    if kind == "need":
        meta.update(currency="current", actor="", outcome="", acceptance=[], confirmed_at="")
        relative = f"openwish/needs/{key}.md"
        content = document(meta, "")
    else:
        needs = list(needs)
        if not needs or len(set(needs)) != len(needs):
            raise WishError("A change needs a nonempty, duplicate-free --need selection.")
        for nid in needs:
            if nid not in project["needs"]:
                raise WishError(f"Unknown need: {nid}")
        meta.update(needs=needs, status="open", mode="fast-forward" if fast_forward else "default")
        relative = f"openwish/changes/{key}/change.md"
        directory = contained(root, f"openwish/changes/{key}")
        if directory.exists():
            raise WishError(f"Already exists; preserved: {directory}")
        content = document(meta, "## Purpose\n\nDescribe this bounded improvement.\n\n"
                           "## Scope\n\n"
                           "- Delivers now: observable results and motivating need IDs.\n"
                           "- Preserves: applicable constraints and existing behavior.\n"
                           "- Defers: remaining outcomes, with follow-up changes when planned.\n\n"
                           "## Approach\n\nKeep working design and engineering decisions here. "
                            "Identify prerequisite capabilities to verify in code/tests. Record material "
                            "conditions, exceptions, units/boundaries and consequences; distinguish confirmed "
                            "rules, engineering choices and unresolved decisions.\n\n"
                           "## Verification\n\nDescribe exit evidence for this increment and "
                           "meaningful regression checks. The result should remain useful "
                            "if later changes are postponed.\n\n"
                            "## Handoff\n\nIdentify where material intent, behavior/checks, rationale and "
                            "approved unfinished work will survive disposal. Final review verifies these "
                            "destinations and independent evidence; do not leave deferred detail only here.")
        extras[f"openwish/changes/{key}/tasks.json"] = '{"tasks": []}\n'
    for name in (relative, *extras):
        if contained(root, name).exists():
            raise WishError(f"Already exists; preserved: {name}")
    write_text(contained(root, relative), content, create=True)
    for name, text in extras.items():
        write_text(contained(root, name), text, create=True)
    return relative
