#!/usr/bin/env python3
"""
MONARCH® Flagship B2B I2V GPU Worker (Runs inside Kaggle GPU T4 x2)
Generates real 49-frame 16:9 widescreen AI motion clips from locked 2K keyframes
using Wan 2.2 TI2V-5B (with automatic sequential offload + LTX-Video 2B fallback).
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def ensure_deps() -> None:
    import importlib

    pkgs = []
    for mod, pkg in (
        ("diffusers", "diffusers>=0.32"),
        ("transformers", "transformers>=4.49"),
        ("accelerate", "accelerate"),
        ("imageio_ffmpeg", "imageio-ffmpeg"),
        ("ftfy", "ftfy"),
        ("sentencepiece", "sentencepiece"),
        ("safetensors", "safetensors"),
    ):
        try:
            importlib.import_module(mod)
        except ModuleNotFoundError:
            pkgs.append(pkg)
    if pkgs:
        log(f"Installing missing packages: {' '.join(pkgs)}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pkgs], check=False)


class MotionEngine:
    def __init__(self, job: dict):
        import torch

        self.torch = torch
        self.job = job
        # Use bfloat16 for LTX-Video / Wan2.2 T5/UMT5 numerical stability; VAE tiled for 16GB T4
        self.dtype = torch.bfloat16
        self.pipe = None
        self.kind = None
        self.width = 768
        self.height = 448
        self.frames = 49
        self.steps = 28
        log(f"CUDA device: {torch.cuda.get_device_name(0)} | dtype={self.dtype}")

    def load_wan(self, sequential: bool = False) -> None:
        from diffusers import AutoencoderKLWan, WanImageToVideoPipeline

        torch = self.torch
        model_id = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
        log(f"Loading {model_id} (sequential={sequential}, dtype={self.dtype})...")
        vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
        pipe = WanImageToVideoPipeline.from_pretrained(model_id, vae=vae, torch_dtype=self.dtype)
        if sequential:
            pipe.enable_sequential_cpu_offload()
        else:
            pipe.enable_model_cpu_offload()
        try:
            pipe.enable_attention_slicing("max")
        except Exception:
            pass
        try:
            pipe.vae.enable_tiling()
            pipe.vae.enable_slicing()
        except Exception:
            pass
        pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe
        self.kind = "wan22_ti2v_5b"

    def load_ltx(self) -> None:
        from diffusers import LTXImageToVideoPipeline

        log("Loading Lightricks/LTX-Video (768x448, 49f, 28 steps, T4-native model offload)...")
        pipe = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=self.dtype)
        pipe.enable_model_cpu_offload()
        try:
            pipe.vae.enable_tiling()
        except Exception:
            pass
        pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe
        self.kind = "ltx_i2v_2b"
        self.width, self.height, self.frames = 768, 448, 49

    def ensure_loaded(self) -> None:
        if self.pipe is not None:
            return
        try:
            self.load_ltx()
        except Exception as exc:
            log(f"LTX-Video load issue ({type(exc).__name__}: {str(exc)[:220]}) -> falling back to Wan 2.2...")
            gc.collect()
            self.torch.cuda.empty_cache()
            self.width, self.height, self.frames, self.steps = 832, 480, 33, 12
            self.load_wan(sequential=True)

    def generate_clip(self, scene: dict, img_path: pathlib.Path, out_mp4: pathlib.Path) -> dict:
        from diffusers.utils import export_to_video, load_image

        torch = self.torch
        self.ensure_loaded()
        prompt = f"{scene['prompt']}, {self.job.get('style', '')}".strip(", ")
        neg = self.job.get("negative", "blurry, low quality, text, watermark")
        seed = int(scene.get("seed", 42))

        for attempt in range(1, 4):
            try:
                img = load_image(str(img_path)).resize((self.width, self.height))
                gen = torch.Generator("cpu").manual_seed(seed)
                t0 = time.time()
                with torch.no_grad():
                    if self.kind == "wan22_ti2v_5b":
                        frames = self.pipe(
                            image=img,
                            prompt=prompt,
                            negative_prompt=neg,
                            height=self.height,
                            width=self.width,
                            num_frames=self.frames,
                            num_inference_steps=self.steps,
                            guidance_scale=5.0,
                            generator=gen,
                        ).frames[0]
                    else:
                        frames = self.pipe(
                            image=img,
                            prompt=prompt,
                            negative_prompt=neg,
                            height=self.height,
                            width=self.width,
                            num_frames=self.frames,
                            num_inference_steps=28,
                            guidance_scale=3.2,
                            decode_timestep=0.03,
                            decode_noise_scale=0.025,
                            generator=gen,
                        ).frames[0]

                raw_tmp = out_mp4.with_suffix(".raw.mp4")
                import numpy as np
                f0 = np.asarray(frames[0], dtype=np.float32)
                f_last = np.asarray(frames[-1], dtype=np.float32)
                luma = float(np.mean(f0))
                motion_delta = float(np.mean(np.abs(f_last - f0)))
                log(f"QC {scene['id']}: luma={luma:.1f}, motion_delta={motion_delta:.2f}")
                if not np.isfinite(luma) or luma < 3.0:
                    raise RuntimeError(f"Dark/NaN frame detected (luma={luma}) — triggering fallback")
                out_fps = 24 if self.kind == "ltx_i2v_2b" else int(self.job.get("fps", 16))
                export_to_video(frames, str(raw_tmp), fps=out_fps)

                # Encode clean H.264 yuv420p clip
                ffmpeg_bin = shutil.which("ffmpeg")
                if not ffmpeg_bin:
                    import imageio_ffmpeg

                    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

                subprocess.run(
                    [
                        ffmpeg_bin,
                        "-y",
                        "-v",
                        "error",
                        "-i",
                        str(raw_tmp),
                        "-c:v",
                        "libx264",
                        "-crf",
                        "17",
                        "-preset",
                        "fast",
                        "-pix_fmt",
                        "yuv420p",
                        str(out_mp4),
                    ],
                    check=True,
                )
                raw_tmp.unlink(missing_ok=True)
                elapsed = round(time.time() - t0, 1)
                log(f"Scene {scene['id']} COMPLETE ({self.kind}, {self.width}x{self.height}, {len(frames)}f) in {elapsed}s")
                return {
                    "id": scene["id"],
                    "backend": self.kind,
                    "width": self.width,
                    "height": self.height,
                    "frames": len(frames),
                    "seconds_elapsed": elapsed,
                    "bytes": out_mp4.stat().st_size,
                }
            except RuntimeError as exc:
                msg = str(exc)
                log(f"Attempt {attempt} RuntimeError on {scene['id']}: {msg[:240]}")
                self.pipe = None
                gc.collect()
                torch.cuda.empty_cache()
                if self.kind == "ltx_i2v_2b":
                    log("Switching fallback to Wan 2.2 TI2V-5B...")
                    self.width, self.height, self.frames, self.steps = 832, 480, 33, 12
                    self.load_wan(sequential=True)
                else:
                    self.load_ltx()
        raise RuntimeError(f"All attempts exhausted for scene {scene['id']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", default=str(ROOT / "gpu-engine/b2b_job.json"))
    ap.add_argument("--only", required=True, help="Comma-separated scene IDs e.g. s01,s02")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ensure_deps()
    job = json.loads(pathlib.Path(args.job).read_text())
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}
    scenes = [s for s in job["scenes"] if s["id"] in wanted]
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = MotionEngine(job)
    receipts = []
    for sc in scenes:
        out_mp4 = out_dir / f"{sc['id']}.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 25000:
            log(f"Skipping {sc['id']} (already exists)")
            continue
        kf_path = ROOT / sc["image"]
        rec = engine.generate_clip(sc, kf_path, out_mp4)
        receipts.append(rec)

    (out_dir / f"receipts_{'_'.join(sorted(wanted))}.json").write_text(json.dumps(receipts, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
