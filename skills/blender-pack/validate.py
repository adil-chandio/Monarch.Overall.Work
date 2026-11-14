#!/usr/bin/env python3
"""Structural validation for the skill pack. Fast, no dependencies, CI-ready.

Upstream had 48 of 95 skills that were a title and one sentence, a `related-skills`
entry pointing at a skill that does not exist, and a directory with no SKILL.md
sitting inside the skills tree pretending to be one. None of that fails loudly: the
tool loads the pack, finds a skill, and the agent produces work with no direction.

    python3 validate.py          # human output
    python3 validate.py --quiet  # exit code only
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SKILLS = ROOT / "skills"

REQUIRED = ("name", "description")
MIN_BODY_LINES = 40


def frontmatter(text: str):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else (None, text)


def field(front: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", front, re.M)
    return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    problems: list[str] = []
    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    names = {p.name for p in dirs}

    for d in dirs:
        f = d / "SKILL.md"
        if not f.exists():
            problems.append(f"{d.name}: directory has no SKILL.md")
            continue
        text = f.read_text()
        front, body = frontmatter(text)
        if front is None:
            problems.append(f"{d.name}: no YAML frontmatter")
            continue

        for key in REQUIRED:
            if not field(front, key):
                problems.append(f"{d.name}: missing `{key}`")
        if field(front, "name") != d.name:
            problems.append(
                f"{d.name}: name field is `{field(front, 'name')}`, "
                f"which does not match the directory")

        body_lines = len([l for l in body.splitlines() if l.strip()])
        if body_lines < MIN_BODY_LINES:
            problems.append(
                f"{d.name}: body is {body_lines} non-blank lines, "
                f"under the {MIN_BODY_LINES} minimum")

        for rel in field(front, "related-skills").split(","):
            rel = rel.strip()
            if rel and rel not in names:
                problems.append(f"{d.name}: related-skills points at `{rel}`, "
                                f"which does not exist")

        # every relative markdown link must resolve
        for m in re.finditer(r"\]\((\.\.[^)]+\.md)\)", text):
            target = (d / m.group(1)).resolve()
            if not target.exists():
                problems.append(f"{d.name}: broken link {m.group(1)}")

        if "blender-version-contract" not in text:
            problems.append(f"{d.name}: does not pin the Blender API contract")

    # duplicate keys inside frontmatter would be silently dropped by a YAML loader
    for d in dirs:
        f = d / "SKILL.md"
        if not f.exists():
            continue
        front, _ = frontmatter(f.read_text())
        if not front:
            continue
        seen: dict[str, int] = {}
        for line in front.splitlines():
            m = re.match(r"^(\s*)([a-z][a-z-]*):", line)
            if m:
                indent, key = m.group(1), m.group(2)
                if indent == "  ":  # metadata block
                    seen[key] = seen.get(key, 0) + 1
        for key, count in seen.items():
            if count > 1:
                problems.append(f"{d.name}: duplicate metadata key `{key}` "
                                f"({count}x) - a YAML loader keeps only the last")

    if not args.quiet:
        total = len(dirs)
        if problems:
            print(f"FAIL  {len(problems)} problem(s) across {total} skills\n")
            for p in problems:
                print(f"  {p}")
        else:
            print(f"PASS  {total} skills · frontmatter, refs, links, "
                  f"related-skills, API contract")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
