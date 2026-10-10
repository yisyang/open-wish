"""Small SemVer comparison and OW's own version-stamp format."""

import re

from .storage import WishError

NUMBER = r"(0|[1-9][0-9]*)"
SEMVER = re.compile(rf"^{NUMBER}\.{NUMBER}\.{NUMBER}(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")


def version_key(value):
    match = SEMVER.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise WishError(f"Invalid OW version {value!r}; expected SemVer, e.g. 0.3.0.")
    major, minor, patch, prerelease, build = match.groups()
    for part in (prerelease, build):
        if part is not None and any(not item for item in part.split(".")):
            raise WishError(f"Invalid OW version: {value!r}")
    identifiers = []
    for item in prerelease.split(".") if prerelease else []:
        if item.isdigit():
            if len(item) > 1 and item.startswith("0"):
                raise WishError(f"Invalid OW prerelease version: {value!r}")
            identifiers.append((0, int(item)))
        else:
            identifiers.append((1, item))
    return int(major), int(minor), int(patch), int(prerelease is None), tuple(identifiers)


def declared_version(text):
    """Read only the format OW writes, not arbitrary YAML metadata."""
    lines = text.splitlines()
    candidates = []
    if lines and lines[0] == "---" and "---" in lines[1:]:
        end = lines.index("---", 1)
        metadata = False
        for line in lines[1:end]:
            if line and not line[0].isspace():
                metadata = line == "metadata:"
            if metadata and line.startswith("  openwish-version:"):
                candidates.append(line.split(":", 1)[1].strip().strip("\"'"))
    if lines:
        marker = re.fullmatch(r"(?:<!-- openwish-version: (.+) -->|# openwish-version: (.+))", lines[0])
        if marker:
            candidates.append(marker.group(1) or marker.group(2))
    if len(candidates) > 1:
        raise WishError("Ambiguous OW version stamps; retain one authoritative version.")
    if candidates:
        version_key(candidates[0])
        return candidates[0]
    return None


def stamp(text, version, *, skill=False, yaml=False):
    version_key(version)
    if skill:
        header, separator, body = text.partition("\n---\n")
        if not text.startswith("---\n") or not separator:
            raise WishError("Bundled skill is missing its frontmatter.")
        if "\nmetadata:" in header:
            raise WishError("Bundled skill already has metadata; merge the version stamp explicitly.")
        return f'{header}\nmetadata:\n  openwish-version: "{version}"{separator}{body}'
    marker = f"# openwish-version: {version}" if yaml else f"<!-- openwish-version: {version} -->"
    return marker + "\n" + text
