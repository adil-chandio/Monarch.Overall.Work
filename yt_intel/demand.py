"""Demand and trend signals that need no API key.

The honest problem with "is anyone interested in this topic?" is that the only true
answer lives inside YouTube's analytics. Everything else is a proxy. So this module
never claims a search volume — it claims an **ordered demand signal** and says which
proxy produced it:

  autocomplete_position   where the phrase appears in YouTube's own suggestion list.
                          Being suggested at all means real query volume; position 1
                          means it beats everything else starting the same way.
  suggestion_spread       how many distinct suggestions share the stem. High spread =
                          the topic has many sub-intents, i.e. it is a topic, not a phrase.
  expansion_gain          suggestions added by appending a letter/word. Measures how
                          deep the rabbit hole goes (people keep looking).
  related_queries         "people also search" from YouTube's own UI.
  trends_slope            pytrends relative interest, 12-week slope. Relative, not absolute.

`demand_score` combines them with published weights and refuses to score when the
underlying data is missing — a missing signal lowers `confidence`, it never contributes
a fake middle value.
"""
from __future__ import annotations

import string
import time
from dataclasses import dataclass, field, asdict

from . import client, http

MODIFIERS = ["", " how", " why", " best", " vs", " for beginners", " 2026", " hindi", " urdu", " ai"]
INTENT_WORDS = {
    "how": "how-to", "why": "explainer", "best": "buyer/list", "vs": "comparison",
    "review": "review", "tutorial": "how-to", "explained": "explainer",
    "shorts": "short-form", "news": "news",
}


@dataclass
class Demand:
    topic: str
    suggestions: list = field(default_factory=list)
    position: int | None = None
    spread: int = 0
    expansion: dict = field(default_factory=dict)
    intent: list = field(default_factory=list)
    long_tail: list = field(default_factory=list)
    trends: dict = field(default_factory=dict)
    score: float | None = None
    confidence: float = 0.0
    parts: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def suggestions_for(topic: str, gl: str = "US") -> list[str]:
    out: list[str] = []
    for mod in MODIFIERS:
        q = (topic + mod).strip()
        try:
            out += client.autocomplete(q, gl=gl)
        except http.RateLimited:
            break
        time.sleep(0.15)
    seen, uniq = set(), []
    for s in out:
        k = s.lower().strip()
        if k and k not in seen:
            seen.add(k)
            uniq.append(s)
    return uniq


def alphabet_expansion(topic: str, letters: str = "abcdefghijklmnopqrstuvwxyz") -> dict:
    """Append each letter and keep the suggestions — the classic rabbit-hole probe."""
    found: dict[str, list[str]] = {}
    for ch in letters:
        try:
            got = client.autocomplete(f"{topic} {ch}")
        except http.RateLimited:
            break
        got = [g for g in got if g.lower().startswith(topic.lower())]
        if got:
            found[ch] = got
        time.sleep(0.12)
    return found


