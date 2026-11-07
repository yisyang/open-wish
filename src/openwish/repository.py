"""Git-aware product discovery, including component revisions and dirty submodules."""

import os
from pathlib import Path
import subprocess
import tempfile

from .storage import WishError

EXCLUDED = {".git", ".hg", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".tox"}


def is_repository(directory):
    """A `.git` file (worktree or submodule) or a `.git` directory with a HEAD. Sandboxes such as
    Codex's mount an empty read-only `.git` into plain directories; that is not a repository."""
    marker = directory / ".git"
    return marker.is_file() or (marker / "HEAD").exists()


def git(root, *arguments, env=None, stdin=None):
    environment = {**os.environ, **env} if env else None
    return subprocess.run(["git", *arguments], cwd=root, env=environment, input=stdin,
                          capture_output=True, check=True, timeout=10).stdout


def product_tree(root, entries):
    """The git tree ID of the given product paths ({name: "100644" or "100755"}),
    including uncommitted content. It is built in a temporary index, so the
    repository's own index and working tree are untouched; component files are
    hashed into the parent's object store so the tree covers the whole product.
    None without a repository or a working git."""
    if not is_repository(Path(root)):
        return None
    fd, index = tempfile.mkstemp()
    os.close(fd)
    try:
        os.unlink(index)  # an empty path makes git create a fresh index there
        env = {"GIT_INDEX_FILE": index}
        names = sorted(entries)
        try:
            blobs = git(root, "hash-object", "-w", "--stdin-paths", env=env,
                        stdin=b"\n".join(os.fsencode(name) for name in names)).split()
            listing = b"".join(entries[name].encode() + b" " + blob + b"\t" +
                               os.fsencode(name) + b"\0" for name, blob in zip(names, blobs))
            git(root, "update-index", "-z", "--index-info", env=env, stdin=listing)
            return git(root, "write-tree", env=env).decode().strip()
        except (OSError, subprocess.SubprocessError):
            return None
    finally:
        Path(index).unlink(missing_ok=True)


def tree_changes(root, before, after):
    """Changed paths between two recorded product trees; None when git cannot compare them."""
    try:
        output = git(root, "diff", "--name-status", "--no-renames", "-z", before, after)
    except (OSError, subprocess.SubprocessError):
        return None
    labels = {"A": "added", "D": "removed"}
    changed = []
    fields = output.split(b"\0")
    for status, path in zip(fields[::2], fields[1::2]):
        if status and path:
            changed.append(f"{os.fsdecode(path)} {labels.get(status[:1].decode(), 'modified')}")
    return changed


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


def pin_mismatches(snapshot):
    """Components whose parent gitlink does not pin the checkout that was inspected."""
    return [f"{path}: parent gitlink {record['index']['0'][:12]} differs from checkout "
            f"{record['head'][:12]}; stage or commit the reviewed pin"
            for path, record in sorted(snapshot["components"].items())
            if record["head"] and record["index"].get("0") not in (None, record["head"])]


def project_files(root, snapshot=None):
    """Inspectable files; pass a command's snapshot so its checks agree on one view."""
    snapshot = snapshot or repository_snapshot(root)
    if snapshot["warnings"]:
        raise WishError("Repository inspection incomplete:\n- " + "\n- ".join(snapshot["warnings"]))
    return snapshot["files"]
