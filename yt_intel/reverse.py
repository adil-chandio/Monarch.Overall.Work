"""Reverse-engineering a video that already won.

Given a video id this produces a teardown with six sections, in the order a creator
actually needs them:

  1. RECEIPT      real numbers, views-per-hour (the only fair speed metric), age
  2. SCRIPT       transcript -> hook length, word rate, section map, CTA density, reading
                  grade. Measured on the transcript, not guessed from the title.
  3. HOOK         the first N words, the first 3 seconds of speech, the claim type
  4. STRUCTURE    chapter/timestamp map when the creator published one, else beat timing
  5. PSYCHOLOGY   which drives the title+opening exploit, mapped to named effects
  6. REPLICATION  the concrete build plan: what to keep, what to change, what to beat

Rule that matters more than any of it: **the teardown never claims the video "went viral
because of X"**. It reports co-occurrence and labels it as such.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

from . import client, forensic

FILLER = {"um", "uh", "like", "you know", "basically", "actually", "literally", "okay", "so yeah"}
CTA = re.compile(r"\b(subscribe|like this video|hit the bell|comment below|link in the description|"
                 r"join (?:my|the) (?:channel|community|discord)|patreon|follow me)\b", re.I)
NUMBER_WORD = re.compile(r"\b\d[\d,.]*\b|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|"
                         r"hundred|thousand|million|billion)\b", re.I)


def reading_grade(text: str) -> float:
    """Flesch-Kincaid grade level. Spoken scripts should land 5-8; above 10 loses people."""
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words = len(re.findall(r"\b\w+\b", text))
    syl = _syllables(text)
    if not words:
        return 0.0
    return round(0.39 * (words / sentences) + 11.8 * (syl / words) - 15.59, 1)


def _syllables(text: str) -> int:
    n = 0
    for w in re.findall(r"[a-zA-Z]+", text.lower()):
        groups = re.findall(r"[aeiouy]+", w)
        s = len(groups)
        if w.endswith("e") and s > 1:
            s -= 1
        n += max(1, s)
    return n


def hook_window(words: list[str], seconds: float = 3.0, wpm: float = 165.0) -> list[str]:
    budget = max(3, round(seconds * wpm / 60))
    return words[:budget]


def section_map(text: str, total_seconds: float | None, chapters: list | None = None) -> list[dict]:
    """Timeline. Uses published chapters when they exist, else proportional pacing."""
    if chapters:
        out = []
        for c in chapters:
            out.append({"at": _hms(c.get("start_time")), "title": c.get("title", "")})
        return out
    if not total_seconds:
        return []
    words = text.split()
    n = len(words)
    if not n:
        return []
    marks = [0.0, 0.08, 0.22, 0.45, 0.62, 0.80, 0.93, 1.0]
    labels = ["cold open", "hook restated", "setup / promise", "first proof", "escalation",
              "payoff", "outro / CTA"]
    return [{"at": _hms(total_seconds * m), "title": labels[i], "pct": round(m * 100)}
            for i, m in enumerate(marks[:-1])]


def _hms(sec: float | None) -> str:
    if not sec:
        return "0:00"
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


def teardown(video_id: str, fetch_transcript: bool = True) -> dict:
    meta = client.videos([video_id]).items
    row = meta[0] if meta else {"id": video_id}
    age = forensic.parse_age_days(row.get("published", ""))
    row["age_days"] = age
    row["vph"] = forensic.vph(row.get("views"), age)
    dur = forensic.parse_duration(row.get("duration", ""))

    out: dict = {"id": video_id, "receipt": row, "duration_seconds": dur}

    if not fetch_transcript:
        return out
    tr = client.transcript(video_id)
    out["transcript_status"] = {k: tr.get(k) for k in ("status", "lang", "kind", "words", "detail")}
    text = tr.get("text", "") or ""
    words = text.split()
    if text:
        dur = dur or tr.get("duration") or 0
        wpm = round(len(words) / (dur / 60), 1) if dur else None
        ctas = [m.group(0).lower() for m in CTA.finditer(text)]
        out["script"] = {
            "words": len(words), "wpm": wpm, "silence_ratio": None,
            "filler_rate": round(sum(1 for w in words if w.lower().strip(".,") in FILLER) / max(1, len(words)), 4),
            "cta_count": len(ctas), "cta_examples": ctas[:5],
            "numbers_per_100w": round(len(NUMBER_WORD.findall(text)) / max(1, len(words)) * 100, 2),
            "reading_grade": reading_grade(text),
            "first_30_words": " ".join(words[:30]),
            "reading": _script_reading(len(words), wpm, reading_grade(text)),
        }
        out["hook"] = {
            "first_3s_words": " ".join(hook_window(words)),
            "first_sentence": re.split(r"(?<=[.!?])\s", text.strip())[0][:240] if text.strip() else "",
            "opens_with_number": bool(NUMBER_WORD.search(" ".join(words[:12]))),
            "opens_with_question": "?" in " ".join(words[:14]),
            "opens_with_you": bool(re.search(r"\byou\b", " ".join(words[:12]), re.I)),
            "claim_type": _claim_type(" ".join(words[:40])),
        }
        out["structure"] = section_map(text, dur, tr.get("chapters"))
        out["psychology"] = _psych(out["hook"], row.get("title", ""))

    out["replication"] = _replication(out)
    return out


def _script_reading(words: int, wpm: float | None, grade: float) -> str:
    bits = []
    if words:
        bits.append(f"{words} words")
    if wpm:
        bits.append(f"{wpm} wpm ({'fast, shorts-native' if wpm > 175 else 'conversational' if wpm > 130 else 'slow, essayist'})")
    if grade:
        bits.append(f"reading grade {grade} ({'clear' if grade <= 8 else 'too dense for spoken word'})")
    return " · ".join(bits)


def _claim_type(opening: str) -> str:
    low = opening.lower()
    if re.search(r"\b(nobody|no one|everyone is wrong|stop)\b", low):
        return "contrarian correction"
    if re.search(r"\b(what if|imagine)\b", low):
        return "hypothetical"
    if NUMBER_WORD.search(opening):
        return "evidenced claim"
    if "?" in opening:
        return "open question"
    if re.search(r"\bi\b", low):
        return "first-person proof"
    return "generic statement"


def _psych(hook: dict, title: str) -> dict:
    drivers = []
    if hook.get("opens_with_number"):
        drivers.append({"driver": "specificity", "effect": "numbers read as evidence; vagueness reads as sales"})
    if hook.get("opens_with_question"):
        drivers.append({"driver": "open loop", "effect": "the brain completes questions involuntarily"})
    if hook.get("opens_with_you"):
        drivers.append({"driver": "self-reference", "effect": "the 'you' effect — self-relevant words get attention"})
    if hook.get("claim_type") == "contrarian correction":
        drivers.append({"driver": "belief threat", "effect": "correcting a held belief creates relief + gratitude"})
    if hook.get("claim_type") == "hypothetical":
        drivers.append({"driver": "simulation", "effect": "the brain runs the scene as if it were happening"})
    if re.search(r"\b(wtf|impossible|insane|nobody|never|secret|truth)\b", (title or "").lower()):
        drivers.append({"driver": "schema violation", "effect": "an impossible claim is flagged as an error to resolve"})
    return {"drivers": drivers, "note": "descriptive mapping of the opening, not a causal claim"}


def _replication(t: dict) -> dict:
    h = t.get("hook", {})
    s = t.get("script", {})
    keep, change, beat = [], [], []
    if h.get("opens_with_number"):
        keep.append("lead with a number in the first sentence")
    if h.get("opens_with_you"):
        keep.append("address the viewer directly in the first 12 words")
    if s.get("reading_grade", 0) > 9:
        change.append("simplify the script to grade <= 8 — this one is written, not spoken")
    if s.get("cta_count", 0) > 3:
        change.append("cut CTAs down to one, placed after the payoff")
    if s.get("wpm") and s["wpm"] < 120:
        beat.append("tighter edit: this delivery leaves dead air a 160 wpm cut can use")
    if not h.get("opens_with_number"):
        beat.append("add a concrete number inside the first 3 seconds")
    if (t.get("receipt", {}).get("age_days") or 0) > 365:
        beat.append("the visual grammar is a year old; rebuild the look, keep the structure")
    return {"keep": keep, "change": change, "beat": beat,
            "note": "keep the mechanism, change the surface — copying the surface is how clones die"}
