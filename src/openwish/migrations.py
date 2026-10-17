"""Upgrade older project schemas so `openwish/` holds only project-owned knowledge."""

import hashlib
import json
import re

from .integrations import asset
from .storage import (OLDEST_MIGRATABLE, SCHEMA_VERSION, WishError, contained, project_config,
                      read_json, write_text)
from .versions import declared_version

POLICY = "openwish/policy.md"
LEGACY_REFERENCE = "openwish/artifacts.md"
MANIFEST = "openwish/installation.json"


def normalize(text):
    return " ".join(text.split())


def digest(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def blocks(text):
    """Split markdown into (heading, block) pairs: paragraphs, list items and table rows.

    A table row also carries its table's header and separator rows, so a kept row can
    be written back as a valid table.
    """
    result, heading, current, fenced, table = [], None, [], False, None

    def flush():
        nonlocal current
        if current:
            result.append((heading, "\n".join(current), None))
        current = []

    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            current.append(line)
            continue
        if fenced:
            current.append(line)
            continue
        if not line.strip():
            flush()
            table = None
            continue
        if re.match(r"#{1,6} ", line):
            flush()
            heading, table = line, None
            continue
        if line.startswith("|"):
            flush()
            if table is None:
                table = [line]
                result.append((heading, line, None))
            elif len(table) == 1 and re.fullmatch(r"\|[\s:|-]+\|", line):
                table.append(line)
                result.append((heading, line, None))
            else:
                result.append((heading, line, tuple(table)))
            continue
        if re.match(r"(- |\d+\. )", line):
            flush()
        current.append(line)
    flush()
    return result


def known_digests():
    return json.loads(asset("migrations/schema-4.json"))


def split_policy(text, generic):
    """Keep the project's own policy blocks; drop text OW shipped, which now lives in ow-core."""
    template = asset("project-policy.md")
    generic = set(generic) | {digest(block) for _, block, _ in blocks(template)}
    kept, sections = [], {}
    for heading, block, table in blocks(text):
        if digest(block) in generic:
            continue
        if heading not in sections:
            sections[heading] = []
            kept.append(heading)
        rows = sections[heading]
        if table and not any(header in rows for header in table):
            rows.extend(table)
        rows.append(block)
    if not kept:
        return template, []
    parts = [template.rstrip("\n")]
    for heading in kept:
        parts.append("\n\n".join(filter(None, [heading, *join_runs(sections[heading])])))
    return "\n\n".join(parts) + "\n", [heading or "(top of file)" for heading in kept]


LIST_ITEM = re.compile(r"(- |\d+\. )")


def join_runs(items):
    """Rejoin consecutive table rows, and consecutive list items, as they were written."""
    joined = []
    for item in items:
        previous = joined[-1] if joined else ""
        if (item.startswith("|") and previous.startswith("|")) or (
                LIST_ITEM.match(item) and LIST_ITEM.match(previous)):
            joined[-1] += "\n" + item
        else:
            joined.append(item)
    return joined


def plan_migration(root):
    """Preflight the whole upgrade; return writes, removals and notes, or None if current."""
    config = project_config(root, migratable=True)
    version = config["version"]
    if version == SCHEMA_VERSION:
        return None
    if version != OLDEST_MIGRATABLE:
        raise WishError(f"No migration from OW schema {version} (expected {SCHEMA_VERSION}).")
    known = known_digests()
    writes, removals, notes = {}, [], []
    policy = contained(root, POLICY)
    text = policy.read_text(encoding="utf-8") if policy.exists() else ""
    migrated, kept = split_policy(text, known["policy"])
    if migrated != text:
        writes[POLICY] = migrated
    if kept:
        notes.append(f"{POLICY}: kept project text under {', '.join(kept)}. OW's own rules now ship in "
                     "the ow-core skill; check that kept text adds to them or names the rule it overrides.")
    reference = contained(root, LEGACY_REFERENCE)
    if reference.exists():
        body = reference.read_text(encoding="utf-8")
        if declared_version(body):
            body = body.split("\n", 1)[1] if "\n" in body else ""
        if digest(body) in known["artifacts"]:
            removals.append(LEGACY_REFERENCE)
        else:
            notes.append(f"{LEGACY_REFERENCE}: edited, so kept as a project file; the current "
                         "artifact reference ships in the ow-core skill.")
    manifest_path = contained(root, MANIFEST)
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        if not isinstance(manifest.get("files"), dict):
            raise WishError("Unsupported or malformed OW installation manifest.")
        if LEGACY_REFERENCE in manifest["files"]:
            files = {k: v for k, v in manifest["files"].items() if k != LEGACY_REFERENCE}
            writes[MANIFEST] = json.dumps({**manifest, "files": files}, indent=2, ensure_ascii=False) + "\n"
    writes["openwish/config.json"] = json.dumps({**config, "version": SCHEMA_VERSION},
                                                indent=2, ensure_ascii=False) + "\n"
    if POLICY in writes and any(contained(root, "openwish/changes").glob("*/review.json")):
        notes.append("Recorded reviews digested the old policy and are now stale; refresh any still "
                     "pending before closing.")
    return {"from": version, "writes": writes, "removals": removals, "notes": notes}


def apply_migration(root, plan):
    """Write the preflighted plan; the schema version is written last, so a rerun resumes safely."""
    config = plan["writes"]["openwish/config.json"]
    for relative, text in plan["writes"].items():
        if relative != "openwish/config.json":
            write_text(contained(root, relative), text)
    for relative in plan["removals"]:
        contained(root, relative).unlink()
    write_text(contained(root, "openwish/config.json"), config)
