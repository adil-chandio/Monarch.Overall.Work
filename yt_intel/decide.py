"""The greenlight decision. One verdict, with its receipts and its objections.

A recommendation nobody can audit is just a mood. So `greenlight()` returns:

  verdict          GO / SHARPEN / NO  (+ a one-line reason)
  score            0-100, weighted, with the weights printed
  strongest_for    the two or three facts that carried the decision
  strongest_against the facts that argue the other way — always non-empty
  missing          signals that would change the answer if we had them
  next_probe       the cheapest experiment that would settle the weakest assumption

`strongest_against` is mandatory by design. A tool that can only say yes is a sales
tool, not a decision tool.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

WEIGHTS = {
    "demand": 0.30,        # autocomplete position/spread/trends
    "winnability": 0.25,   # saturation shape: can a new entrant actually break in?
    "mechanism": 0.20,     # do the winners reveal a repeatable structure?
    "fit": 0.15,           # can THIS studio execute it at its current level?
    "timing": 0.10,        # rising vs decaying
}


# 50 is deliberately not a good score and not a bad one. A placeholder should pull the
# assembled decision toward "not yet", never toward "go".
YOUNG_SAMPLE_PLACEHOLDER = 50.0


YOUNG_MAX_AGE_DAYS = 14


def is_young_sample(sat: dict) -> bool:
    """The sample has not had time to settle, so concentration cannot be read from it.

    Two ways to be young, and the first one is the one that was missed:

    * every row is very new (`median_age_days` under two weeks) — a `--order date` sample is
      this by construction. A live case: 30 rows aged 0.10-0.46 days, median 238 views, every
      one under 12 hours old. The old guard demanded `median_views < 100`, so 238 slipped
      through and the topic scored SHARPEN 62.3 at confidence 0.75 while the saturation
      reading on the same card said "too young to judge".
    * almost nothing has double-digit views (`median_views < 100` with 80% under 30 days).

    Age is the honest signal. View count is the symptom, and at 238 median views the symptom
    was too small to notice.
    """
    if sat.get("status") != "ok":
        return False
    age = sat.get("median_age_days")
    if age is not None and age < YOUNG_MAX_AGE_DAYS:
        return True
    median = sat.get("median_views")
    fresh = sat.get("fresh_share_30d")
    return median is not None and median < 100 and (fresh or 0) >= 0.8


def winnability(sat: dict) -> float | None:
    """"Can we break in" from the saturation shape alone."""
    if sat.get("status") != "ok":
        return None
    top3 = sat.get("top3_share")
    fresh = sat.get("fresh_share_30d")
    ratio = sat.get("winner_ratio")
    median = sat.get("median_views")
    # A sample where almost nothing has double-digit views is not a crowded topic — it is a
    # young one. Concentration measured on unreleased/just-released videos says nothing about
    # who owns the market, and scoring it as "a few videos own this" inverts the advice.
    # (Live case: a thisMonth sample with a 16-view median scored winnability 29 and NO.)
    if is_young_sample(sat):
        # This is a placeholder, not a measurement: the sample had no time to concentrate.
        # Returning a good score here is defensible; returning it at full confidence is not,
        # and the old code did exactly that — a `--order date` sample (median 238 views, every
        # row under 12 hours old) scored SHARPEN 62.2 at high confidence while the saturation
        # reading on the same report said "too young to judge". The verdict and the honest
        # reading contradicted each other in public. The number below is neutral so the
        # assembled score is visibly a guess (and `young_sample` in `missing` says why).
        return YOUNG_SAMPLE_PLACEHOLDER
    if top3 is None:
        return None
    # concentrated topics are hard; fresh uploads mean the topic is still live
    base = 100 * (1 - min(1.0, top3))
    if fresh is not None:
        base += 40 * min(1.0, fresh / 0.35)         # 35 %+ fresh = full marks
    if ratio and ratio > 30:
        base -= 12                                   # one runaway winner dominates
    return max(0.0, min(100.0, base))


def mechanism_strength(funnel: dict, title_sig: dict) -> float | None:
    """Is there a readable, repeatable structure in the winners?"""
    if funnel.get("status") != "ok":
        return None
    shares = funnel.get("share", {})
    if not shares:
        return None
    hits = sum(1 for v in shares.values() if v >= 0.3)
    base = min(100.0, hits / 4 * 100)
    if title_sig.get("status") == "ok":
        base += 10 if title_sig.get("strength") == "firm" else 0
    return max(0.0, min(100.0, base))


def timing(trends: dict) -> float | None:
    if trends.get("status") != "ok":
        return None
    series = trends.get("series") or {}
    if not series:
        return None
    first = next(iter(series.values()))
    d = first.get("direction")
    return {"rising": 90.0, "flat": 55.0, "falling": 20.0}.get(d)


def fit_score(fit: dict | None) -> float | None:
    """Studio fit: can we actually shoot this with what we own?

    `fit` is supplied by the caller from config: {assets_ready, skills_ready, hours_estimate}.
    Missing fit is not a zero — it lowers confidence.
    """
    if not fit:
        return None
    a = 1.0 if fit.get("assets_ready") else 0.4
    s = 1.0 if fit.get("skills_ready") else 0.5
    hours = fit.get("hours_estimate")
    h = 1.0 if not hours else max(0.2, min(1.0, 16.0 / hours))
    return round(100 * (0.4 * a + 0.35 * s + 0.25 * h), 1)


def greenlight(demand: dict, sat: dict, funnel: dict, title_sig: dict,
               trends: dict | None = None, fit: dict | None = None,
               access: dict | None = None) -> dict:
    """`access` = {"status": "ok"|"rate_limited"|"blocked", "detail": "..."}.

    This distinction is the whole point of the function. "We measured nothing" and "we
    could not measure" produce the same empty numbers and completely different advice:
    the first is a NO, the second is a RETRY from another network. Collapsing them is how
    a good topic gets killed by a blocked IP.
    """
    access = access or {}
    if access.get("status") in ("rate_limited", "blocked", "error"):
        return {
            "verdict": "RETRY", "score": None, "confidence": 0.0,
            "reason": f"could not measure ({access['status']}) — this is an access problem, not a demand problem",
            "parts": {}, "weights": WEIGHTS,
            "strongest_for": [], "strongest_against": [f"no data: {access.get('detail','')[:160]}"],
            "missing": ["everything — the sample never arrived"],
            "next_probe": (
                "run the same command with YOUTUBE_API_KEY set (free, 10k units/day), or from a "
                "residential network / a browser session. A datacenter IP gets throttled by YouTube "
                "by design — that is the tool telling the truth, not the topic failing."
            ),
            "access": access,
        }
    parts = {
        "demand": demand.get("score") if isinstance(demand, dict) else None,
        "winnability": winnability(sat),
        "mechanism": mechanism_strength(funnel, title_sig),
        "fit": fit_score(fit),
        "timing": timing(trends or demand.get("trends", {}) if isinstance(demand, dict) else {}),
    }
    # recorded, because a score built on a placeholder must be able to say so
    placeholder_used = is_young_sample(sat)
    used = {k: v for k, v in parts.items() if v is not None}
    if not used:
        return {"verdict": "NO", "score": None, "reason": "no measurable signal at all — do not spend a day on it",
                "parts": parts, "strongest_for": [], "strongest_against": ["nothing was measurable"],
                "missing": list(WEIGHTS), "next_probe": "run the topic through autocomplete + a 20-video search sample first"}

    wsum = sum(WEIGHTS[k] for k in used)
    score = round(sum(WEIGHTS[k] * v for k, v in used.items()) / wsum, 1)
    # A placeholder must not buy confidence. It stays in the score (the score has to mean
    # something) but is excluded from the denominator's credit, so a decision resting on
    # "could not tell yet" reads as low-confidence instead of well-supported.
    credit = wsum - (WEIGHTS["winnability"] if placeholder_used and "winnability" in used else 0)
    confidence = round(max(0.0, credit) / sum(WEIGHTS.values()), 2)

    for_, against, missing = [], [], []

    if parts["demand"] is not None and parts["demand"] >= 65:
        for_.append(f"demand signal {parts['demand']:.0f}/100 (autocomplete + trends)")
    # A placeholder must never be narrated as an observation. Live case: a young sample got
    # "a few videos already own this topic (winnability 50)" — a claim about ownership, made
    # from a number that exists precisely because ownership could not be measured.
    if placeholder_used:
        for_.append("winnability could not be measured — the sample is too new to concentrate")
    elif parts["winnability"] is not None:
        if parts["winnability"] >= 60:
            for_.append(f"the topic is not owned by one video (winnability {parts['winnability']:.0f})")
        else:
            against.append(f"a few videos already own this topic (winnability {parts['winnability']:.0f})")
    if parts["mechanism"] is not None and parts["mechanism"] >= 60:
        for_.append("the winners share a readable structure we can copy at the mechanism level")
    if parts["timing"] is not None and parts["timing"] >= 80:
        for_.append("interest is rising, not decaying")
    elif parts["timing"] is not None and parts["timing"] <= 25:
        against.append("interest is decaying — this is a topic of last quarter")
    if parts["fit"] is not None and parts["fit"] < 55:
        against.append(f"studio fit is {parts['fit']:.0f}/100 — we would be learning on camera")
    if sat.get("status") == "ok" and sat.get("fresh_share_30d") is not None and sat["fresh_share_30d"] < 0.1:
        against.append("almost nobody uploaded on this in the last 30 days — could be satiated or dead")
    if (sat.get("status") == "ok" and sat.get("median_views") is not None
            and sat["median_views"] < 100 and (sat.get("fresh_share_30d") or 0) >= 0.8):
        against.append(
            f"the sample is too new to judge — median {sat['median_views']} views with "
            f"{sat['fresh_share_30d']:.0%} uploaded in the last 30 days, so 'nobody owns it' "
            "may just mean 'nobody has watched it yet'"
        )
        missing.append("an older comparable sample (relevance order) to judge the real ceiling")
        # Say it in the same words the score uses, so the number and the note agree.
        against.append("winnability is a placeholder at 50/100, not a measurement — it has been "
                       "excluded from the confidence figure for this reason")
    for k, label in (("fit", "studio fit data"), ("timing", "trend direction")):
        if parts[k] is None:
            missing.append(label)
    if not against:
        against.append("no objection found in the data — which itself is a reason to check the sample")

    # GO means all three of its own words are true: demand, entry room *and* a readable
    # mechanism. A live case scored 70 with mechanism 25 and was labelled GO with the reason
    # "a readable mechanism" — the verdict was copying its own template, not its evidence.
    mechanism_clear = parts["mechanism"] is None or parts["mechanism"] >= 55
    if score >= 70 and confidence >= 0.6 and mechanism_clear:
        verdict, reason = "GO", "demand, entry room and a readable mechanism all clear"
    elif score >= 70 and confidence >= 0.6:
        verdict, reason = "SHARPEN", (
            "the topic is live but we cannot yet see how the winners are built — "
            "teardown the top 5 before committing a production day"
        )
    elif score >= 52 and (parts["mechanism"] or 100) < 55:
        # Same score band, different bottleneck: say which one it is, because the next action
        # differs (fix the mechanism vs. sharpen the angle).
        verdict, reason = "SHARPEN", (
            "the topic is live but we cannot yet see how the winners are built — "
            "teardown the top 5 before committing a production day"
        )
    elif score >= 52:
        verdict, reason = "SHARPEN", "the topic is live but the angle is not yet differentiated"
    else:
        verdict, reason = "NO", "the numbers do not support a day of production"

    probe = _next_probe(parts, sat, demand)
    return {
        "verdict": verdict, "score": score, "confidence": confidence, "reason": reason,
        "access": access or {"status": "ok"},
        "parts": parts, "weights": WEIGHTS,
        "strongest_for": for_ or ["nothing cleared a threshold"],
        "strongest_against": against,
        "missing": missing,
        "next_probe": probe,
    }


def _next_probe(parts: dict, sat: dict, demand: dict) -> str:
    if parts.get("demand") is None:
        return "sample 30 search results for this exact phrase, then re-run"
    if (parts.get("winnability") or 100) < 55:
        return "find the 3 videos that own it and reverse-engineer them (yt-intel reverse <id>) before deciding"
    if (parts.get("mechanism") or 100) < 55:
        return "teardown the top 5 by views; if no shared structure emerges, the topic is luck-driven"
    if parts.get("fit") is not None and parts["fit"] < 55:
        return "shoot a 30-second pilot of the hardest shot before committing to the full build"
    return "write the hook and title first; if they score under 80, the topic will not save them"
