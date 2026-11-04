# MONARCH v3 — GPU word-level alignment (Whisper large-v3) on Kaggle T4 x2
#
# This file is the kernel body. It is NOT imported by the repo; the packager
# (tools/kaggle/make_voice_kernel.py) replaces __PAYLOAD__ / __TIMING__ and
# ships the result as a Kaggle notebook. Keeping it as ordinary Python — instead
# of a f-string with doubled braces — means it can be compiled and linted here
# before it ever costs a GPU run.
import base64
import ctypes
import glob
import json
import os
import site
import pathlib
import subprocess
import sys
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Only *results* may live under /kaggle/working: everything there is zipped into
# the kernel output, and a 3 GB model cache there made `kaggle kernels output`
# skip the deliverables entirely (a COMPLETE kernel with no words.json).
OUT = pathlib.Path("/kaggle/working/monarch_out")
OUT.mkdir(parents=True, exist_ok=True)
SCRATCH = pathlib.Path("/kaggle/temp")
SCRATCH.mkdir(parents=True, exist_ok=True)
VO = SCRATCH / "vo"
VO.mkdir(parents=True, exist_ok=True)
MODELS = SCRATCH / "models"

# substituted as Python/JSON literals by the packager — not re-parsed
PAYLOAD = __PAYLOAD__
TIMING = __TIMING__

for name, b64 in PAYLOAD.items():
    (VO / name).write_bytes(base64.b64decode(b64))
print("unpacked VO files:", sorted(p.name for p in VO.glob("*.mp3")), flush=True)


def ensure(module, spec):
    """Install only what the image is missing, and let pip talk when it fails."""
    try:
        __import__(module)
        return spec + ": present"
    except Exception:
        pass
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-input",
                        "--no-cache-dir", "--disable-pip-version-check",
                        "--break-system-packages", spec],
                       capture_output=True, text=True)
    print("pip", spec, "rc=", r.returncode, flush=True)
    if r.returncode != 0:
        print((r.stdout or "")[-1500:], flush=True)
        print((r.stderr or "")[-1500:], flush=True)
    return spec + ": rc=" + str(r.returncode)


install_log = [ensure("faster_whisper", "faster-whisper>=1.0.3"),
               ensure("ctranslate2", "ctranslate2>=4.4.0"),
               ensure("nvidia.cublas", "nvidia-cublas-cu12"),
               ensure("nvidia.cudnn", "nvidia-cudnn-cu12")]
print(install_log, flush=True)


def enable_nvidia_libs():
    """Put the CUDA 12 wheels' .so files on the loader path.

    ctranslate2 4.x is built against CUDA 12; the image ships its own runtime and
    does not put the pip wheels' lib directories on LD_LIBRARY_PATH, so encode()
    dies with 'Library libcublas.so.12 is not found'. Preload them RTLD_GLOBAL so
    dlopen finds them even after the loader has cached its search path.
    """
    roots = []
    for sp in list(site.getsitepackages()) + [site.getusersitepackages()]:
        roots += sorted(glob.glob(sp + "/nvidia/*/lib"))
    if not roots:
        return []
    os.environ["LD_LIBRARY_PATH"] = ":".join(
        roots + [os.environ.get("LD_LIBRARY_PATH", "")]).strip(":")
    for lib in ("libcublas.so.12", "libcublasLt.so.12", "libcudnn.so.9",
                "libcudnn_ops.so.9", "libcudnn_graph.so.9"):
        for r in roots:
            p = os.path.join(r, lib)
            if os.path.exists(p):
                try:
                    ctypes.CDLL(p, mode=ctypes.RTLD_GLOBAL)
                except Exception as exc:
                    print("preload failed:", lib, exc, flush=True)
                break
    return roots



receipt = {"stage": "gpu", "python": sys.version.split()[0], "install": install_log}
# before any model is built: ctranslate2 dlopens libcublas at load time
receipt["nvidia_lib_dirs"] = enable_nvidia_libs()
print("nvidia lib dirs:", receipt["nvidia_lib_dirs"], flush=True)
try:
    import torch
    receipt["torch"] = torch.__version__
    receipt["cuda_available"] = bool(torch.cuda.is_available())
    receipt["gpu_count"] = int(torch.cuda.device_count())
    receipt["devices"] = []
    for i in range(torch.cuda.device_count()):
        p = torch.cuda.get_device_properties(i)
        receipt["devices"].append({"index": i, "name": p.name,
                                   "vram_gb": round(p.total_memory / 1024 ** 3, 2),
                                   "cc": str(p.major) + "." + str(p.minor)})
except Exception as exc:
    receipt["torch_error"] = str(exc)
try:
    receipt["nvidia_smi"] = subprocess.run(["nvidia-smi", "-L"], capture_output=True,
                                           text=True, timeout=30).stdout.strip()
except Exception as exc:
    receipt["nvidia_smi"] = "unavailable: " + str(exc)
print(json.dumps(receipt, indent=1), flush=True)

backend = ""
model = None
t0 = time.time()
try:
    from faster_whisper import WhisperModel
    model = WhisperModel("large-v3", device="cuda", compute_type="float16",
                         download_root=str(MODELS))
    backend = "faster-whisper large-v3 float16 cuda"
except Exception as exc:
    receipt["faster_whisper_error"] = type(exc).__name__ + ": " + str(exc)[:400]
    print("faster-whisper unusable ->", receipt["faster_whisper_error"], flush=True)

