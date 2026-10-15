"""Soft knowledge targets and optional project-selected source-size enforcement."""

from .model import estimate_tokens, needs_context
from .repository import project_files, repository_snapshot
from .storage import contained

CODE_SUFFIXES = set(".py .pyi .js .jsx .mjs .cjs .ts .tsx .vue .svelte .go .rs .java .kt .kts "
                    ".c .h .cc .cpp .hpp .cs .fs .fsx .rb .php .swift .scala .sh .bash .zsh "
                    ".ps1 .sql .ex .exs .erl .hrl .clj .cljs .dart .lua .r .R .pl .pm "
                    ".html .htm .css .scss .sass .less .sol .elm .hs .ml .mli .tf".split())
DATA_SUFFIXES = {".json", ".jsonl", ".xml", ".csv", ".tsv", ".yaml", ".yml", ".toml", ".lock"}


def check_budgets(project, *, code=True):
    root = project["root"]
    errors, warnings = [], []
    for path in sorted((root / "openwish").rglob("*")):
        # Machine-written records (review inputs, installer bookkeeping) are not knowledge to read.
        if not path.is_file() or path.name in ("review.json", "installation.json"):
            continue
        path = contained(root, path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"OW knowledge must be UTF-8 text: {path.relative_to(root)}")
            continue
        tokens = estimate_tokens(text)
        if tokens >= 8000:
            warnings.append(f"{path.relative_to(root)}: ~{tokens} tokens; inspect scope and duplication, preserve meaning")
    context = needs_context(project)
    tokens = estimate_tokens(context)
    budget = project["config"]["needs_token_budget"]
    if tokens >= budget * 0.8:
        warnings.append(f"Current needs use ~{tokens}/{budget} tokens (soft target); review sizing and duplication without losing intent.")
    closed = [key for key, change in project["changes"].items() if change["meta"]["status"] == "closed"]
    if closed:
        warnings.append("Closed changes can be disposed after preserving useful knowledge: " + ", ".join(closed))
    if not code:
        return errors, warnings
    exceptions = {}
    for entry in project["config"]["code_exceptions"]:
        path = contained(root, entry["path"])
        relative = path.relative_to(root).as_posix()
        if not path.is_file():
            warnings.append(f"Stale code-size exception: {relative}")
        if entry["kind"] == "data" and path.suffix not in DATA_SUFFIXES:
            errors.append(f"{relative}: data exception requires a data-file extension")
        if relative in exceptions:
            errors.append(f"Duplicate code-size exception: {relative}")
        exceptions[relative] = entry
    snapshot = repository_snapshot(root)
    warnings.extend(snapshot["warnings"])
    hard_limit = project["config"].get("source_hard_limit", 0)
    for path in snapshot["files"]:
        relative = path.relative_to(root).as_posix()
        if relative.startswith("openwish/") or path.suffix not in CODE_SUFFIXES:
            continue
        try:
            # Nonblank physical lines are a language-neutral, conservative LOC proxy.
            count = sum(bool(line.strip()) for line in path.read_text(encoding="utf-8").splitlines())
        except UnicodeError:
            continue
        if count < 500 and (not hard_limit or count < hard_limit):
            continue
        if exceptions.get(relative, {}).get("kind") == "generated":
            continue  # Tool output nobody edits by hand; its size says nothing about maintainability.
        if relative in exceptions:
            warnings.append(f"{relative}: {count} LOC; exception: {exceptions[relative]['reason']}")
        elif hard_limit and count >= hard_limit:
            errors.append(f"{relative}: {count} LOC; project requires under {hard_limit} (or a justified exception)")
        else:
            warnings.append(f"{relative}: {count} LOC; soft target is under 500")
    return errors, warnings
