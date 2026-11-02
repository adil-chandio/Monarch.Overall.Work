#!/usr/bin/env python3
"""Packages a self-contained Kaggle Dual-T4 (GPU T4 x2) notebook (embeds code + keyframes, zero git clone needed)."""
from __future__ import annotations

import argparse
import base64
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def build_notebook(scenes_csv: str) -> dict:
    wanted = [s.strip() for s in scenes_csv.split(",") if s.strip()]
    job_data = json.loads((ROOT / "gpu-engine/b2b_job.json").read_text())
    worker_py = (ROOT / "gpu-engine/kaggle/run_b2b_i2v.py").read_text()

    from io import BytesIO
    from PIL import Image

    # Embed code + crisp 1024x576 q=94 keyframes (~250 KB total -> well under Kaggle's 1MB .ipynb API cap!)
    embedded_files: dict[str, str] = {
        "gpu-engine/b2b_job.json": base64.b64encode(json.dumps(job_data).encode()).decode(),
        "gpu-engine/kaggle/run_b2b_i2v.py": base64.b64encode(worker_py.encode()).decode(),
    }
    for sc in job_data["scenes"]:
        if sc["id"] in wanted:
            kf = ROOT / sc["image"]
            buf = BytesIO()
            Image.open(kf).convert("RGB").resize((1024, 576), Image.Resampling.LANCZOS).save(buf, format="JPEG", quality=94)
            embedded_files[sc["image"]] = base64.b64encode(buf.getvalue()).decode()

    payload_json = json.dumps(embedded_files)

    code = f'''# Auto-generated self-contained MONARCH Dual-T4 Parallel I2V Kernel
import base64, gc, json, os, pathlib, shutil, socket, subprocess, sys, time, urllib.request

# CRITICAL: Use default ~/.cache/huggingface (container root SSD, ~50GB+), NEVER /tmp (tmpfs RAM!).
os.environ["TOKENIZERS_PARALLELISM"] = "false"

SCENES = {json.dumps(wanted)}
PAYLOAD = json.loads({json.dumps(payload_json)})

repo = pathlib.Path("/kaggle/working/_monarch_repo")
if repo.exists():
    shutil.rmtree(repo)
for rel_path, b64_data in PAYLOAD.items():
    dest = repo / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(b64_data))
print("Unpacked embedded repo files:", len(PAYLOAD), flush=True)

import torch
n_gpu = torch.cuda.device_count()
gpu_names = [torch.cuda.get_device_name(i) for i in range(n_gpu)]
print(f"GPU_INFO: cuda={{torch.cuda.is_available()}} count={{n_gpu}} names={{gpu_names}}", flush=True)

try:
    urllib.request.urlopen("https://huggingface.co", timeout=8)
    net_ok = True
    net_err = ""
except Exception as ne:
    net_ok = False
    net_err = f"{{type(ne).__name__}}: {{ne}}"
print(f"NET_INFO: ok={{net_ok}} err={{net_err}}", flush=True)

if n_gpu == 0:
    raise RuntimeError(f"NO_GPU_ALLOCATED on Kaggle account (GPU_INFO count=0, net_ok={{net_ok}}). Account may need Kaggle Phone Verification for GPU+Internet.")
if not net_ok:
    raise RuntimeError(f"NO_INTERNET_IN_KERNEL ({{net_err}}). GPU count={{n_gpu}} {{gpu_names}}.")

# Install/verify diffusers>=0.32.2 without breaking preinstalled torch
r_pip = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q",
     "diffusers>=0.32.2", "transformers>=4.49,<5.0", "accelerate",
     "imageio-ffmpeg", "ftfy", "sentencepiece", "safetensors", "regex"],
    capture_output=True, text=True,
)
print("PIP_RC:", r_pip.returncode, r_pip.stderr[-300:] if r_pip.returncode else "ok", flush=True)

try:
    from diffusers import LTXImageToVideoPipeline
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print("Pre-caching LTXImageToVideoPipeline onto root SSD...", flush=True)
    _p = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=dtype)
    del _p
    gc.collect()
    torch.cuda.empty_cache()
except Exception as pre_exc:
    print("Pre-cache note:", type(pre_exc).__name__, str(pre_exc)[:300], flush=True)

if n_gpu >= 2 and len(SCENES) > 1:
    mid = (len(SCENES) + 1) // 2
    groups = [SCENES[:mid], SCENES[mid:]]
else:
    groups = [SCENES]

procs = []
log_files = []
for idx, grp in enumerate(groups):
    if idx == 1:
        # Stagger worker 1 by 35s so T5-XXL CPU shard load never overlaps with worker 0
        time.sleep(35)
    wdir = f"/kaggle/working/_worker_{{idx}}"
    pathlib.Path(wdir).mkdir(parents=True, exist_ok=True)
    wlog = open(f"/kaggle/working/worker_{{idx}}.txt", "w")
    log_files.append(wlog)
    cmd = [
        sys.executable,
        str(repo / "gpu-engine/kaggle/run_b2b_i2v.py"),
        "--job", str(repo / "gpu-engine/b2b_job.json"),
        "--only", ",".join(grp),
        "--out", wdir,
    ]
    env = dict(os.environ)
    if len(groups) > 1:
        env["CUDA_VISIBLE_DEVICES"] = str(idx)
    print("LAUNCHING:", cmd, "GPU=", env.get("CUDA_VISIBLE_DEVICES", "0"), flush=True)
    procs.append(subprocess.Popen(cmd, env=env, stdout=wlog, stderr=subprocess.STDOUT))

codes = [p.wait() for p in procs]
for lf in log_files:
    lf.close()

for idx in range(len(groups)):
    txt = pathlib.Path(f"/kaggle/working/worker_{{idx}}.txt").read_text(errors="ignore")
    print(f"=== WORKER {{idx}} LOG ===", flush=True)
    print(txt[-2500:], flush=True)

print("WORKER EXIT CODES:", codes, flush=True)

final_out = pathlib.Path("/kaggle/working/clips")
final_out.mkdir(parents=True, exist_ok=True)
for idx in range(len(groups)):
    wpath = pathlib.Path(f"/kaggle/working/_worker_{{idx}}")
    if wpath.exists():
        for item in wpath.iterdir():
            shutil.copy2(item, final_out / item.name)
    shutil.rmtree(wpath, ignore_errors=True)

# Remove temp repo before notebook exit so /kaggle/working only holds tiny MP4 clips
shutil.rmtree(repo, ignore_errors=True)

produced = sorted(p.name for p in final_out.glob("*.mp4"))
print("PRODUCED_CLIPS:", produced, flush=True)
if not produced:
    raise SystemExit(f"Zero clips produced: codes={{codes}}")
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
    ap.add_argument("--branch", default="")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.slug)
    (out / "main.ipynb").write_text(json.dumps(build_notebook(args.only), indent=1) + "\n")

    meta = {
        "id": f"{args.user}/{slug}",
        "title": slug,
        "code_file": "main.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"Packaged self-contained Dual-T4 kernel {meta['id']} ({args.only}) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
