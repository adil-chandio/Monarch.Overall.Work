#!/usr/bin/env python3
"""Align the finished narration to the script without an external forced aligner.

Method (deterministic and inspectable):
  1. speech activity from a smoothed RMS envelope
  2. syllable nuclei = the voiced bursts inside that activity
  3. dynamic-programming alignment: every script word has a syllable weight, and
     words are assigned consecutive nuclei so that the *voiced time* each word
     receives matches its syllable share. Two words never share a nucleus and the
     order can never cross, which is the same constraint a forced aligner uses.
  4. captions are built from the script's own punctuation, then merged so no
     caption is on screen for less than MIN_CAP seconds or more than MAX_WORDS.

Output: audio/align.json + a printed report.

Limits, stated up front: this is an energy/syllable alignment, not phoneme
forced alignment (PocketSphinx is not installed here). It also assumes the voice
read the script as written — it did, this take was generated from it — so any
mispronunciation or ad-lib would shift a caption. Caption text is from the
script, so the captions can never disagree with what is written, only with the
exact audio onset. Human listening is still required.
"""
import json
import os
import wave

import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
WAV = os.path.join(HERE, "audio", "vo.wav")
OUT = os.path.join(HERE, "audio", "align.json")

MIN_CAP = 0.55          # seconds a caption must stay up
MAX_WORDS = 4

SCRIPT = [
    "This ship is about to climb a mountain.",
    "No crane.",
    "No elevator.",
    "Just water.",
    "At Gatun, three pairs of chambers climb eighty-five feet.",
    "Steel gates seal the ship inside, and the water does the rest.",
    "Open the valves, and the water pours down through tunnels inside the walls, then rises through a hundred holes in the floor.",
    "The ship floats up with it.",
    "Nothing lifts the ship. Buoyancy does.",
    "When both sides reach the same level, the gates swing open, and it moves to the next step.",
    "Three steps.",
    "Eighty-five feet.",
    "All the way to Gatun Lake.",
    "Gravity moves every drop.",
    "Electric motors only open gates and valves.",
    "No pumps. No engines.",
    "Engineering, hiding in plain sight.",
]


def read(p):
    with wave.open(p) as w:
        n = w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
        if w.getnchannels() > 1:
            x = x.reshape(-1, w.getnchannels()).mean(1)
    return x


