#!/usr/bin/env python3
"""Packages a zero-OOM Kaggle Dual-T4 (GPU T4 x2) notebook:
1. Pre-encodes T5-XXL prompt embeddings once on GPU 0 (0.8s) and frees 9.5GB T5-XXL completely.
2. Spawns 2 lightweight GPU workers (text_encoder=None -> only 4.8GB VRAM & <2.5GB CPU RAM each!).
"""
from __future__ import annotations

import argparse
import base64
from io import BytesIO
import json
import pathlib
import re
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def build_notebook(scenes_csv: str) -> dict:
    wanted = [s.strip() for s in scenes_csv.split(",") if s.strip()]
    job_data = json.loads((ROOT / "production/mafia-temple/job.json").read_text())
    worker_py = (ROOT / "production/mafia-temple/worker.py").read_text()

    embedded_files: dict[str, str] = {
        "production/mafia-temple/job.json": base64.b64encode(json.dumps(job_data).encode()).decode(),
        "production/mafia-temple/worker.py": base64.b64encode(worker_py.encode()).decode(),
    }
    for sc in job_data["scenes"]:
        if sc["id"] in wanted:
            kf = ROOT / sc["image"]
            buf = BytesIO()
            Image.open(kf).convert("RGB").resize((1024, 576), Image.Resampling.LANCZOS).save(buf, format="JPEG", quality=94)
            embedded_files[sc["image"]] = base64.b64encode(buf.getvalue()).decode()

    payload_json = json.dumps(embedded_files)

    code = f'''# Auto-generated Zero-OOM MONARCH Dual-T4 Parallel I2V Kernel
import base64, gc, json, os, pathlib, shutil, subprocess, sys, time, urllib.request

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

if n_gpu == 0:
    raise RuntimeError("NO_GPU_ALLOCATED on Kaggle account.")

r_pip = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q",
     "diffusers>=0.32.2", "transformers>=4.49,<5.0", "accelerate",
     "imageio-ffmpeg", "ftfy", "sentencepiece", "safetensors", "regex"],
    capture_output=True, text=True,
)
print("PIP_RC:", r_pip.returncode, r_pip.stderr[-300:] if r_pip.returncode else "ok", flush=True)

# PHASE 1: Load ONLY T5-XXL text encoder once, compute embeddings for our scenes in <2s, then FREE 9.5GB RAM!
from diffusers import LTXImageToVideoPipeline
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
job = json.loads((repo / "production/mafia-temple/job.json").read_text())
emb_dir = pathlib.Path("/kaggle/working/_embeds")
emb_dir.mkdir(parents=True, exist_ok=True)

print("Phase 1: Encoding T5-XXL prompts once & freeing 9.5GB RAM...", flush=True)
enc_pipe = LTXImageToVideoPipeline.from_pretrained(
    "Lightricks/LTX-Video", transformer=None, vae=None, torch_dtype=dtype
)
enc_pipe.to("cuda:0")
neg = job.get("negative", "blurry, low quality, text, watermark")
with torch.no_grad():
    for sc in job["scenes"]:
        if sc["id"] not in SCENES:
            continue
        prompt = f"{{sc['prompt']}}, {{job.get('style', '')}}".strip(", ")
        pe, pam, npe, npam = enc_pipe.encode_prompt(
            prompt=prompt,
            negative_prompt=neg,
            do_classifier_free_guidance=True,
            num_videos_per_prompt=1,
            device=torch.device("cuda:0"),
            dtype=dtype,
        )
        torch.save(
            {{
                "prompt_embeds": pe.cpu(),
                "prompt_attention_mask": pam.cpu(),
                "negative_prompt_embeds": npe.cpu(),
                "negative_prompt_attention_mask": npam.cpu(),
            }},
            emb_dir / f"{{sc['id']}}.pt",
        )
        print("  encoded", sc["id"], tuple(pe.shape), flush=True)

del enc_pipe
gc.collect()
torch.cuda.empty_cache()

# Pre-download lightweight 4.8GB Transformer + VAE shards once so GPU workers load from SSD without race
print("Phase 2: Pre-caching 4.8GB Transformer + VAE shards...", flush=True)
_vp = LTXImageToVideoPipeline.from_pretrained(
    "Lightricks/LTX-Video", text_encoder=None, tokenizer=None, torch_dtype=dtype
)
del _vp
gc.collect()
torch.cuda.empty_cache()

if n_gpu >= 2 and len(SCENES) > 1:
    mid = (len(SCENES) + 1) // 2
    groups = [SCENES[:mid], SCENES[mid:]]
else:
    groups = [SCENES]

procs = []
log_files = []
for idx, grp in enumerate(groups):
    wdir = f"/kaggle/working/_worker_{{idx}}"
    pathlib.Path(wdir).mkdir(parents=True, exist_ok=True)
    wlog = open(f"/kaggle/working/worker_{{idx}}.txt", "w")
    log_files.append(wlog)
    cmd = [
        sys.executable,
        str(repo / "production/mafia-temple/worker.py"),
        "--job", str(repo / "production/mafia-temple/job.json"),
        "--embeds", str(emb_dir),
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

shutil.rmtree(emb_dir, ignore_errors=True)
shutil.rmtree(repo, ignore_errors=True)

produced = sorted(p.name for p in final_out.glob("*.mp4"))
print("PRODUCED_CLIPS:", produced, flush=True)
if len(produced) < len(SCENES) or any(c != 0 for c in codes):
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
        "machine_shape": "NvidiaTeslaT4",
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"Packaged Zero-OOM Dual-T4 kernel {meta['id']} ({args.only}) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
