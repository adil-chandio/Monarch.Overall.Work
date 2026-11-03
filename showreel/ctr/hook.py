"""First-3-seconds hook scoring.

Retention is decided before the viewer has consciously decided anything. What decides it
is not "quality" — it is whether four specific things happen in the first 120 frames:

  1. MOTION at frame 0. A static open reads as a banner ad and gets swiped.
  2. A CLAIM in words within ~1.5 s. Silence is not intrigue, it is a reason to leave.
  3. SPECIFICITY in that claim (a number, a named thing, a verifiable fact).
  4. NO RAMP. The energy of second 1 must already be at the level of the body.
     This is the exact defect v3 had: hook -19.5 dBFS vs deck -14.7.

The audio half is measurable with showreel/audio_qc; this module scores the script and
the on-screen plan, and `hook_plan_score` folds in the measured audio numbers.
"""
from __future__ import annotations

import re

CLAIM_MARKERS = [
    r"\d", r"\bproof\b", r"\breal\b", r"\bbuilt\b", r"\bshipped\b", r"\bmeasured\b",
    r"\bverified\b", r"\bhere'?s\b", r"\bthis is\b", r"\bwatch\b",
]
VAGUE = [r"\bimagine\b", r"\blet me\b", r"\bwelcome\b", r"\bin today'?s video\b",
         r"\bbefore we (start|begin)\b", r"\bsmash that\b", r"\blike and subscribe\b"]
WPM = 165          # natural spoken pace for a 3-second cold open


def score_hook(script: str, on_screen: str = "", motion_at_frame0: bool = True,
               seconds: float = 3.0) -> dict:
    low = script.lower()
    words = len(re.findall(r"\b\w+\b", script))
    spoken_s = words / (WPM / 60.0)

    fails = []
    if words and spoken_s > seconds + 0.35:
        fails.append(f"script needs {spoken_s:.1f}s of speech but has {seconds:.1f}s")
    for pat in VAGUE:
        if re.search(pat, low):
            fails.append(f"vague opener: {re.search(pat, low).group(0)}")
    if not motion_at_frame0:
        fails.append("frame 0 is static")

    claim = 1.0 if any(re.search(p, low) for p in CLAIM_MARKERS) else 0.0
    # a hard declarative contrast ("X. Nobody Y.") is also a claim, just without a number
    if claim == 0.0 and re.search(r"\bnobody\b|\bnothing\b|\bnever\b|\bno one\b", low):
        claim = 0.75
    specific = 1.0 if re.search(r"\d", low) else 0.0
    # the on-screen text should not duplicate the narration; it should add the number
    onscreen_adds = 1.0 if on_screen and not set(on_screen.lower().split()) <= set(low.split()) else 0.55
    tight = max(0.0, 1.0 - max(0.0, spoken_s - seconds) / 1.5)

    sub = {
        "claim_in_1_5s": round(100 * claim, 1),
        "specificity": round(100 * specific, 1),
        "onscreen_adds_info": round(100 * onscreen_adds, 1),
        "spoken_fits_window": round(100 * tight, 1),
        "motion_at_frame0": 100.0 if motion_at_frame0 else 0.0,
    }
    w = {"claim_in_1_5s": 0.30, "specificity": 0.25, "onscreen_adds_info": 0.15,
         "spoken_fits_window": 0.15, "motion_at_frame0": 0.15}
    score = sum(w[k] * v for k, v in sub.items())
    return {"script": script, "on_screen": on_screen, "spoken_seconds": round(spoken_s, 2),
            "score": round(score, 1),
            "grade": "A" if score >= 85 else "B" if score >= 72 else "C" if score >= 58 else "D",
            "subscores": sub, "hard_fails": fails}


def hook_plan_score(hook_report: dict, measured_audio: dict) -> dict:
    """Fold the *measured* audio numbers into the hook verdict.

    measured_audio keys from showreel/audio_qc:
      hook_rms_dbfs, body_rms_dbfs, onsets_per_second, integrated_lufs
    """
    hook = measured_audio.get("hook_rms_dbfs")
    body = measured_audio.get("body_rms_dbfs")
    gap = None if hook is None or body is None else round(body - hook, 2)
    audio_ok = gap is not None and gap <= 2.0
    combined = hook_report["score"]
    if gap is not None:
        combined = combined * 0.75 + (100.0 if audio_ok else max(0.0, 100 - 18 * (gap - 2.0))) * 0.25
    return {
        "combined": round(combined, 1),
        "hook_vs_body_db": gap,
        "audio_ok": audio_ok,
        "note": "hook must be within 2 dB of the body, or the open reads as a fade-in",
        "script_report": hook_report,
    }


def hook_variants():
    """Four openers with genuinely different bets, all inside 3 seconds."""
    return [
        ("A · number slam",   "583,290 views. Zero bought numbers.", "583,290 / ZERO BOUGHT"),
        ("B · contradiction", "Everybody pitches. Nobody ships.",      "PITCH → SHIP"),
        ("C · spec flex",     "36 seconds. 2,160 frames. One take.",   "36.00s / 2,160F / 1 TAKE"),
        ("D · receipt",       "Here's the Studio screenshot. Unedited.", "UNEDITED CAPTURE"),
    ]


if __name__ == "__main__":
    for name, script, on in hook_variants():
        r = score_hook(script, on)
        flag = "FAIL " + "; ".join(r["hard_fails"]) if r["hard_fails"] else r["grade"]
        print(f'{r["score"]:5.1f} {flag:6} {r["spoken_seconds"]:4.1f}s  {name:18} {script}')
