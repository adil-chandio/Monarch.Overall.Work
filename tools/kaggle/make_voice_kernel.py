#!/usr/bin/env python3
"""Package the v3 voice-alignment kernel for Kaggle GPU T4 x2.

Why this exists: the film's captions must be *measured*, not guessed. Whisper
large-v3 with word timestamps on a real T4 gives per-word start/end; we then
build an SRT from those numbers instead of eyeballing line breaks.

The kernel is self-contained: the seven VO mp3s are base64-embedded, because a
private repo cannot be cloned from inside Kaggle.
"""
from __future__ import annotations

import argparse
import base64
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
VO_DIR = ROOT / "public/demo/vo"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def gather_vo() -> dict[str, str]:
    files = sorted(VO_DIR.glob("*.mp3"))
    if not files:
        raise SystemExit(f"no VO mp3s in {VO_DIR}")
    return {f.name: base64.b64encode(f.read_bytes()).decode() for f in files}


def build_notebook() -> dict:
    timing = json.loads((VO_DIR / "timing.json").read_text())
    payload = json.dumps(gather_vo())

    code = f'''# MONARCH v3 — GPU word-level alignment (Whisper large-v3) on Kaggle T4 x2
import base64, json, os, pathlib, subprocess, sys, time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
OUT = pathlib.Path("/kaggle/working/monarch_out")
OUT.mkdir(parents=True, exist_ok=True)
VO = pathlib.Path("/kaggle/working/vo")
VO.mkdir(parents=True, exist_ok=True)

PAYLOAD = json.loads({json.dumps(payload)})
TIMING = json.loads({json.dumps(json.dumps(timing))})
for name, b64 in PAYLOAD.items():
    (VO / name).write_bytes(base64.b64decode(b64))
print("unpacked VO files:", sorted(p.name for p in VO.glob("*.mp3")), flush=True)

# Kaggle's image already carries torch/ctranslate2; install only what is
# missing, and let pip TALK when it fails (a quiet pip cost two runs).
def ensure(module, spec):
    try:
        __import__(module)
        return f"{{spec}}: present"
    except Exception:
        pass
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-input",
                        "--no-cache-dir", "--disable-pip-version-check",
                        "--break-system-packages", spec],
                       capture_output=True, text=True)
    print(f"pip {{spec}} rc={{r.returncode}}", flush=True)
    if r.returncode != 0:
        print((r.stdout or "")[-1500:], flush=True)
        print((r.stderr or "")[-1500:], flush=True)
    return f"{{spec}}: rc={{r.returncode}}"

install_log = [ensure("faster_whisper", "faster-whisper>=1.0.3"),
               ensure("ctranslate2", "ctranslate2>=4.4.0")]
print(install_log, flush=True)

receipt = {{"stage": "gpu", "python": os.sys.version.split()[0]}}
try:
    import torch
    receipt["torch"] = torch.__version__
    receipt["cuda_available"] = bool(torch.cuda.is_available())
    receipt["gpu_count"] = int(torch.cuda.device_count())
    receipt["devices"] = []
    for i in range(torch.cuda.device_count()):
        p = torch.cuda.get_device_properties(i)
        receipt["devices"].append({{"index": i, "name": p.name,
                                   "vram_gb": round(p.total_memory / 1024**3, 2),
                                   "cc": f"{{p.major}}.{{p.minor}}"}})
except Exception as exc:
    receipt["torch_error"] = str(exc)
try:
    receipt["nvidia_smi"] = subprocess.run(["nvidia-smi", "-L"], capture_output=True,
                                           text=True, timeout=30).stdout.strip()
except Exception as exc:
    receipt["nvidia_smi"] = f"unavailable: {{exc}}"
print(json.dumps(receipt, indent=1), flush=True)

receipt["install"] = install_log

backend = ""
model = None
t0 = time.time()
try:
    from faster_whisper import WhisperModel
    model = WhisperModel("large-v3", device="cuda", compute_type="float16",
                         download_root="/kaggle/working/models")
    backend = "faster-whisper large-v3 float16 cuda"
except Exception as exc:
    receipt["faster_whisper_error"] = f"{{type(exc).__name__}}: {{str(exc)[:400]}}"
    print("faster-whisper unusable ->", receipt["faster_whisper_error"], flush=True)

if model is None:
    # second backend: whatever Kaggle's image already ships
    import torch, whisper
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("large-v3", device=device)
    backend = f"openai-whisper large-v3 {{device}}"

receipt["model_load_s"] = round(time.time() - t0, 2)
receipt["model"] = backend
print("backend:", backend, flush=True)

beats = []
audio_total = 0.0
for idx, (name, start) in enumerate(zip(sorted(PAYLOAD), TIMING["starts"])):
    t0 = time.time()
    words, text_parts, seg_rows = [], [], []
    if backend.startswith("faster-whisper"):
        segments, info = model.transcribe(
            str(VO / name), language="hi", task="transcribe", word_timestamps=True,
            vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for seg in segments:
            seg_rows.append({{"start": round(seg.start, 3), "end": round(seg.end, 3),
                             "text": seg.text.strip()}})
            text_parts.append(seg.text.strip())
            for w in (seg.words or []):
                words.append({{"w": w.word.strip(), "s": round(w.start, 3),
                              "e": round(w.end, 3), "p": round(float(w.probability), 3)}})
        dur = float(info.duration)
        lang, lang_prob = info.language, float(info.language_probability)
    else:
        res = model.transcribe(str(VO / name), language="hi", word_timestamps=True,
                               verbose=False)
        dur = float(res.get("duration") or 0.0)
        lang, lang_prob = "hi", 1.0
        for seg in res.get("segments", []):
            seg_rows.append({{"start": round(seg["start"], 3), "end": round(seg["end"], 3),
                             "text": str(seg.get("text", "")).strip()}})
            text_parts.append(str(seg.get("text", "")).strip())
            for w in seg.get("words", []) or []:
                words.append({{"w": str(w.get("word", "")).strip(),
                              "s": round(float(w.get("start", 0)), 3),
                              "e": round(float(w.get("end", 0)), 3),
                              "p": round(float(w.get("probability", 0)), 3)}})
    audio_total += dur
    beat = {{
        "file": name,
        "offset": round(float(start), 3),
        "duration": round(dur, 3),
        "lang": lang,
        "lang_prob": round(lang_prob, 3),
        "text": " ".join(text_parts).strip(),
        "segments": seg_rows,
        "words": words,
        "rtf": round((time.time() - t0) / max(dur, 0.01), 4),
    }}
    beats.append(beat)
    print(f"[{{idx+1}}/{{len(PAYLOAD)}}] {{name}}  {{dur:.2f}}s  rtf={{beat['rtf']}}  words={{len(words)}}", flush=True)

receipt["audio_total_s"] = round(audio_total, 3)
receipt["wall_s"] = round(time.time() - t0, 2)
receipt["words"] = sum(len(b["words"]) for b in beats)
receipt["mean_word_prob"] = round(sum(w["p"] for b in beats for w in b["words"]) /
                                  max(receipt["words"], 1), 3)

(OUT / "words.json").write_text(json.dumps({{"beats": beats, "total": TIMING["total"]}}, indent=1))
(OUT / "receipts_gpu.json").write_text(json.dumps(receipt, indent=1))
print("WROTE", sorted(p.name for p in OUT.iterdir()), flush=True)
print(json.dumps({{k: receipt[k] for k in ("gpu_count", "devices", "words", "mean_word_prob", "wall_s")}}, indent=1), flush=True)
'''
    return {
        "cells": [
            {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
             "source": code.splitlines(keepends=True)},
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--slug", default="monarch-v3-voice")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.slug)
    nb = build_notebook()
    # fail here, not 30 minutes later inside Kaggle: the kernel must compile and
    # every stdlib module it names must be imported.
    import ast

    src = "".join(nb["cells"][0]["source"])
    tree = ast.parse(src)
    imported = {a.name.split(".")[0] for n in ast.walk(tree)
                if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module.split(".")[0] for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    named = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    missing = sorted(m for m in ("sys", "json", "os", "pathlib", "subprocess", "time",
                                 "base64", "re") if m in named and m not in imported)
    if missing:
        raise SystemExit(f"kernel names {missing} without importing them")
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
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"packaged {meta['id']} (gpu T4 x2) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
