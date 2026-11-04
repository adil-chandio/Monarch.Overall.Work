# v3 on the GPU — what the Kaggle T4 x2 run actually measured

This file is the receipt for the claim "the GPU was really used". Everything below
came back from Kaggle; the raw artifacts are in this folder and are committed.

## The job

`tools/kaggle/voice_kernel.py` (packaged by `tools/kaggle/make_voice_kernel.py`)
runs on Kaggle with `enable_gpu: true` and `machine_shape: "NvidiaTeslaT4"`, which
is what allocates **2 × Tesla T4** rather than the legacy single P100. The seven
voice-over mp3s are embedded in the notebook (base64) because a private repo
cannot be cloned from inside Kaggle, and `tools/kaggle/push_voice.sh` pushes,
polls to completion and pulls the results back.

Entry point: `.github/workflows/kaggle-v3-voice.yml` — credential resolution →
push → wait → commit the receipt even on failure (CI logs cannot be read from the
authoring sandbox, so the job commits its own transcript: `gpu-transcript.log`).

## The measurement (`receipts_gpu.json`)

| field | value |
|---|---|
| GPUs | **2 × Tesla T4**, 14.56 GB each, compute capability 7.5 |
| `nvidia-smi -L` | `GPU 0: Tesla T4 …` / `GPU 1: Tesla T4 …` |
| torch | 2.11.0+cu130, `cuda_available: true` |
| model | **faster-whisper large-v3, float16, CUDA** |
| model load | 24.37 s (weights pulled once, then cached) |
| audio | 7 files, 39.76 s of voice |
| transcribe wall time | **0.88 s** (≈45× realtime) |
| words aligned | **93**, mean word probability **0.964** |
| CPU fallbacks | **0** |

## What it bought the film

`public/demo/gpu/words.json` carries per-word start/end for all seven beats, in
Hindi, all seven detected as `hi` with probability 1.0. That turns "does the
voice fit the edit?" from an opinion into a check:

`tools/verify_sync.mjs` (wired into the render workflow) asserts that the last
spoken word of every beat lands **before that beat's seam**:

| beat | beat ends | last word | slack | words |
|---|---|---|---|---|
| 01-hook | 4.89 | 4.25 | 0.64 s | 13 |
| 02-rest | 11.25 | 10.59 | 0.66 s | 15 |
| 03-gap | 18.49 | 17.87 | 0.62 s | 13 |
| 04-lie | 25.09 | 24.37 | 0.72 s | 18 |
| 05-shift | 31.73 | 30.97 | 0.76 s | 13 |
| 06-audience | 37.29 | 36.69 | **0.60 s (min)** | 14 |
| 07-end | 42.24 | 41.17 | 1.07 s | 7 |

Voice ends at 41.17 s inside a 42.24 s film. Gate result: **PASS**.

## What it cost to get here (so nobody repeats it)

Eight pushes, each one a real defect found by the committed transcript rather
than guessed:

1. `COMPALI` looked like a bad token — actually the probe was missing `six`, and
   the earlier probe judged auth by scraping `kernels list` output (an account
   with no kernels looks like a failure). It is a valid `KGAT_` access token for
   the handle **`compali`**, auth method `ACCESS_TOKEN`.
2. The notebook baked the *packager's* `sys.executable` → `FileNotFoundError`
   inside Kaggle.
3. `pip install` was run with `-q`, hiding its own failure; now pip is verbose on
   failure and the kernel falls back to the image's openai-whisper.
4. `sys` used without being imported (my regression).
5. `json.loads()` on a value the packager had already substituted as a dict.
6. faster-whisper decodes through PyAV even for WAV, and the image's `av` predates
   `metadata_errors` → decode with ffmpeg to float32 PCM in memory instead.
7. `libcublas.so.12 is not found` — the pip CUDA wheels' `lib` dirs were not on the
   loader path; preload them `RTLD_GLOBAL` before building the model.
8. The kernel said COMPLETE but delivered nothing: a 3 GB model cache sat inside
   `/kaggle/working`, and the output archive skipped the deliverables. Weights and
   decoded audio now live in `/kaggle/temp`.

The last failure was the nastiest because it was a *false negative*: the results
were on Kaggle, and the copy step only looked at the output root.

## Honest limits

- The GPU is used for **measurement** (word alignment), not for rasterising the
  film. The picture is still HyperFrames + Chromium on a GitHub runner, because
  that is what renders this composition faithfully; a GPU would not change a
  single pixel of it. Saying otherwise would be the jugaad this project is
  avoiding.
- 0.88 s for 39.76 s of audio is faster than expected for large-v3 float16; it is
  what the kernel reported, and the receipt keeps the kernel's own log next to it.
- Background music and SFX are still synthesised on the CPU (`showreel/v2/audio.py`)
  from the same seams file, with no samples and no budget.
