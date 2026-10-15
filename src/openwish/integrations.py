"""Plan version-aware installation before performing filesystem effects."""

from importlib.resources import files
import json

from . import __version__
from .storage import WishError, contained, read_json, write_json, write_text
from .versions import declared_version, stamp, version_key

SKILLS = ("propose", "align", "plan", "implement", "review", "consolidate", "fast-forward", "onboard")
HARNESSES = ("opencode", "claude", "codex", "generic")
DIRECTORIES = {"generic": ".agents", "codex": ".agents", "claude": ".claude", "opencode": ".opencode"}
MANIFEST = "openwish/installation.json"
# The artifact reference documents this CLI, so it upgrades with it; policy stays project-owned.
REFERENCE = "openwish/artifacts.md"


def asset(name):
    return files("openwish").joinpath("assets", name).read_text(encoding="utf-8")


def normalize_harnesses(harnesses):
    values = [harnesses] if isinstance(harnesses, str) else list(harnesses)
    if not values or any(value not in HARNESSES for value in values):
        raise WishError("Select at least one supported harness: " + ", ".join(HARNESSES))
    return [name for name in HARNESSES if name in values]


def load_manifest(root):
    path = contained(root, MANIFEST)
    if not path.exists():
        return {"format": 1, "harnesses": [], "files": {}}
    manifest = read_json(path)
    if manifest.get("format") != 1 or not isinstance(manifest.get("files"), dict):
        raise WishError("Unsupported or malformed OW installation manifest.")
    harnesses = manifest.get("harnesses")
    if not isinstance(harnesses, list) or any(name not in HARNESSES for name in harnesses):
        raise WishError("Invalid harnesses in OW installation manifest.")
    for relative, version in manifest["files"].items():
        contained(root, relative)
        version_key(version)
    return manifest


def require_current_cli(root):
    """Refuse to judge records installed by a newer OW, whose rules this CLI may not know."""
    newest = max(load_manifest(root)["files"].values(), key=version_key, default=None)
    if newest is not None and version_key(newest) > version_key(__version__):
        raise WishError(f"This project's OW integrations are {newest}, newer than this CLI "
                        f"({__version__}). Upgrade OpenWish (uv tool upgrade openwish) before using it here.")


def installed_harnesses(root):
    manifest = load_manifest(root)
    detected = set(manifest["harnesses"])
    for name in ("opencode", "claude", "codex"):
        if name == "codex" and "generic" in detected:
            continue
        directory = contained(root, f"{DIRECTORIES[name]}/skills")
        if any(directory.glob("ow-*/SKILL.md")):
            detected.add(name)
    return [name for name in HARNESSES if name in detected]


def integration_files(harnesses, version):
    outputs = {REFERENCE: stamp(asset("artifacts.md"), version)}
    for harness in normalize_harnesses(harnesses):
        directory = DIRECTORIES[harness]
        for skill in SKILLS:
            outputs[f"{directory}/skills/ow-{skill}/SKILL.md"] = stamp(
                asset(f"skills/ow-{skill}/SKILL.md"), version, skill=True)
            if harness == "opencode":
                prompt = (f"Follow the ow-{skill} skill in this project. "
                          f"Read .opencode/skills/ow-{skill}/SKILL.md if needed.\n\n$ARGUMENTS\n")
                outputs[f".opencode/commands/ow-{skill}.md"] = stamp(prompt, version)
                if skill in ("fast-forward", "onboard"):
                    outputs[f".opencode/commands/{skill}.md"] = stamp(prompt, version)
            if harness == "claude" and skill in ("fast-forward", "onboard"):
                content = (f"---\nname: {skill}\ndescription: Explicit OpenWish {skill} shortcut.\n"
                           "disable-model-invocation: true\n---\n\n"
                           f"Read and follow .claude/skills/ow-{skill}/SKILL.md from the project root.\n"
                           "Apply it to the user's arguments.\n")
                outputs[f".claude/skills/{skill}/SKILL.md"] = stamp(content, version, skill=True)
            if harness in ("generic", "codex") and skill == "fast-forward":
                outputs[f"{directory}/skills/ow-{skill}/agents/openai.yaml"] = stamp(
                    "policy:\n  allow_implicit_invocation: false\n", version, yaml=True)
    return outputs


def install_skills(root, harnesses, *, confirm_downgrade=None):
    harnesses = normalize_harnesses(harnesses)
    manifest = load_manifest(root)
    outputs = integration_files(harnesses, __version__)
    target = version_key(__version__)
    plan = []
    for relative, content in outputs.items():
        path = contained(root, relative)
        try:
            current = path.read_text(encoding="utf-8") if path.exists() else None
        except UnicodeError as error:
            raise WishError(f"Cannot read integration file as UTF-8; preserved: {relative}") from error
        if current is None:
            plan.append((relative, content, "installed", __version__))
            continue
        installed = declared_version(current) or manifest["files"].get(relative)
        if installed is None and relative == REFERENCE:
            raise WishError(f"{REFERENCE} predates version stamps; delete it and rerun 'ow init' "
                            "to install the current reference (project knowledge lives elsewhere).")
        if installed is None:
            raise WishError(f"Integration file has no version or installation record; preserved: {relative}")
        existing = version_key(installed)
        action = "unchanged" if existing == target else ("upgraded" if existing < target else "downgraded")
        plan.append((relative, content, action, installed))

    downgrades = [{"path": path, "installed": version, "available": __version__}
                  for path, _, action, version in plan if action == "downgraded"]
    allow_downgrade = False
    if downgrades:
        if confirm_downgrade is None:
            raise WishError("Downgrade requires confirmation. Run 'ow init' in an interactive terminal.")
        allow_downgrade = confirm_downgrade(downgrades)

    tracked = dict(manifest["files"])
    for relative, _, action, installed in plan:
        tracked[relative] = (installed if action == "unchanged" or
                            (action == "downgraded" and not allow_downgrade) else __version__)
    updated = {"format": 1, "harnesses": normalize_harnesses(manifest["harnesses"] + harnesses), "files": tracked}

    report = dict.fromkeys(("installed", "upgraded", "downgraded", "unchanged", "kept_newer"), 0)
    for relative, content, action, installed in plan:
        if action == "downgraded" and not allow_downgrade:
            action = "kept_newer"
        report[action] += 1
        if action in ("installed", "upgraded", "downgraded"):
            write_text(contained(root, relative), content, create=action == "installed")
    if updated != manifest:
        write_json(contained(root, MANIFEST), updated)
    return {"harnesses": harnesses, **report}
