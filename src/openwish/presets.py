"""The OW defaults a project may replace, the presets that replace them, and the lint that holds both."""

from importlib.resources import files
import re

from .storage import contained

DEFAULTS = ("stage", "calibration", "verification")
POLICY = "openwish/policy.md"
OVERRIDES = re.compile(r"^Overrides:(.*)$", re.M)
NAME = re.compile(r"`([^`]+)`")


def preset_directory():
    return files("openwish").joinpath("assets", "skills", "ow-core", "presets")


def available_presets():
    return sorted(entry.name[:-3] for entry in preset_directory().iterdir() if entry.name.endswith(".md"))


def preset_text(name):
    return preset_directory().joinpath(f"{name}.md").read_text(encoding="utf-8")


def overridden(text):
    """Defaults named on `Overrides:` lines, the one marker presets and project policy share."""
    return [name for line in OVERRIDES.findall(text) for name in NAME.findall(line)]


def selected_presets(config):
    presets = config.get("presets", [])
    return presets if isinstance(presets, list) else []


def preset_rows(config):
    return [{"name": name, "overrides": overridden(preset_text(name)), "path": f"ow-core/presets/{name}.md"}
            for name in selected_presets(config) if name in available_presets()]


def preset_errors(project):
    config, errors = project["config"], []
    presets = config.get("presets", [])
    known = available_presets()
    if not isinstance(presets, list) or not all(isinstance(name, str) for name in presets):
        return ["config: presets must be an array of preset names"]
    if len(set(presets)) != len(presets):
        errors.append("config: duplicate presets")
    for name in presets:
        if name not in known:
            errors.append(f"config: unknown preset {name} (available: {', '.join(known)})")
    claimed = {}
    for row in preset_rows(config):
        for default in row["overrides"]:
            if default in claimed and claimed[default] != row["name"]:
                errors.append(f"config: presets {claimed[default]} and {row['name']} both replace {default}")
            claimed[default] = row["name"]
    policy = contained(project["root"], POLICY)
    text = policy.read_text(encoding="utf-8") if policy.exists() else ""
    for default in overridden(text):
        if default not in DEFAULTS:
            errors.append(f"{POLICY}: '{default}' is not a default a project may override "
                          f"({', '.join(DEFAULTS)}); OW's other rules hold in every project")
    return errors
