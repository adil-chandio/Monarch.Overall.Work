#!/usr/bin/env python3
"""One source of truth for the skill pack; generate the per-tool copies.

The upstream repo shipped the same 269 files twice - once under .claude/skills and
once under .cursor/skills - and the two trees were byte-identical. Every edit had to
be made twice or the tools silently diverged. This keeps a single canonical tree in
skills/ and materialises the copies a tool expects.

    python3 build.py           # regenerate tool copies
    python3 build.py --check   # fail if a copy has drifted
"""
from __future__ import annotations

import argparse
import filecmp
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
CANON = ROOT / "skills"

# tool -> directory it reads skills from, relative to the pack root
TARGETS = {
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
}


def copy_tree(dst: pathlib.Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CANON, dst)


def diff_tree(a: pathlib.Path, b: pathlib.Path) -> list[str]:
    if not b.exists():
        return [f"{b} is missing"]
    cmp = filecmp.dircmp(a, b)
    out: list[str] = []

    def walk(c: filecmp.dircmp, prefix: str = "") -> None:
        for name in c.left_only:
            out.append(f"only in canonical: {prefix}{name}")
        for name in c.right_only:
            out.append(f"only in generated: {prefix}{name}")
        for name in c.diff_files:
            out.append(f"differs: {prefix}{name}")
        for name, sub in c.subdirs.items():
            walk(sub, f"{prefix}{name}/")

    walk(cmp)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify generated copies match the canonical tree")
    args = ap.parse_args()

    if not CANON.is_dir():
        print(f"no canonical skills tree at {CANON}", file=sys.stderr)
        return 2

    n = len([p for p in CANON.iterdir() if (p / "SKILL.md").exists()])

    if args.check:
        bad = 0
        for tool, rel in TARGETS.items():
            d = ROOT / rel
            drift = diff_tree(CANON, d)
            if drift:
                bad += 1
                print(f"{tool}: {len(drift)} difference(s)")
                for line in drift[:10]:
                    print(f"  {line}")
            else:
                print(f"{tool}: in sync")
        return 1 if bad else 0

    for tool, rel in TARGETS.items():
        copy_tree(ROOT / rel)
        print(f"{tool}: wrote {rel} ({n} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
