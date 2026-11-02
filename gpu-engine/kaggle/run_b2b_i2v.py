#!/usr/bin/env python3
"""
MONARCH® Zero-OOM GPU I2V Worker (Runs on each 16GB Tesla T4 in Kaggle Dual-T4)
Loads ONLY the 4.8GB LTX-Video Transformer + VAE directly onto GPU (text_encoder=None),
consuming pre-encoded T5-XXL embeddings (<2.5GB CPU RAM per worker -> zero OOM!).
"""
from __future__ import annotations

import argparse
import gc
import json
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


class MotionEngine:
    def __init__(self, job: dict, embeds_dir: pathlib.Path | None = None):
        import torch

        self.torch = torch
        self.job = job
        self.embeds_dir = embeds_dir
        self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        self.pipe = None
        self.width = 768
        self.height = 448
        self.frames = 49
        self.steps = 28
        log(f"CUDA device: {torch.cuda.get_device_name(0)} | dtype={self.dtype}")

    def ensure_loaded(self, has_preencoded: bool) -> None:
        if self.pipe is not None:
            return
        from diffusers import LTXImageToVideoPipeline

        if has_preencoded:
            log("Loading lightweight LTX-Video (text_encoder=None -> 4.8GB directly on CUDA!)...")
            pipe = LTXImageToVideoPipeline.from_pretrained(
                "Lightricks/LTX-Video",
                text_encoder=None,
                tokenizer=None,
                torch_dtype=self.dtype,
            )
            pipe.to("cuda")
        else:
            log("Loading full LTX-Video with model CPU offload...")
            pipe = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=self.dtype)
            pipe.enable_model_cpu_offload()
        try:
            pipe.vae.enable_tiling()
        except Exception:
            pass
        pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe

    def generate_clip(self, scene: dict, img_path: pathlib.Path, out_mp4: pathlib.Path) -> dict:
        from diffusers.utils import export_to_video, load_image

        torch = self.torch
        emb_file = (self.embeds_dir / f"{scene['id']}.pt") if self.embeds_dir else None
        has_emb = bool(emb_file and emb_file.exists())
        self.ensure_loaded(has_emb)

        img = load_image(str(img_path)).resize((self.width, self.height))
        gen = torch.Generator("cpu").manual_seed(int(scene.get("seed", 42)))
        t0 = time.time()

        with torch.no_grad():
            if has_emb:
                pack = torch.load(str(emb_file), map_location="cuda", weights_only=True)
                frames = self.pipe(
                    image=img,
                    prompt=None,
                    negative_prompt=None,
                    prompt_embeds=pack["prompt_embeds"].to(device="cuda", dtype=self.dtype),
                    prompt_attention_mask=pack["prompt_attention_mask"].to(device="cuda"),
                    negative_prompt_embeds=pack["negative_prompt_embeds"].to(device="cuda", dtype=self.dtype),
                    negative_prompt_attention_mask=pack["negative_prompt_attention_mask"].to(device="cuda"),
                    height=self.height,
                    width=self.width,
                    num_frames=self.frames,
                    num_inference_steps=self.steps,
                    guidance_scale=3.2,
                    decode_timestep=0.03,
                    decode_noise_scale=0.025,
                    generator=gen,
                ).frames[0]
                del pack
            else:
                prompt = f"{scene['prompt']}, {self.job.get('style', '')}".strip(", ")
                neg = self.job.get("negative", "blurry, low quality, text, watermark")
                frames = self.pipe(
                    image=img,
                    prompt=prompt,
                    negative_prompt=neg,
                    height=self.height,
                    width=self.width,
                    num_frames=self.frames,
                    num_inference_steps=self.steps,
                    guidance_scale=3.2,
                    decode_timestep=0.03,
                    decode_noise_scale=0.025,
                    generator=gen,
                ).frames[0]

        f0 = np.asarray(frames[0], dtype=np.float32)
        f_last = np.asarray(frames[-1], dtype=np.float32)
        luma = float(np.mean(f0))
        motion_delta = float(np.mean(np.abs(f_last - f0)))
        log(f"QC {scene['id']}: luma={luma:.1f}, motion_delta={motion_delta:.2f}")
        if not np.isfinite(luma) or luma < 3.0:
            raise RuntimeError(f"Dark/NaN frame detected on {scene['id']} (luma={luma})")

        raw_tmp = out_mp4.with_suffix(".raw.mp4")
        export_to_video(frames, str(raw_tmp), fps=24)

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            import imageio_ffmpeg

            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

        subprocess.run(
            [
                ffmpeg_bin, "-y", "-v", "error", "-i", str(raw_tmp),
                "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
                str(out_mp4),
            ],
            check=True,
        )
        raw_tmp.unlink(missing_ok=True)
        torch.cuda.empty_cache()
        elapsed = round(time.time() - t0, 1)
        log(f"Scene {scene['id']} COMPLETE (ltx_i2v_2b_direct_cuda, {self.width}x{self.height}, {len(frames)}f) in {elapsed}s")
        return {
            "id": scene["id"],
            "backend": "ltx_i2v_2b_direct_cuda",
            "width": self.width,
            "height": self.height,
            "frames": len(frames),
            "luma": round(luma, 2),
            "motion_delta": round(motion_delta, 2),
            "seconds_elapsed": elapsed,
            "bytes": out_mp4.stat().st_size,
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", default=str(ROOT / "gpu-engine/b2b_job.json"))
    ap.add_argument("--embeds", default="")
    ap.add_argument("--only", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    job = json.loads(pathlib.Path(args.job).read_text())
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}
    scenes = [s for s in job["scenes"] if s["id"] in wanted]
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    emb_dir = pathlib.Path(args.embeds) if args.embeds else None

    engine = MotionEngine(job, embeds_dir=emb_dir)
    receipts = []
    for sc in scenes:
        out_mp4 = out_dir / f"{sc['id']}.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 25000:
            log(f"Skipping {sc['id']} (already exists)")
            continue
        kf_path = pathlib.Path(args.job).resolve().parents[1] / sc["image"]
        rec = engine.generate_clip(sc, kf_path, out_mp4)
        receipts.append(rec)

    (out_dir / f"receipts_{'_'.join(sorted(wanted))}.json").write_text(json.dumps(receipts, indent=2))
    gc.collect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