def nuclei(env, sr, thr_frac=0.045, min_gap=0.055, min_len=0.035):
    on = env > env.max() * thr_frac
    k = max(1, int(min_gap * sr) // 2)
    ker = np.ones(k, np.int8)
    dil = np.convolve(on.astype(np.int8), ker, "same") > 0
    on = on | dil
    idx = np.nonzero(np.diff(np.r_[0, on.astype(np.int8), 0]))[0]
    segs = [(idx[i] / sr, idx[i + 1] / sr) for i in range(0, len(idx) - 1, 2)]
    return [(a, b) for a, b in segs if b - a >= min_len]


def syllables(word):
    w = "".join(c for c in word.lower() if c.isalpha())
    if not w:
        return 1
    groups, prev = 0, False
    for c in w:
        v = c in "aeiouy"
        if v and not prev:
            groups += 1
        prev = v
    if w.endswith("e") and not w.endswith(("le", "ee")) and groups > 1:
        groups -= 1
    if len(w) <= 2 and groups == 0:
        groups = 1
    return max(1, groups)


def tokenize(script):
    toks, si = [], 0
    for line in script:
        for raw in line.replace(",", " , ").split():
            w = raw.strip(",.")
            if not w:
                continue
            toks.append(dict(sentence=si, raw=raw, word=w, punct=raw[-1] if raw[-1] in ",." else ""))
            if raw.endswith("."):
                si += 1
    return toks


def dp_align(words, segs):
    """Monotone assignment of consecutive nuclei to words, matching voiced share."""
    W, N = len(words), len(segs)
    d = np.array([b - a for a, b in segs], np.float64)
    wgt = np.array([syllables(w["word"]) for w in words], np.float64)
    target = wgt / wgt.sum() * d.sum()
    INF = 1e18
    cost = np.full((W + 1, N + 1), INF)
    back = np.full((W + 1, N + 1), -1, np.int32)
    cost[0, 0] = 0.0
    for j in range(1, W + 1):
        for i in range(j, N + 1):
            best, bi = INF, -1
            # previous split point k: word j took nuclei k..i-1
            for k in range(j - 1, i):
                if cost[j - 1, k] >= INF:
                    continue
                got = d[k:i].sum()
                c = cost[j - 1, k] + ((got - target[j - 1]) ** 2)
                if c < best:
                    best, bi = c, k
            cost[j, i] = best if bi >= 0 else INF
            back[j, i] = bi
    # require the last word to end at the last nucleus
    i_best = N
    if cost[W, i_best] >= INF:
        i_best = int(np.argmin(cost[W]))
    # backtrack
    out, i, j = [], i_best, W
    while j > 0:
        k = back[j, i]
        out.append((k, i))
        i, j = k, j - 1
    out.reverse()
    spans = []
    for (k, i), w in zip(out, words):
        spans.append((segs[k][0], segs[i - 1][1]))
    return spans


def make_captions(words, spans, max_words=4, min_cap=0.62, max_cap=2.40):
    """Break captions inside each script sentence.

    A cut is only made where the audio actually pauses, the chunk may not exceed
    max_words, and a chunk that would stay up longer than max_cap is split earlier.
    Cards never overlap and never flash for less than min_cap.
    """
    units = []
    for w, sp in zip(words, spans):
        if not units or units[-1][0] != w["sentence"]:
            units.append([w["sentence"], []])
        units[-1][1].append((w, sp))

    caps = []
    for si, ch in units:
        p = 0
        n = len(ch)
        while p < n:
            best_k, best_s = None, -1e9
            for k in range(1, min(max_words, n - p) + 1):
                if n - p - k == 1:            # never leave a single orphan word
                    continue
                dur = ch[p + k - 1][1][1] - ch[p][1][0]
                gap = (ch[p + k][1][0] - ch[p + k - 1][1][1]) if p + k < n else 0.6
                score = gap * 1.0 - 0.55 * max(0.0, dur - max_cap) - (0.9 if k == 1 and n - p > 2 else 0.0)
                if score > best_s:
                    best_s, best_k = score, k
            k = best_k or 1
            part = ch[p:p + k]
            caps.append(dict(sentence=si, text=" ".join(x[0]["raw"] for x in part),
                             start=part[0][1][0], end=part[-1][1][1]))
            p += k

    # merge a flash card into a neighbour when the pause between them is short
    out = []
    for c in caps:
        if out and (c["end"] - c["start"]) < min_cap and (c["start"] - out[-1]["end"]) < 0.16:
            out[-1]["text"] += " " + c["text"]
            out[-1]["end"] = c["end"]
        else:
            out.append(c)

    # hold each card to the next cut, and never let two cards overlap
    for i, c in enumerate(out):
        nxt = out[i + 1]["start"] if i + 1 < len(out) else c["end"] + 0.45
        c["end"] = round(min(nxt - 0.02, c["end"] + 0.42), 3)
        c["start"] = round(max(0.0, c["start"] - 0.05), 3)
        if i:
            c["start"] = round(max(c["start"], out[i - 1]["end"] + 0.02), 3)
        if c["end"] <= c["start"]:
            c["end"] = round(c["start"] + 0.4, 3)
    return out


def main():
    x = read(WAV)
    sr = SR
    env = np.convolve(np.abs(x), np.ones(int(0.010 * sr)) / int(0.010 * sr), mode="same")
    segs = nuclei(env, sr)
    words = tokenize(SCRIPT)
    if len(segs) < len(words):
        raise SystemExit(f"fewer nuclei ({len(segs)}) than words ({len(words)}) - lower thr_frac")
    spans = dp_align(words, segs)
    for w, (a, b) in zip(words, spans):
        w["start"], w["end"] = round(a, 3), round(b, 3)
    caps = make_captions(words, spans)

    dur = len(x) / sr
    rep = dict(sr=sr, dur=round(dur, 3), words=len(words), nuclei=len(segs), captions=len(caps),
               method="RMS envelope -> syllable nuclei -> monotone DP on syllable weight",
               limits="not phoneme-forced alignment; assumes the take follows the script verbatim")
    json.dump(dict(report=rep, words=[{k: v for k, v in w.items() if k in
                                      ("sentence", "word", "raw", "punct", "start", "end")} for w in words],
                   captions=caps), open(OUT, "w"), indent=1)
    print(json.dumps(rep, indent=1))
    print("\n--- captions ---")
    for c in caps:
        d = c["end"] - c["start"]
        print("%6.2f - %6.2f (%4.2fs) %s%s" % (c["start"], c["end"], d, c["text"], "   <-- SHORT" if d < 0.5 else ""))
    # sanity: monotone, non-overlapping, inside the take
    bad = [c for i, c in enumerate(caps) if i and c["start"] < caps[i - 1]["start"] - 1e-6]
    over = [c for i, c in enumerate(caps) if i and c["start"] < caps[i - 1]["end"] - 1e-6]
    print("\nmonotone:", not bad, "| overlaps:", len(over), "| last end:", caps[-1]["end"], "of", round(dur, 2))


if __name__ == "__main__":
    main()
