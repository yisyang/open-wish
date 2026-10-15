"""Git-aware product discovery, including component revisions and dirty submodules."""

from pathlib import Path
import subprocess

from .storage import WishError

EXCLUDED = {".git", ".hg", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".tox"}


def is_repository(directory):
    """A `.git` file (worktree or submodule) or a `.git` directory with a HEAD. Sandboxes such as
    Codex's mount an empty read-only `.git` into plain directories; that is not a repository."""
    marker = directory / ".git"
    return marker.is_file() or (marker / "HEAD").exists()


def git(root, *arguments):
    return subprocess.run(["git", *arguments], cwd=root, capture_output=True,
                          check=True, timeout=10).stdout


def repository_snapshot(root):
    """Return inspectable files, gitlink/checkout revisions, and explicit discovery gaps."""
    root = Path(root).resolve()
    files, components, warnings = set(), {}, []

    def safe(path):
        return (not EXCLUDED.intersection(path.relative_to(root).parts)
                and not any(p.is_symlink() for p in (path, *path.parents) if p != root))

    def discover(directory, *, component=False):
        try:
            entries = git(directory, "ls-files", "--stage", "-z", "--", ".").split(b"\0")
            others = git(directory, "ls-files", "--others", "--exclude-standard", "-z", "--", ".")
        except (OSError, subprocess.SubprocessError) as error:
            if component or is_repository(directory):
                warnings.append(f"Cannot inspect repository {directory.relative_to(root)}: {error}")
                return
            files.update(p for p in directory.rglob("*") if safe(p) and p.is_file())
            return
        for entry in entries:
            if not entry:
                continue
            header, name = entry.split(b"\t", 1)
            mode, revision, stage = header.decode().split()
            path = directory / name.decode("utf-8")
            if not safe(path):
                if mode == "160000":
                    warnings.append(f"Cannot inspect submodule {path.relative_to(root)}: excluded or symlinked")
                continue
            if mode != "160000":
                if path.is_file():
                    files.add(path)
                continue
            relative = path.relative_to(root).as_posix()
            record = components.setdefault(relative, {"index": {}, "head": None})
            record["index"][stage] = revision
            if stage != "0":
                warnings.append(f"Cannot inspect conflicted submodule {relative}; resolve its gitlink")
                continue
            if not is_repository(path):
                warnings.append(f"Cannot inspect submodule {relative}; initialize its checkout")
                continue
            try:
                record["head"] = git(path, "rev-parse", "HEAD").decode().strip()
                discover(path, component=True)
            except (OSError, subprocess.SubprocessError) as error:
                warnings.append(f"Cannot inspect submodule {relative}: {error}")
        for name in others.split(b"\0"):
            if name:
                path = directory / name.decode("utf-8")
                if safe(path) and path.is_file():
                    files.add(path)

    discover(root)
    return {"files": sorted(files), "components": components, "warnings": warnings}


def project_files(root, snapshot=None):
    """Inspectable files; pass a command's snapshot so its checks agree on one view."""
    snapshot = snapshot or repository_snapshot(root)
    if snapshot["warnings"]:
        raise WishError("Repository inspection incomplete:\n- " + "\n- ".join(snapshot["warnings"]))
    return snapshot["files"]
