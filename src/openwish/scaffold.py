"""Safe initialization and small, editable artifact templates."""

from pathlib import Path

from .integrations import asset, install_skills
from .storage import WishError, contained, document, identifier, initial_state, read_json, write_json, write_text


def initialize(root, harnesses="generic", *, confirm_downgrade=None):
    root = Path(root).resolve()
    config = contained(root, "openwish/config.json")
    if config.exists():
        if read_json(config).get("version") != 2:
            raise WishError("Unsupported OW schema; expected 2. See docs/migration.md before updating this project.")
        report = install_skills(root, harnesses, confirm_downgrade=confirm_downgrade)
        return {"root": root, "initialized": False, **report}
    outputs = {"openwish/policy.md": asset("policy.md"),
               "openwish/artifacts.md": asset("artifacts.md"),
               "openwish/knowledge/environment.md": "# Environment\n\nRecord verified environment profiles and secret references here.\n"}
    for relative in outputs:
        if contained(root, relative).exists():
            raise WishError(f"Existing artifact preserved: {relative}")
    report = install_skills(root, harnesses, confirm_downgrade=confirm_downgrade)
    for relative, content in outputs.items():
        write_text(contained(root, relative), content, create=True)
    write_json(config, {"version": 2, "product": root.name, "needs_token_budget": 6000,
                        "epic_limit": 8, "code_exceptions": []}, create=True)
    return {"root": root, "initialized": True, **report}


def new_artifact(root, kind, key, title, *, fast_forward=False):
    if kind not in ("need", "spec", "epic"):
        raise WishError(f"Unknown artifact kind: {kind}")
    if fast_forward and kind != "need":
        raise WishError("--fast-forward applies only to needs.")
    prefix = {"need": "N", "spec": "S", "epic": "E"}.get(kind)
    identifier(key, prefix)
    if not title.strip():
        raise WishError("A non-empty title is required.")
    meta = {"id": key, "title": title}
    if kind == "need":
        meta.update(currency="current", implementation="open", actor="",
                    outcome="", acceptance=[], confirmed_at="", verified_at="")
        relative = f"openwish/needs/{key}.md"
        content = document(meta, "")
    elif kind == "spec":
        meta.update(depends_on=[], parent="", implementation="open")
        relative = f"openwish/specs/{key}/spec.md"
        content = document(meta, "## Contract\n\nDescribe observable behavior and acceptance scenarios.")
    elif kind == "epic":
        meta.update(specs=[])
        relative = f"openwish/epics/{key}/design.md"
        content = document(meta, "## Implementation design\n\nDescribe the smallest coherent increment supporting the linked spec designs.")
    extras = {}
    if kind == "spec":
        extras[f"openwish/specs/{key}/design.md"] = document(
            {"id": key, "needs": []}, "# Design\n\nExplain how the approach satisfies the linked needs and constraints.")
    if kind == "epic":
        extras[f"openwish/epics/{key}/tasks.json"] = '{"tasks": []}\n'
    state_path = f"openwish/needs/{key}.state.json" if kind == "need" else None
    for name in (relative, *extras, *([state_path] if state_path else [])):
        if contained(root, name).exists():
            raise WishError(f"Already exists; preserved: {name}")
    write_text(contained(root, relative), content, create=True)
    for name, text in extras.items():
        write_text(contained(root, name), text, create=True)
    if state_path:
        write_json(contained(root, state_path), initial_state(fast_forward=fast_forward), create=True)
    return relative
