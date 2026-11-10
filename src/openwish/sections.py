"""Markdown outlines and single sections, so a session reads part of a large doc."""

import re

from .model import estimate_tokens
from .storage import WishError, contained

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE = re.compile(r"^(```|~~~)")


def slug(heading):
    """GitHub's heading anchor: lowercase, punctuation dropped, each whitespace character a hyphen."""
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", heading.strip().lower()))


def outline(text):
    """Each heading outside code fences, with its text up to the next heading of the same or a higher level."""
    lines = text.split("\n")
    found, seen, fenced = [], {}, False
    for index, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
        match = None if fenced else HEADING.match(line)
        if match:
            anchor = slug(match.group(2))
            count = seen.get(anchor, 0)
            seen[anchor] = count + 1
            found.append({"level": len(match.group(1)), "title": match.group(2).strip(),
                          "anchor": f"{anchor}-{count}" if count else anchor, "start": index})
    for position, section in enumerate(found):
        end = next((other["start"] for other in found[position + 1:] if other["level"] <= section["level"]),
                   len(lines))
        section["text"] = "\n".join(lines[section["start"]:end]).rstrip()
    return found


def read_sections(root, targets):
    """`path` gives an outline with estimated sizes; `path#anchor` gives that section and its subsections."""
    output = []
    for target in targets:
        relative, _, anchor = target.partition("#")
        path = contained(root, relative)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise WishError(f"Cannot read {relative}: {error}") from error
        sections = outline(text)
        if not anchor:
            output.append(f"{relative}: ~{estimate_tokens(text)} tokens")
            output.extend(f"{'  ' * (section['level'] - 1)}#{section['anchor']}  "
                          f"~{estimate_tokens(section['text'])}  {section['title']}" for section in sections)
            continue
        match = next((section for section in sections if section["anchor"] == anchor), None)
        if match is None:
            raise WishError(f"No section #{anchor} in {relative}; run `ow section {relative}` for its outline.")
        output.append(f"<!-- {relative}#{anchor} -->\n{match['text']}\n")
    return "\n".join(output)