if model is None:
    # second backend: whatever the image already ships
    import torch
    import whisper
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("large-v3", device=device)
    backend = "openai-whisper large-v3 " + device

receipt["model_load_s"] = round(time.time() - t0, 2)
receipt["model"] = backend
print("backend:", backend, flush=True)


def to_pcm(src):
    """Decode to 16 kHz mono float32 with ffmpeg, in memory.

    Both backends accept a numpy array, which means neither one touches PyAV:
    the image's PyAV is older than the argument faster-whisper passes
    (`metadata_errors`), and that TypeError has already cost three runs. ffmpeg
    is the decoder we control, so it is the only decoder we use.
    """
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar",
                        "16000", "-f", "f32le", "-acodec", "pcm_f32le", "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("ffmpeg decode failed for " + src.name + ": "
                           + (r.stderr or b"").decode("utf-8", "ignore")[:300])
    audio = np.frombuffer(r.stdout, dtype=np.float32).copy()
    return audio, round(len(audio) / 16000.0, 3)


PCM = {}
for name in sorted(PAYLOAD):
    try:
        PCM[name] = to_pcm(VO / name)
    except Exception as exc:
        print("decode failed:", exc, flush=True)
print("decoded:", sorted((k, len(v[0]), v[1]) for k, v in PCM.items()), flush=True)

def transcribe_beat(model, backend, name):
    """One beat -> the keepers. Raises if the backend cannot run it."""
    words, text_parts, seg_rows = [], [], []
    if backend.startswith("faster-whisper"):
        segments, info = model.transcribe(
            PCM[name][0], language="hi", task="transcribe", word_timestamps=True,
            vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for seg in segments:
            seg_rows.append({"start": round(seg.start, 3), "end": round(seg.end, 3),
                             "text": seg.text.strip()})
            text_parts.append(seg.text.strip())
            for w in (seg.words or []):
                words.append({"w": w.word.strip(), "s": round(w.start, 3),
                              "e": round(w.end, 3), "p": round(float(w.probability), 3)})
        return words, text_parts, seg_rows, info.language, float(info.language_probability)
    res = model.transcribe(PCM[name][0], language="hi", word_timestamps=True,
                           verbose=False)
    for seg in res.get("segments", []):
        seg_rows.append({"start": round(seg["start"], 3), "end": round(seg["end"], 3),
                         "text": str(seg.get("text", "")).strip()})
        text_parts.append(str(seg.get("text", "")).strip())
        for w in (seg.get("words") or []):
            words.append({"w": str(w.get("word", "")).strip(),
                          "s": round(float(w.get("start", 0)), 3),
                          "e": round(float(w.get("end", 0)), 3),
                          "p": round(float(w.get("probability", 0)), 3)})
    return words, text_parts, seg_rows, "hi", 1.0


beats = []
audio_total = 0.0
fallbacks = []
for name in sorted(PAYLOAD):
    if name not in PCM:
        continue
    start = TIMING["starts"][len(beats)]
    dur = PCM[name][1]
    t0 = time.time()
    try:
        words, text_parts, seg_rows, lang, lang_prob = transcribe_beat(model, backend, name)
    except Exception as exc:
        # A CUDA-level failure must not cost the whole run: fall back to CPU int8
        # (42 s of audio, so it is minutes, not hours) and record why.
        msg = type(exc).__name__ + ": " + str(exc)[:300]
        print("backend failed on", name, "->", msg, flush=True)
        fallbacks.append({"file": name, "error": msg, "from": backend})
        backend = "faster-whisper large-v3 int8 cpu"
        model = WhisperModel("large-v3", device="cpu", compute_type="int8",
                             download_root=str(MODELS))
        words, text_parts, seg_rows, lang, lang_prob = transcribe_beat(model, backend, name)

    audio_total += dur
    rtf = round((time.time() - t0) / max(dur, 0.01), 4)
    beats.append({"file": name, "offset": round(float(start), 3),
                  "duration": round(dur, 3), "lang": lang,
                  "lang_prob": round(lang_prob, 3),
                  "text": " ".join(text_parts).strip(), "segments": seg_rows,
                  "words": words, "rtf": rtf})
    print("[" + str(len(beats)) + "/" + str(len(PAYLOAD)) + "] " + name
          + "  dur=" + str(dur) + "s  rtf=" + str(rtf)
          + "  words=" + str(len(words)), flush=True)

receipt["backend_fallbacks"] = fallbacks
receipt["model_final"] = backend
receipt["audio_total_s"] = round(audio_total, 3)
receipt["wall_s"] = round(time.time() - t0, 2)
receipt["words"] = sum(len(b["words"]) for b in beats)
receipt["mean_word_prob"] = round(
    sum(w["p"] for b in beats for w in b["words"]) / max(receipt["words"], 1), 3)

(OUT / "words.json").write_text(
    json.dumps({"beats": beats, "total": TIMING["total"]}, indent=1))
(OUT / "receipts_gpu.json").write_text(json.dumps(receipt, indent=1))
print("WROTE", sorted(p.name for p in OUT.iterdir()), flush=True)
print(json.dumps({k: receipt.get(k) for k in
                  ("gpu_count", "devices", "model", "words", "mean_word_prob",
                   "wall_s", "audio_total_s")}, indent=1), flush=True)
