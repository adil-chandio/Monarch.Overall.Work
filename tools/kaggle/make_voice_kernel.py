#!/usr/bin/env python3
"""Package tools/kaggle/voice_kernel.py as a Kaggle GPU (T4 x2) notebook.

The kernel body lives in its own file so it can be compiled here; this script
only substitutes the data (the seven VO mp3s, base64'd, because a private repo
cannot be cloned from inside Kaggle) and writes kernel-metadata.json.

Refuses to package anything that does not compile, that names a stdlib module it
never imports, or that still contains a placeholder.
"""
from __future__ import annotations

import argparse
import ast
import base64
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
KERNEL = ROOT / "tools/kaggle/voice_kernel.py"
VO_DIR = ROOT / "public/demo/vo"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def build_source() -> str:
    timing = json.loads((VO_DIR / "timing.json").read_text())
    files = sorted(VO_DIR.glob("*.mp3"))
    if len(files) != len(timing["starts"]):
        raise SystemExit(f"{len(files)} VO files but {len(timing['starts'])} starts")
    payload = {f.name: base64.b64encode(f.read_bytes()).decode() for f in files}

    src = KERNEL.read_text()
    src = src.replace("__PAYLOAD__", json.dumps(payload))
    src = src.replace("__TIMING__", json.dumps(timing))

    if "__PAYLOAD__" in src or "__TIMING__" in src:
        raise SystemExit("placeholder substitution failed")

    tree = ast.parse(src)  # must compile: a broken kernel costs a GPU run
    imported = {a.name.split(".")[0] for n in ast.walk(tree)
                if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module.split(".")[0] for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    named = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    missing = sorted(m for m in ("sys", "json", "os", "pathlib", "subprocess", "time",
                                 "base64") if m in named and m not in imported)
    if missing:
        raise SystemExit(f"kernel names {missing} without importing them")
    return src


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--slug", default="monarch-v3-voice")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = build_source()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.slug)

    nb = {
        "cells": [{"cell_type": "code", "id": "align",
                   "metadata": {}, "execution_count": None, "outputs": [],
                   "source": src.splitlines(keepends=True)}],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (out / "main.ipynb").write_text(json.dumps(nb, indent=1) + "\n")

    meta = {
        "id": f"{args.user}/{slug}",
        "title": slug,
        "code_file": "main.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        # this is what pins GPU T4 x2 instead of the legacy P100 default
        "machine_shape": "NvidiaTeslaT4",
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"packaged {meta['id']} (machine_shape NvidiaTeslaT4, {len(src):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