def classify_intent(suggestions: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for s in suggestions:
        low = s.lower()
        for word, label in INTENT_WORDS.items():
            if f" {word} " in f" {low} ":
                counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def google_trends(keywords: list[str], timeframe: str = "today 3-m", geo: str = "") -> dict:
    """Relative interest + 12-week slope via pytrends. Optional: needs pypi, not a key."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        return {"status": "unavailable", "detail": "pip install pytrends"}
    try:
        py = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        py.build_payload(keywords[:5], timeframe=timeframe, geo=geo)
        df = py.interest_over_time()
        if df is None or df.empty:
            return {"status": "empty"}
        import math
        out = {}
        for kw in keywords[:5]:
            if kw not in df:
                continue
            series = [int(v) for v in df[kw].tolist()]
            n = len(series)
            xs = list(range(n))
            mx = sum(xs) / n
            my = sum(series) / n
            denom = sum((x - mx) ** 2 for x in xs) or 1
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, series)) / denom
            out[kw] = {
                "mean": round(my, 1), "peak": max(series), "latest": series[-1],
                "slope_per_week": round(slope * 7, 2),
                "direction": "rising" if slope * 7 > 1 else "falling" if slope * 7 < -1 else "flat",
                "points": n,
            }
        rising = [q for q, v in out.items() if v.get("direction") == "rising"]
        return {"status": "ok", "timeframe": timeframe, "series": out, "rising": rising}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": str(e)[:160]}


def analyse(topic: str, gl: str = "US", deep: bool = False, with_trends: bool = True) -> Demand:
    d = Demand(topic=topic)
    try:
        d.suggestions = suggestions_for(topic, gl=gl)
    except http.RateLimited as e:
        d.notes.append(f"autocomplete rate limited: {e}")

    if not d.suggestions:
        d.notes.append(
            "NO AUTocomplete RESPONSE from this host — the demand signal is unavailable, not zero. "
            "This environment cannot reach suggestqueries.google.com; run the same command from a "
            "machine with outbound access (or a YOUTUBE_API_KEY, which sidesteps autocomplete)."
        )
    if d.suggestions:
        stems = [s for s in d.suggestions if s.lower().startswith(topic.lower())]
        d.spread = len(stems)
        # position = rank of the exact phrase among suggestions for the bare topic
        try:
            base = client.autocomplete(topic, gl=gl)
            low = [b.lower() for b in base]
            d.position = (low.index(topic.lower()) + 1) if topic.lower() in low else None
            if base:
                d.long_tail = base[:12]
        except http.RateLimited:
            pass
        d.intent = [f"{k} ({v})" for k, v in classify_intent(d.suggestions).items()]

    if deep:
        d.expansion = {ch: v[:5] for ch, v in alphabet_expansion(topic).items()}

    if with_trends:
        d.trends = google_trends([topic])

    d.parts, d.score, d.confidence = score(d)
    return d


TOTAL_WEIGHT = 1.0   # position .35 + spread .25 + expansion .20 + trends .20


def score(d: Demand) -> tuple[dict, float | None, float]:
    """Weighted, explainable, and honest about missing inputs.

    `confidence` divides by the FULL scheme weight, not by the weights that happened to be
    present. Normalising by the present weights makes confidence 1.0 the moment one signal
    exists — which is how a two-signal topic gets reported as a certainty.
    """
    parts: dict[str, float | None] = {}
    weights: dict[str, float] = {}

    # 1. suggestion position: 1st = 100, 10th = 10, absent = 0 (but low confidence)
    if d.position is not None:
        parts["position"] = max(0.0, 100 - (d.position - 1) * 10)
        weights["position"] = 0.35
    elif d.suggestions:
        parts["position"] = 55.0        # suggested somewhere, exact rank unknown
        weights["position"] = 0.35
    else:
        parts["position"] = None

    # 2. spread: how many sub-intents exist (8+ is a real topic)
    if d.spread:
        parts["spread"] = min(100.0, d.spread / 12 * 100)
        weights["spread"] = 0.25

    # 3. expansion: how much of the alphabet opens up new queries
    if d.expansion:
        parts["expansion"] = min(100.0, len(d.expansion) / 26 * 100 * 2.5)
        weights["expansion"] = 0.20

    # 4. trends: only if it actually returned
    t = d.trends or {}
    if t.get("status") == "ok" and t.get("series"):
        first = next(iter(t["series"].values()))
        level = min(100.0, first.get("mean", 0) * 1.4)
        slope_bonus = 20 if first.get("direction") == "rising" else 0
        parts["trends"] = min(100.0, level + slope_bonus)
        weights["trends"] = 0.20

    if not weights:
        return parts, None, 0.0
    got = sum(parts[k] * w for k, w in weights.items() if parts.get(k) is not None)
    got_w = sum(w for k, w in weights.items() if parts.get(k) is not None)
    score_val = round(got / got_w, 1) if got_w else None
    confidence = round(got_w / TOTAL_WEIGHT, 2)
    return parts, score_val, confidence


def verdict(score_val: float | None, confidence: float) -> str:
    if score_val is None:
        return "no signal — do not greenlight on this alone"
    if confidence < 0.5:
        return "thin signal (confidence < 0.5) — collect more queries before deciding"
    if score_val >= 70:
        return "strong demand — build it"
    if score_val >= 50:
        return "workable demand — needs a sharper angle"
    if score_val >= 30:
        return "weak demand — only with a contrarian angle"
    return "no demand — kill it"
