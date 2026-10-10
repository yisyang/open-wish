"""Bounded artifacts and a conservative source-size check."""

from pathlib import Path
import subprocess

from .model import estimate_tokens, needs_context
from .storage import contained

CODE_SUFFIXES = set(".py .pyi .js .jsx .mjs .cjs .ts .tsx .vue .svelte .go .rs .java .kt .kts "
                    ".c .h .cc .cpp .hpp .cs .fs .fsx .rb .php .swift .scala .sh .bash .zsh "
                    ".ps1 .sql .ex .exs .erl .hrl .clj .cljs .dart .lua .r .R .pl .pm "
                    ".html .htm .css .scss .sass .less .sol .elm .hs .ml .mli .tf".split())
DATA_SUFFIXES = {".json", ".jsonl", ".xml", ".csv", ".tsv", ".yaml", ".yml", ".toml", ".lock"}
EXCLUDED = {".git", ".hg", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".tox"}


def project_files(root):
    """Respect Git ignores, include tracked and untracked files, support non-Git projects."""
    try:
        result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "."],
                                cwd=root, capture_output=True, check=True, timeout=10)
        candidates = [root / Path(name.decode("utf-8")) for name in result.stdout.split(b"\0") if name]
    except (OSError, subprocess.SubprocessError, UnicodeError):
        candidates = list(root.rglob("*"))
    return sorted({path for path in candidates if path.is_file() and not path.is_symlink()
                   and not EXCLUDED.intersection(path.relative_to(root).parts)
                   and not any(parent.is_symlink() for parent in path.parents if parent != root)})


def check_budgets(project, *, code=True):
    root = project["root"]
    errors, warnings = [], []
    for path in sorted((root / "openwish").rglob("*")):
        if not path.is_file():
            continue
        path = contained(root, path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"OW knowledge must be UTF-8 text: {path.relative_to(root)}")
            continue
        count = len(text.splitlines())
        if count >= 500:
            errors.append(f"{path.relative_to(root)}: {count} lines; OW artifacts must be under 500")
        elif count >= 400:
            warnings.append(f"{path.relative_to(root)}: {count} lines; compact before reaching 500")
    context = needs_context(project)
    tokens = estimate_tokens(context)
    budget = project["config"]["needs_token_budget"]
    if tokens > budget:
        errors.append(f"Current needs use ~{tokens} tokens; budget is {budget}. Consolidate without losing intent.")
    if len(context.splitlines()) >= 500:
        errors.append("Combined current-needs context must be under 500 lines; splitting files is insufficient.")
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
    for path in project_files(root):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("openwish/") or path.suffix not in CODE_SUFFIXES:
            continue
        try:
            # Nonblank physical lines are a language-neutral, conservative LOC proxy.
            count = sum(bool(line.strip()) for line in path.read_text(encoding="utf-8").splitlines())
        except UnicodeError:
            continue
        if count < 500:
            continue
        if relative in exceptions:
            warnings.append(f"{relative}: {count} LOC; exception: {exceptions[relative]['reason']}")
        elif count >= 1000:
            errors.append(f"{relative}: {count} LOC; code must be under 1000 (or have a justified exception)")
        else:
            warnings.append(f"{relative}: {count} LOC; soft target is under 500")
    return errors, warnings
