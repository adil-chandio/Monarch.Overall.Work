#!/usr/bin/env python3
"""Packages a Kaggle Dual-T4 (GPU T4 x2) notebook + kernel-metadata.json."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO_URL = "https://github.com/adil-chandio/Monarch.Overall.Work.git"
DEFAULT_BRANCH = "arena/9960286a-monarch-overall-work"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def build_notebook(scenes_csv: str, branch: str) -> dict:
    code = f'''# Auto-generated MONARCH Dual-T4 (2x 16GB) Parallel I2V Kernel
import json, os, pathlib, shutil, subprocess, sys

BRANCH = "{branch}"
REPO = "{REPO_URL}"
SCENES = [s.strip() for s in "{scenes_csv}".split(",") if s.strip()]

repo = pathlib.Path("/kaggle/working/monarch_repo")
if repo.exists():
    shutil.rmtree(repo)
subprocess.run(["git", "clone", "--depth", "1", "-b", BRANCH, REPO, str(repo)], check=True)

# Pre-install shared packages once before spawning per-GPU workers
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-U",
     "diffusers>=0.33.0", "transformers>=4.49.0", "accelerate>=1.2.0",
     "huggingface_hub", "imageio-ffmpeg", "ftfy", "sentencepiece", "safetensors", "protobuf"],
    check=True,
)

# Pre-warm LTX-Video weights once into shared HF cache so GPU-0 and GPU-1 never race on cache locks
from huggingface_hub import snapshot_download
print("Pre-warming Lightricks/LTX-Video into local SSD cache...", flush=True)
snapshot_download("Lightricks/LTX-Video")

import torch
n_gpu = torch.cuda.device_count()
print("DETECTED GPUS:", n_gpu, [torch.cuda.get_device_name(i) for i in range(n_gpu)], flush=True)

if n_gpu >= 2 and len(SCENES) > 1:
    mid = (len(SCENES) + 1) // 2
    groups = [SCENES[:mid], SCENES[mid:]]
else:
    groups = [SCENES]

procs = []
for idx, grp in enumerate(groups):
    wdir = f"/kaggle/working/worker_{{idx}}"
    cmd = [
        sys.executable,
        str(repo / "gpu-engine/kaggle/run_b2b_i2v.py"),
        "--only", ",".join(grp),
        "--out", wdir,
    ]
    env = dict(os.environ)
    # Stagger model download cache lock slightly on worker 1
    if idx == 1:
        import time
        time.sleep(8)
    if len(groups) > 1:
        env["CUDA_VISIBLE_DEVICES"] = str(idx)
    print("LAUNCHING:", cmd, "GPU=", env.get("CUDA_VISIBLE_DEVICES", "0"), flush=True)
    procs.append(subprocess.Popen(cmd, env=env))

codes = [p.wait() for p in procs]
print("WORKER EXIT CODES:", codes, flush=True)

final_out = pathlib.Path("/kaggle/working/clips")
final_out.mkdir(parents=True, exist_ok=True)
for idx in range(len(groups)):
    wpath = pathlib.Path(f"/kaggle/working/worker_{{idx}}")
    if wpath.exists():
        for item in wpath.iterdir():
            shutil.copy2(item, final_out / item.name)

# Clean cloned repo and temp worker dirs so /kaggle/working output stays tiny for instant download
shutil.rmtree(repo, ignore_errors=True)
for idx in range(len(groups)):
    shutil.rmtree(f"/kaggle/working/worker_{{idx}}", ignore_errors=True)
produced = sorted(p.name for p in final_out.glob("*.mp4"))
print("PRODUCED_CLIPS:", produced, flush=True)
if not produced or any(c != 0 for c in codes):
    raise SystemExit(f"Incomplete render: codes={{codes}}, clips={{produced}}")
'''
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code.splitlines(True),
            }
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--only", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.slug)
    (out / "main.ipynb").write_text(json.dumps(build_notebook(args.only, args.branch), indent=1) + "\n")

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
        "machine_shape": "NvidiaTeslaT4",
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"Packaged Dual-T4 kernel {meta['id']} ({args.only}) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
