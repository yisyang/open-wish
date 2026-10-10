"""Small filesystem boundary; the model and scheduling rules live elsewhere."""

import json
import os
from pathlib import Path
import re
import tempfile
import tomllib


class WishError(ValueError):
    """An actionable project or command error."""


def project_root(start=None):
    start = Path(start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "openwish" / "config.json").is_file():
            return candidate
    raise WishError("No OW project found. Run 'ow init' first.")


def contained(root, relative):
    root = Path(root).resolve()
    target = root / relative
    if not target.resolve().is_relative_to(root):
        raise WishError(f"Path escapes the project: {relative}")
    if any(p.is_symlink() for p in (target, *target.parents) if p != root):
        raise WishError(f"OW does not write or load through symlinks: {relative}")
    return target


def identifier(value, prefix=None):
    pattern = rf"{prefix}-[0-9]{{3,}}" if prefix else r"[a-z0-9]+(?:-[a-z0-9]+)*"
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise WishError(f"Invalid identifier: {value!r}")
    return value


def read_json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WishError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise WishError(f"Expected a JSON object in {path}")
    return value


def read_document(path):
    try:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines or lines[0] != "+++":
            raise ValueError("expected TOML frontmatter between +++ lines")
        end = lines.index("+++", 1)
        metadata = tomllib.loads("\n".join(lines[1:end]))
    except (OSError, UnicodeError, ValueError) as error:
        raise WishError(f"Cannot read {path}: {error}") from error
    return metadata, "\n".join(lines[end + 1:]).strip()


def document(metadata, body):
    # OW headers deliberately use only strings, booleans, integers and lists.
    def encode(value):
        if isinstance(value, (str, bool, int)):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, list):
            return "[" + ", ".join(encode(item) for item in value) + "]"
        raise WishError(f"Unsupported header value: {value!r}")

    header = "\n".join(f"{key} = {encode(value)}" for key, value in metadata.items())
    return f"+++\n{header}\n+++\n\n{body.strip()}\n"


def write_text(path, text, *, create=False):
    if len(text.splitlines()) >= 500:
        raise WishError(f"OW artifacts must be under 500 lines: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if create:
        try:
            with path.open("x", encoding="utf-8") as output:
                output.write(text)
        except FileExistsError as error:
            raise WishError(f"Already exists; preserved: {path}") from error
        return
    # Replacement is atomic so interruption cannot leave a half-written record.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as output:
        temporary = Path(output.name)
        try:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path, value, *, create=False):
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n", create=create)


def initial_state(*, fast_forward=False, revision=1):
    return {"revision": revision, "mode": "fast-forward" if fast_forward else "default",
            "no_work_reason": "", "gates": {}}


def load_project(root):
    root = Path(root).resolve()
    base = contained(root, "openwish")
    result = {"root": root, "config": read_json(contained(root, "openwish/config.json"))}
    if result["config"].get("version") != 2:
        raise WishError("Unsupported OW schema; expected 2. See docs/migration.md for the v0.1 prototype.")
    patterns = {"needs": "needs/*.md", "specs": "specs/*/spec.md",
                "epics": "epics/*/design.md"}
    for kind, pattern in patterns.items():
        result[kind] = {}
        for path in sorted(base.glob(pattern)):
            path = contained(root, path.relative_to(root))
            metadata, body = read_document(path)
            key = metadata.get("id")
            prefix = {"needs": "N", "specs": "S", "epics": "E"}[kind]
            identifier(key, prefix)
            expected = path.stem if kind == "needs" else path.parent.name
            if key != expected or key in result[kind]:
                raise WishError(f"Duplicate or misplaced {key}: {path}")
            result[kind][key] = {"meta": metadata, "body": body, "path": path}
            if kind == "needs":
                state_path = contained(root, f"openwish/needs/{key}.state.json")
                result[kind][key]["state"] = read_json(state_path) if state_path.exists() else initial_state()
            if kind == "specs":
                design = contained(root, f"openwish/specs/{key}/design.md")
                design_meta, design_body = read_document(design)
                result[kind][key]["design"] = {"meta": design_meta, "body": design_body, "path": design}
    result["tasks"] = []
    for key, epic in result["epics"].items():
        path = contained(root, epic["path"].parent.relative_to(root) / "tasks.json")
        tasks = read_json(path).get("tasks")
        if not isinstance(tasks, list) or not all(isinstance(t, dict) for t in tasks):
            raise WishError(f"Expected a tasks array in {path}")
        result["tasks"].extend({**task, "epic": key} for task in tasks)
    return result
