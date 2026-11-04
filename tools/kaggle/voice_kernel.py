# MONARCH v3 — GPU word-level alignment (Whisper large-v3) on Kaggle T4 x2
#
# This file is the kernel body. It is NOT imported by the repo; the packager
# (tools/kaggle/make_voice_kernel.py) replaces __PAYLOAD__ / __TIMING__ and
# ships the result as a Kaggle notebook. Keeping it as ordinary Python — instead
# of a f-string with doubled braces — means it can be compiled and linted here
# before it ever costs a GPU run.
import base64
import json
import os
import pathlib
import subprocess
import sys
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"

OUT = pathlib.Path("/kaggle/working/monarch_out")
OUT.mkdir(parents=True, exist_ok=True)
VO = pathlib.Path("/kaggle/working/vo")
VO.mkdir(parents=True, exist_ok=True)

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
               ensure("av", "av>=14.0.0")]
print(install_log, flush=True)

receipt = {"stage": "gpu", "python": sys.version.split()[0], "install": install_log}
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
                         download_root="/kaggle/working/models")
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


def to_wav(src):
    """Decode with ffmpeg to exactly what Whisper wants.

    faster-whisper reads through PyAV, and the image's PyAV may be older than the
    argument faster-whisper passes (`metadata_errors`). Decoding here removes that
    dependency entirely: whoever wins the backend race, we hand it a clean
    16 kHz mono WAV.
    """
    wav = src.with_suffix(".wav")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1",
                        "-ar", "16000", "-c:a", "pcm_s16le", str(wav)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not wav.exists():
        raise RuntimeError("ffmpeg decode failed for " + src.name + ": "
                           + (r.stderr or "")[:300])
    return wav


WAVS = {}
for name in sorted(PAYLOAD):
    try:
        WAVS[name] = to_wav(VO / name)
    except Exception as exc:
        print("decode failed:", exc, flush=True)
print("decoded:", sorted((k, v.stat().st_size) for k, v in WAVS.items()), flush=True)

beats = []
audio_total = 0.0
for name in sorted(PAYLOAD):
    if name not in WAVS:
        continue
    start = TIMING["starts"][len(beats)]
    t0 = time.time()
    words, text_parts, seg_rows = [], [], []
    if backend.startswith("faster-whisper"):
        segments, info = model.transcribe(
            str(WAVS[name]), language="hi", task="transcribe", word_timestamps=True,
            vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for seg in segments:
            seg_rows.append({"start": round(seg.start, 3), "end": round(seg.end, 3),
                             "text": seg.text.strip()})
            text_parts.append(seg.text.strip())
            for w in (seg.words or []):
                words.append({"w": w.word.strip(), "s": round(w.start, 3),
                              "e": round(w.end, 3), "p": round(float(w.probability), 3)})
        dur = float(info.duration)
        lang, lang_prob = info.language, float(info.language_probability)
    else:
        res = model.transcribe(str(WAVS[name]), language="hi", word_timestamps=True,
                               verbose=False)
        dur = float(res.get("duration") or 0.0)
        lang, lang_prob = "hi", 1.0
        for seg in res.get("segments", []):
            seg_rows.append({"start": round(seg["start"], 3), "end": round(seg["end"], 3),
                             "text": str(seg.get("text", "")).strip()})
            text_parts.append(str(seg.get("text", "")).strip())
            for w in (seg.get("words") or []):
                words.append({"w": str(w.get("word", "")).strip(),
                              "s": round(float(w.get("start", 0)), 3),
                              "e": round(float(w.get("end", 0)), 3),
                              "p": round(float(w.get("probability", 0)), 3)})
        if not dur:
            dur = max([r["end"] for r in seg_rows], default=0.0)
    audio_total += dur
    rtf = round((time.time() - t0) / max(dur, 0.01), 4)
    beats.append({"file": name, "offset": round(float(start), 3),
                  "duration": round(dur, 3), "lang": lang,
                  "lang_prob": round(lang_prob, 3),
                  "text": " ".join(text_parts).strip(), "segments": seg_rows,
                  "words": words, "rtf": rtf})
    print("[" + str(len(beats)) + "/" + str(len(PAYLOAD)) + "] " + name
          + "  dur=" + str(round(dur, 2)) + "s  rtf=" + str(rtf)
          + "  words=" + str(len(words)), flush=True)

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
