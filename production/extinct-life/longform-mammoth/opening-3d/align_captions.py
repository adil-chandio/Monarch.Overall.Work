"""Align narration to caption cues using detected speech activity.

Method: decode the narration to mono PCM, detect voiced regions by short-term RMS,
then distribute the known sentence order across the detected voiced regions in
proportion to character length. This is a measured approximation of speech
activity, not a claim of word-level forced alignment.
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
import imageio_ffmpeg

B = Path(__file__).resolve().parent
SRC = B / 'source'
ff = imageio_ffmpeg.get_ffmpeg_exe()

SENTENCES = [
    "This mammoth may have had an extraordinary coat.",
    "Scientists found two mutations in a gene linked to hair development.",
    "They predicted a silky coat, but could not observe it directly.",
    "The animal lived on Wrangel Island, in the Arctic Ocean, a few thousand years ago.",
    "Now the strange part.",
    "A later study of ancient genomes found that the island population recovered after an extreme bottleneck.",
    "Yet the mammoths eventually disappeared.",
    "How can both things be true?",
    "Scientists have examined genetic damage, climate, and human arrival, but the final generations are missing from the genetic record.",
    "So which explanation holds up?",
    "We will take the evidence apart, and at the end, separate what is proven, what is plausible, and what is still missing from the file.",
]
CHUNKS = [
    ["This mammoth may have had", "an extraordinary coat."],
    ["Scientists found two mutations", "in a gene linked", "to hair development."],
    ["They predicted a silky coat,", "but could not observe it directly."],
    ["The animal lived on Wrangel Island,", "in the Arctic Ocean,", "a few thousand years ago."],
    ["Now the strange part."],
    ["A later study of ancient genomes", "found that the island population", "recovered after an extreme bottleneck."],
    ["Yet the mammoths eventually disappeared."],
    ["How can both things be true?"],
    ["Scientists have examined genetic damage,", "climate, and human arrival,", "but the final generations", "are missing from the genetic record."],
    ["So which explanation holds up?"],
    ["We will take the evidence apart,", "and at the end,", "separate what is proven,", "what is plausible,", "and what is still missing", "from the file."],
]


def decode(path: Path, out: Path) -> tuple[int, np.ndarray]:
    subprocess.run([ff, '-y', '-v', 'error', '-i', str(path), '-ar', '48000', '-ac', '1',
                    '-c:a', 'pcm_s16le', str(out)], check=True)
    with wave.open(str(out)) as w:
        n = w.getnframes()
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    return sr, data


def voiced_regions(x: np.ndarray, sr: int, min_gap: float = 0.16, min_len: float = 0.12):
    hop = int(0.01 * sr)
    win = int(0.03 * sr)
    frames = (len(x) - win) // hop
    rms = np.array([np.sqrt(np.mean(x[i * hop:i * hop + win] ** 2)) for i in range(frames)])
    peak = rms.max()
    thresh = max(0.012, peak * 0.14)
    active = rms > thresh
    regions = []
    i = 0
    while i < len(active):
        if active[i]:
            j = i
            while j < len(active) and active[j]:
                j += 1
            start = i * hop / sr
            end = j * hop / sr
            if end - start >= min_len:
                regions.append([start, end])
            i = j
        else:
            i += 1
    merged = []
    for r in regions:
        if merged and r[0] - merged[-1][1] < min_gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return merged


def distribute(chunks, start, end):
    weights = np.array([max(1, len(c.split())) for c in chunks], dtype=float)
    bounds = np.concatenate([[0.0], np.cumsum(weights) / weights.sum()])
    out = []
    for i, c in enumerate(chunks):
        s = start + (end - start) * bounds[i]
        e = start + (end - start) * bounds[i + 1]
        out.append({'start': round(float(s), 3), 'end': round(float(e), 3), 'text': c})
    return out


def main():
    wav = SRC / 'narration.wav'
    sr, x = decode(SRC / 'narration.mp3', wav)
    regions = voiced_regions(x, sr)
    lengths = [len(s) for s in SENTENCES]
    total_chars = sum(lengths)

    # Group the fine regions into sentence-like blocks using longer internal pauses.
    groups = []
    for r in regions:
        if groups and r[0] - groups[-1][1] < 0.34:
            groups[-1][1] = r[1]
        else:
            groups.append([r[0], r[1]])

    spoken_start = regions[0][0]
    spoken_end = regions[-1][1]

    if len(groups) == len(SENTENCES):
        chosen = groups
        method = 'one-region-per-sentence'
    else:
        # Sentences and pauses do not always agree. Split the spoken span into as many
        # blocks as sentences exist, weighted by sentence length, then map 1:1.
        weights = np.array(lengths, dtype=float)
        bounds = np.concatenate([[0.0], np.cumsum(weights) / weights.sum()])
        span = spoken_end - spoken_start
        chosen = [[spoken_start + span * bounds[i], spoken_start + span * bounds[i + 1]]
                  for i in range(len(SENTENCES))]
        method = f'length-weighted split ({len(groups)} detected blocks, {len(SENTENCES)} sentences)'

    cues = []
    for chunks, (s, e) in zip(CHUNKS, chosen):
        cues.extend(distribute(chunks, s, e))

    cues = [c for c in cues if c['end'] > c['start']]
    # Merge very short cues into their neighbour so captions read cleanly.
    merged_cues = []
    for c in cues:
        if merged_cues and (c['end'] - c['start']) < 0.42:
            merged_cues[-1]['end'] = c['end']
            merged_cues[-1]['text'] += ' ' + c['text']
        else:
            merged_cues.append(c)

    meta = {
        'source': 'narration.mp3 (platform synthesised voice-04, unsped)',
        'audio_seconds': round(len(x) / sr, 3),
        'sample_rate': sr,
        'voiced_regions': [[round(a, 3), round(b, 3)] for a, b in regions],
        'alignment_method': method,
        'alignment_caveat': 'Sentence-level speech-activity alignment, not word-level forced alignment.',
        'cue_count': len(merged_cues),
    }
    (B / 'caption-alignment.json').write_text(json.dumps({**meta, 'cues': merged_cues}, indent=2) + '\n')
    print(json.dumps({k: v for k, v in meta.items() if k != 'voiced_regions'}, indent=2))
    for c in merged_cues:
        print(f"{c['start']:6.2f} - {c['end']:6.2f}  {c['text']}")


if __name__ == '__main__':
    main()
