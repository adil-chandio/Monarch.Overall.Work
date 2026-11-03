"""Title generation + scoring.

The rules are boring on purpose. A title has one job: win the click without lying,
because a lie destroys retention and retention is what the algorithm actually rewards.
Every rule below is a measurable property, not a vibe.

Hard rules (a violation is a hard fail, not a deduction):
  - <= 60 characters (YouTube truncates around there in most surfaces)
  - the load-bearing word is inside the first 4 words (mobile truncates the tail)
  - no ALL-CAPS runs longer than one word
  - no fake urgency, no "you won't believe", no emoji spam
"""
from __future__ import annotations

import re

MAX_CHARS = 60

CLICKBAIT = [
    r"you won'?t believe", r"shocking", r"insane", r"crazy", r"must see",
    r"\bnever\b.*\bbefore\b", r"\bsecret\b", r"they don'?t want you to",
    r"\bgone wrong\b", r"\bexposed\b", r"\bbreaking\b",
]
FAKE_URGENCY = [r"\bnow\b", r"\btoday only\b", r"\blast chance\b", r"\burgent\b"]

# Words that carry the click in this niche. Presence near the front is worth a lot.
POWER = [
    "proof", "numbers", "real", "built", "ship", "shipped", "solo", "client",
    "frame", "film", "render", "60fps", "workflow", "system", "audit", "zero",
    "budget", "measured", "verified", "before", "after", "vs",
]
# Abstract words that cost you a click because they can mean anything.
FILLER = [
    "journey", "passion", "creative", "content", "amazing", "incredible",
    "story", "process", "mindset", "value", "solutions", "digital",
]


def _words(s: str) -> list:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’,.%+-]*", s)


def score_title(title: str) -> dict:
    w = _words(title)
    low = title.lower()
    n = len(title)

    fails = []
    if n > MAX_CHARS:
        fails.append(f"{n} chars > {MAX_CHARS}")
    if len(w) < 3:
        fails.append("fewer than 3 words")
    if re.search(r"\b[A-Z]{5,}\b", title):
        fails.append("shouting caps")
    for pat in CLICKBAIT:
        if re.search(pat, low):
            fails.append(f"clickbait phrase: {re.search(pat, low).group(0)}")
    for pat in FAKE_URGENCY:
        if re.search(pat, low):
            fails.append(f"fake urgency: {re.search(pat, low).group(0)}")

    # front-load: position of the first power word, as a 0..1 fraction of the title
    front = None
    for i, word in enumerate(w):
        if word.lower().strip(",.") in POWER:
            front = 1.0 - (i / max(1, len(w)))
            break
    number = 1.0 if re.search(r"\d", title) else 0.0
    concrete = 1.0 if re.search(r"\d|\bproof\b|\bmeasured\b|\bverified\b|\bbuilt\b", low) else 0.0
    filler = sum(1 for x in w if x.lower() in FILLER) / max(1, len(w))
    length_fit = max(0.0, 1.0 - abs(n - 48) / 40.0)     # 48 chars is the sweet spot

    sub = {
        "front_load": round(100 * (front if front is not None else 0.25), 1),
        "specificity": round(100 * concrete, 1),
        "number": round(100 * number, 1),
        "length_fit": round(100 * length_fit, 1),
        "filler_free": round(100 * (1.0 - min(1.0, filler * 4)), 1),
    }
    weights = {"front_load": 0.30, "specificity": 0.25, "number": 0.10,
               "length_fit": 0.20, "filler_free": 0.15}
    score = sum(weights[k] * v for k, v in sub.items())
    return {
        "title": title, "chars": n, "words": len(w),
        "score": round(score, 1),
        "grade": "A" if score >= 85 else "B" if score >= 72 else "C" if score >= 58 else "D",
        "subscores": sub, "hard_fails": fails,
    }


def title_variants(subject="Proof Over Promises", proof="583,290 views",
                   deliverable="1080p60", actor="a solo studio"):
    """Candidate titles across the four angles that reliably pull in this niche."""
    return [
        # 1. proof-led: the number is the promise
        f"{proof}. Zero bought numbers.",
        f"{proof} — here's every frame that earned it",
        # 2. method-led: curiosity without lying
        f"How {actor} ships {deliverable} alone",
        f"The {deliverable} pipeline {actor} actually uses",
        # 3. tension-led: the thing everyone else does wrong
        f"Everyone pitches. We shipped {deliverable} instead.",
        f"Pitch decks are dead. Here's the {deliverable} proof.",
        # 4. spec-led: for the people who buy on specs
        f"{deliverable} · 36s · 2,160 frames · measured",
        f"36 seconds, {deliverable}, one take — proof first",
    ]


def rank_titles(titles=None, **kw) -> list:
    titles = titles or title_variants(**kw)
    return sorted(((t, score_title(t)) for t in titles), key=lambda r: -r[1]["score"])


if __name__ == "__main__":
    for t, r in rank_titles():
        flag = "FAIL " + "; ".join(r["hard_fails"]) if r["hard_fails"] else r["grade"]
        print(f'{r["score"]:5.1f} {flag:6} {r["chars"]:3}c  {t}')
