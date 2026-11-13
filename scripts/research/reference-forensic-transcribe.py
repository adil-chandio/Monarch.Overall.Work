#!/usr/bin/env python3
"""Forensic transcription of a reference video, run where the network works.

Why this is a workflow and not a sandbox script: every speech-to-text model host is
unreachable from the development sandbox (huggingface.co 000, cdn-lfs 000, the ggml
files 404 at their old GitHub paths). GitHub Actions runners have the network. The
repo already does exactly this in .github/workflows/zack-audio-model-analysis.yml.

What it produces, and why each part exists:

  transcript.json   word-level timings. Not sentences — words, each with a start and
                    an end, so a claim about pacing can be checked rather than felt.
  transcript.srt    the same thing as subtitles, for a human to read in a player.
  speech-stats.json the derived numbers: words per minute per minute, silence
                    between words, the longest unbroken pause, the first word time.
                    This is the file the analysis actually cites.

The video never enters the model's context. This script only reads audio and writes
text; nothing about the picture is inferred here.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

VIDEO = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("reference-forensics")
MODEL = sys.argv[3] if len(sys.argv) > 3 else "base.en"

OUT.mkdir(parents=True, exist_ok=True)
WAV = OUT / "audio-16k-mono.wav"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> int:
    if not VIDEO.exists():
        print(f"error: {VIDEO} does not exist", file=sys.stderr)
        return 2

    # 16 kHz mono is what Whisper was trained on; resampling here rather than inside
    # the model keeps the audio artefact in the output folder so a later check can
    # re-run without touching the source video.
    run(["ffmpeg", "-y", "-i", str(VIDEO), "-vn", "-ac", "1", "-ar", "16000", str(WAV)])

    from faster_whisper import WhisperModel

    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(WAV),
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
        beam_size=5,
    )

    words: list[dict] = []
    cues: list[dict] = []
    for seg in segments:
        cues.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
        for w in seg.words or []:
            words.append({"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip()})
        print(f"[{seg.start:7.2f}] {seg.text.strip()}", flush=True)

    if not words:
        print("error: no words came back — the audio is music-only or silent", file=sys.stderr)
        return 3

    duration = max(w["end"] for w in words)

    # Silence is measured between consecutive words, not between segments: a segment
    # boundary is an artefact of the model's chunking, a word gap is real speech.
    gaps = []
    for a, b in zip(words, words[1:]):
        g = b["start"] - a["end"]
        if g > 0:
            gaps.append({"at": round(a["end"], 2), "seconds": round(g, 2)})
    gaps.sort(key=lambda x: -x["seconds"])

    # Words per minute in one-minute buckets, so a slow middle third is visible
    # instead of being averaged away.
    per_minute = []
    for m in range(int(duration // 60) + 1):
        lo, hi = m * 60, (m + 1) * 60
        n = sum(1 for w in words if lo <= w["start"] < hi)
        if n:
            per_minute.append({"minute": m + 1, "words": n});

    text = " ".join(w["word"] for w in words)
    low = re.findall(r"[a-z']+", text.lower())
    stop = set(
        "the a an and or but if of to in on at for with from by as is are was were be been "
        "it its this that these those he she they we you i not no do does did so then than "
        "there their them his her our your my me us him what which who whom how why when where "
        "can could will would may might must shall should about into over under more most some "
        "such only own same very just also have has had up out off down all any both each few".split()
    )
    content = [w for w in low if w not in stop and len(w) > 2]

    stats = {
        "source": VIDEO.name,
        "model": MODEL,
        "language": info.language,
        "language_probability": round(info.language_probability, 4),
        "duration_s": round(duration, 2),
        "word_count": len(words),
        "words_per_minute": round(len(words) / (duration / 60), 1) if duration else None,
        "first_word_at_s": words[0]["start"],
        "last_word_ends_at_s": round(words[-1]["end"], 2),
        "gaps_over_0_5s": sum(1 for g in gaps if g["seconds"] >= 0.5),
        "gaps_over_1s": sum(1 for g in gaps if g["seconds"] >= 1.0),
        "longest_gaps": gaps[:15],
        "words_per_minute_by_minute": per_minute,
        "top_content_words": Counter(content).most_common(40),
        "segment_count": len(cues),
        "mean_segment_s": round(sum(c["end"] - c["start"] for c in cues) / len(cues), 2),
    }

    (OUT / "transcript.json").write_text(
        json.dumps({"words": words, "segments": cues}, indent=1, ensure_ascii=False) + "\n"
    )
    (OUT / "speech-stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n")

    def stamp(t: float) -> str:
        h, r = divmod(t, 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"

    (OUT / "transcript.srt").write_text(
        "\n".join(
            f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n"
            for i, c in enumerate(cues, 1)
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "transcript.txt").write_text(text + "\n", encoding="utf-8")

    print(json.dumps({k: v for k, v in stats.items() if k != "top_content_words"}, indent=2))
    WAV.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
