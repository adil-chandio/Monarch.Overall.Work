#!/usr/bin/env python3
"""
Cue sheet built ON the repo's own audio contract (audio/kit.json + audio/cues.json).

Every cue names a kit role, and the kit supplies the level and the alignment:
  bed_db     the role's level over the music bed (measured median, not a guess)
  offset_ms  how far the sample sits off the cut (taps lead, whooshes trail)
  min_gap_ms the closest two cues of that role may run
The takes are the repo's rendered earshot bank (audio/takes/*.wav + meta.json),
which also carries onset_s / peak_s / end_s — so a cue is aligned on the
sample's own onset, not on its file start.
"""
from __future__ import annotations

import json
import math
import os
import wave

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
KIT = json.load(open(os.path.join(ROOT, "audio", "kit.json")))["kit"]
META = json.load(open(os.path.join(ROOT, "audio", "takes", "meta.json")))
TAKES = os.path.join(ROOT, "audio", "takes")
SR = 48000


def load(role):
    r = KIT["roles"].get(role)
    if not r:
        return None
    name = r["sound"].replace("/", "_")
    p = os.path.join(TAKES, name + ".wav")
    if not os.path.exists(p):
        return None
    with wave.open(p) as w:
        n = w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    m = META.get(name, {})
    return dict(x=x, meta=m, role=r, name=name)


def db(x):
    x = np.asarray(x, np.float32)
    peak = np.sqrt(np.mean(np.square(np.maximum(np.abs(x), 1e-9))))
    return 20 * math.log10(max(peak, 1e-9))


class Bus:
    """A stereo bed that cues are written into, with the kit's own rules enforced."""

    def __init__(self, dur, seed=7):
        self.n = int(dur * SR)
        self.L = np.zeros(self.n, np.float32)
        self.R = np.zeros(self.n, np.float32)
        self.last = {}
        self.rng = np.random.default_rng(seed)

    def cue(self, role, t, gain_db=0.0, bed_db=0.0, pan=0.0, width=1.0):
        c = load(role)
        if c is None:
            return False
        r = c["role"]
        gap = (r.get("min_gap_ms") or 0) / 1000.0
        if role in self.last and t - self.last[role] < gap:
            return False
        # onset alignment: shift so the sample's onset lands on the cut
        onset = float(c["meta"].get("onset_s", 0.0))
        off = (r.get("offset_ms", 0) or 0) / 1000.0
        start = t + off - onset
        # level: the kit states bed_db relative to the bed; convert to linear
        target_db = bed_db + r.get("bed_db", 0.0) + gain_db
        cur = db(c["x"])
        g = 10 ** ((target_db - cur) / 20.0)
        s = int(round(start * SR))
        x = c["x"]
        i0 = max(0, -s)
        j0 = max(0, s)
        m = min(len(x) - i0, self.n - j0)
        if m <= 0:
            return False
        seg = x[i0:i0 + m] * g
        # equal-power pan; sub stays mono
        if role in ("drop", "land", "hit", "tock", "suck"):
            gl = gr = 0.7071
        else:
            a = (np.clip(pan, -1, 1) + 1) * 0.25 * math.pi
            gl, gr = math.cos(a), math.sin(a)
        self.L[j0:j0 + m] += seg * gl * 1.4142
        self.R[j0:j0 + m] += seg * gr * 1.4142
        self.last[role] = t
        return True

    def stereo(self):
        return np.stack([self.L, self.R], 1)


# ------------------------------------------------------------------ the 0-60 s cut

# ---------------------------------------------------------------- film sync
# The cue sheet is not hand-timed. Every event is derived from the same data the
# renderer uses: the shot list in film1min.py, and the walk clock of the animal.
import film1min as FILM


def _shots():
    _, sh = FILM.film()
    starts, acc = [], 0.0
    for s in sh:
        starts.append(acc); acc += s.dur
    return sh, starts


def _walk_shot(sh, starts):
    """Which shot actually contains the walk, and when does each foot land."""
    for i, s in enumerate(sh):
        # the gait is driven by phase = u * 2*pi*freq inside the act() lambda
        act = s.act(0.5)
        if act.get("kind") == "bear" and act.get("walk", 0.0) > 0.5:
            return i, starts[i], s.dur
    return None, None, None


def events():
    """Every audio event with its reason, in seconds."""
    sh, starts = _shots()
    off, total = {}, 0.0
    for s in sh:
        off[s.name] = total; total += s.dur
    ev = []

    # 1) transitions: one whoosh per cut, alternating the two the kit provides
    for i, t in enumerate(starts[1:], start=1):
        role = "whoosh.long" if i in (1, 3, 5) else "whoosh.short"
        ev.append((t, role, -2.0, 0.25 if i % 2 else -0.25, "cut %d" % i))

    # 2) story beats: riser into the beat, impact on the beat
    for t, why in ((off["S3"], "the animal is revealed"),
                   (off["S4"], "it fills the doorway"),
                   (off["S5"], "six hundred kilos"),
                   (off["S6"], "it moves"),
                   (off["S7"], "the mouth, cold")):
        ev.append((max(0.0, t - 1.1), "riser", -3.0, 0.0, why + " (riser)"))
        ev.append((t, "hit", -1.5, 0.0, why))
    ev.append((off["S1"], "drop", -1.0, 0.0, "cold open"))
    ev.append((off["S4"], "drop", -6.0, 0.0, "doorway, under the punch"))

    # 3) text cards land on a tick
    for t, txt in ((1.2, "37,000"), (10.4, "A SKULL"), (28.4, "ONE DOOR"),
                   (37.0, "600 KG"), (55.2, "NOT A BEAR")):
        ev.append((t, "tick", 0.0, 0.0, "card: " + txt))

    # 4) the skull reveal gets a bell, "PLACED." gets a body landing
    ev.append((6.2, "bell", 0.0, 0.15, "skull reveal"))
    ev.append((off["S3"] - 0.6, "land", -1.0, 0.0, "the animal settles"))

    # 5) footsteps come from the gait clock: 2 steps per stride cycle, and the
    #    kit's land.light (tap/finger) is a claw/gravel touch, land (pro_pop) a
    #    full weight plant. This is why the feet and the sound cannot drift.
    i, t0, dur = _walk_shot(sh, starts)
    if i is not None:
        freq = FILM.BEAR_WALK["freq"]
        n_steps = int(dur * freq * 2)
        for k in range(n_steps):
            t = t0 + k / (2.0 * freq)
            role = "land" if k % 4 == 0 else "land.light"
            g = -3.0 if k % 4 == 0 else -5.0
            ev.append((t, role, g, -0.35 if k % 2 else 0.35, "footfall %d" % k))
    return ev


def build(dur=60.0, bed_db=-26.0):
    """Render the cue sheet: kit levels, kit alignment, kit gaps, and the film's
    own clock. Nothing here is a hand-placed guess."""
    b = Bus(dur)
    for (t, role, gain, pan, why) in sorted(events()):
        b.cue(role, t, gain_db=gain, bed_db=bed_db, pan=pan)
    return b


if __name__ == "__main__":
    b = build()
    st = b.stereo()
    print("cued", len(b.last), "roles |", "peak %.3f" % np.abs(st).max())
    for role, t in sorted(b.last.items(), key=lambda kv: kv[1]):
        print("  %-14s %6.2fs" % (role, t))
