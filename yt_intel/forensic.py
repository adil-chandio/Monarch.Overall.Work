"""Forensic and reverse-engineering analysis of a topic's existing videos.

Three questions, three separate answer sets:

  SATURATION   how many people already made this, and how well did it go?
  MECHANISM    what exactly did the winners do in the first 30 seconds?
  TITLE MATH   which words and structures actually correlate with view counts?

The regression in `title_signal()` is deliberately small: with 20-200 rows a full model
overfits and lies. A ridge regression on log(views) with three features produces a
coefficient you can read out loud ("title length +10 chars ≈ +11% views on this sample")
and a confidence that degrades honestly as the sample shrinks.

Durations: the API returns ISO-8601 (`PT12M3S`); the web lane returns `12:03`. Both are
parsed to seconds, because retention stories are all about minutes.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, asdict

from . import client

STOP = set("a an the and or but of to in on for with at by from is are was were be been "
           "this that these those i you he she it we they my your his her its our their "
           "how what why when where who which do does did not no so if then than as".split())


def parse_duration(s: str) -> int:
    """`PT1H2M3S` or `1:02:03` -> seconds. 0 when unknown."""
    if not s:
        return 0
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    if m:
        h, mi, se = (int(x) if x else 0 for x in m.groups())
        return h * 3600 + mi * 60 + se
    parts = [p for p in s.split(":") if p.strip().isdigit()]
    if not parts:
        return 0
    secs = 0
    for p in parts:
        secs = secs * 60 + int(p)
    return secs


_REL = re.compile(r"^\s*(\d+)\s*(s|sec|m|min|h|hr|d|day|w|wk|mo|month|y|yr)?\s*(?:ago)?\s*$", re.I)
_ABBR = [
    # order matters: 'mo' before 'm', 'min' before 'm'
    (re.compile(r"^\s*(\d+)\s*(?:mo|month)s?\s*(?:ago)?", re.I), 30.4),
    (re.compile(r"^\s*(\d+)\s*(?:min|minute)s?\s*(?:ago)?", re.I), 1 / 1440),
    (re.compile(r"^\s*(\d+)\s*(?:y|yr|year)s?\s*(?:ago)?", re.I), 365.0),
    (re.compile(r"^\s*(\d+)\s*(?:w|wk|week)s?\s*(?:ago)?", re.I), 7.0),
    (re.compile(r"^\s*(\d+)\s*(?:d|day)s?\s*(?:ago)?", re.I), 1.0),
    (re.compile(r"^\s*(\d+)\s*(?:h|hr|hour)s?\s*(?:ago)?", re.I), 1 / 24),
    (re.compile(r"^\s*(\d+)\s*(?:s|sec|second)s?\s*(?:ago)?", re.I), 1 / 86400),
]


def parse_age_days(published: str) -> float | None:
    """'3 weeks ago' / '8d ago' / '1mo ago' / ISO date -> age in days.

    The web lane abbreviates, and the long-form regex missed every abbreviation silently —
    which is why the first live run produced a full sample with every views/hour blank.
    A missing age is not a small gap: it silently disables the only fair speed metric.
    """
    if not published:
        return None
    m = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year)", published, re.I)
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        mult = {"second": 1/86400, "minute": 1/1440, "hour": 1/24, "day": 1, "week": 7,
                "month": 30.4, "year": 365}[unit]
        return round(n * mult, 2)
    for pat, mult in _ABBR:
        m = pat.match(published)
        if m:
            return round(int(m.group(1)) * mult, 2)
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", published)
    if m:
        import datetime as dt
        then = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return round((dt.date.today() - then).days, 2)
    return None


def vph(views: int | None, age_days: float | None) -> float | None:
    """Views per hour since publish. The only fair cross-video speed metric."""
    if views is None or not age_days or age_days <= 0:
        return None
    return round(views / (age_days * 24), 2)


# ------------------------------------------------------------------ title analysis
def tokens(title: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9']+", (title or "").lower()) if t not in STOP and len(t) > 2]


def title_signal(rows: list[dict], min_n: int = 20) -> dict:
    """Ridge regression of log10(views) on four title features.

    Sample-size discipline, because this is the single easiest place to publish a lie:
      n < min_n        -> refuse ("insufficient"), no coefficients at all
      n >= 5 * params  -> "firm"
      otherwise        -> "weak", coefficients still shown but marked unreliable
    Features are standardised before the fit, so the ridge penalty is comparable across
    them and a coefficient is "log10 views per 1 SD of this feature".
    """
    data = [r for r in rows if r.get("views") and r.get("title")]
    if len(data) < min_n:
        return {"status": "insufficient", "n": len(data), "required": min_n,
                "detail": "a coefficient fitted on fewer rows than this is noise dressed as insight"}

    raw = []
    for r in data:
        t = r["title"]
        raw.append([
            len(t),
            1.0 if re.search(r"\d", t) else 0.0,
            1.0 if t.strip().endswith("?") else 0.0,
            1.0 if re.search(r"\b[A-Z]{4,}\b", t) else 0.0,
        ])
    y = [math.log10(r["views"]) for r in data]

    cols = list(zip(*raw))
    mu = [sum(c) / len(c) for c in cols]
    sd = [math.sqrt(sum((v - m) ** 2 for v in c) / len(c)) or 1.0 for c, m in zip(cols, mu)]
    X = [[1.0] + [(v - m) / s for v, m, s in zip(row, mu, sd)] for row in raw]

    # ridge penalty is small relative to n (data is standardised, so the Gram matrix
    # scales with n); a fixed 2.0 over-shrank a 120-row sample and hid a real signal
    lam = max(0.5, len(X) * 0.02)
    k = len(X[0])
    A = [[sum(row[i] * row[j] for row in X) + (lam if i == j and i else 0) for j in range(k)] for i in range(k)]
    b = [sum(row[i] * yy for row, yy in zip(X, y)) for i in range(k)]
    beta = _solve(A, b)

    # in-sample R^2 and leave-one-out error: how much would we actually trust this?
    pred = [sum(bi * xi for bi, xi in zip(beta, row)) for row in X]
    ybar = sum(y) / len(y)
    ss_tot = sum((v - ybar) ** 2 for v in y) or 1e-9
    ss_res = sum((p - v) ** 2 for p, v in zip(pred, y))
    r2 = 1 - ss_res / ss_tot

    loo = []
    for i in range(len(X)):
        Ai = [[v for j2, v in enumerate(row) if True] for row in A]
        for a in range(k):
            for c in range(k):
                Ai[a][c] -= X[i][a] * X[i][c]
            Ai[a][a] += lam if a else 0
        bi_ = [b[a] - X[i][a] * y[i] for a in range(k)]
        try:
            bb = _solve(Ai, bi_)
            loo.append(sum(bv * xv for bv, xv in zip(bb, X[i])) - y[i])
        except Exception:
            pass
    loo_rmse = math.sqrt(sum(e * e for e in loo) / len(loo)) if loo else None

    names = ["intercept", "length_per_sd", "has_number", "question_form", "shouted_word"]
    coef = {n: round(v, 4) for n, v in zip(names, beta)}

    # beta is per 1 SD, so a ONE-UNIT change in the raw feature is beta/sd.
    # For a 0/1 flag sd is 0.5, which is exactly why the naive 10**beta under-reports a
    # binary effect by half. Converting back to raw units fixes that.
    per_unit = [beta[j + 1] / (sd[j] or 1.0) for j in range(len(sd))]
    effects = {
        "length_+10chars_pct": round((10 ** (per_unit[0] * 10) - 1) * 100, 1),
        "has_number_pct": round((10 ** per_unit[1] - 1) * 100, 1),
        "question_form_pct": round((10 ** per_unit[2] - 1) * 100, 1),
        "shouted_word_pct": round((10 ** per_unit[3] - 1) * 100, 1),
    }
    strength = "firm" if len(data) >= 5 * (k - 1) and (loo_rmse is None or loo_rmse < 0.6) else "weak"
    return {
        "status": "ok", "n": len(data), "strength": strength,
        "coef": coef, "effect_pct": effects,
        "fit": {"r2": round(r2, 3), "loo_rmse_log10": round(loo_rmse, 3) if loo_rmse is not None else None},
        "read": (
            f"titles containing a number performed {effects['has_number_pct']:+.0f}% vs those without "
            f"(n={len(data)}, R2={r2:.2f})"
        ),
        "caveat": "correlational, single sample; a prior for a decision, never proof of causation",
    }


def _solve(A, b):
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            continue
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [vr - f * vc for vr, vc in zip(M[r], M[c])]
    return [M[i][n] for i in range(n)]


def word_signal(rows: list[dict], min_n: int | None = None) -> dict:
    """Which words appear in the high-view half vs the low-view half."""
    data = [r for r in rows if r.get("views") and r.get("title")]
    if len(data) < 10:
        return {"status": "insufficient", "n": len(data), "required": 10}
    min_n = min_n or max(2, round(len(data) * 0.12))
    data.sort(key=lambda r: -r["views"])
    half = len(data) // 2
    top, bot = data[:half], data[half:]
    def counts(rs):
        c: dict[str, int] = {}
        for r in rs:
            for t in set(tokens(r["title"])):
                c[t] = c.get(t, 0) + 1
        return c
    ct, cb = counts(top), counts(bot)
    words = set(ct) | set(cb)
    lift = []
    for w in words:
        a, b2 = ct.get(w, 0), cb.get(w, 0)
        if a + b2 < min_n:
            continue
        lift.append({"word": w, "top": a, "bottom": b2, "lift": round((a + 0.5) / (b2 + 0.5), 2)})
    lift.sort(key=lambda r: -r["lift"])
    return {"status": "ok", "n": len(data), "winners": lift[:15], "losers": lift[-10:][::-1]}


def funnel(rows: list[dict], min_n: int = 15) -> dict:
    """Title/thumbnail hooks that recur in the winning slice."""
    data = [r for r in rows if r.get("views")]
    if len(data) < min_n:
        return {"status": "insufficient", "n": len(data), "required": min_n}
    data.sort(key=lambda r: -r["views"])
    top = data[:max(3, round(len(data) * 0.25))]
    pats = {
        "number_in_title": r"\d",
        "question": r"\?",
        "you_form": r"\byou\b|\byour\b",
        "contrarian": r"\bwrong\b|\bmistake\b|\bnever\b|\bstop\b|\bnobody\b|\bno one\b",
        "urgency": r"\bnow\b|\btoday\b|\b2026\b|\bnew\b",
        "curiosity_gap": r"\bthis\b|\bwhy\b|\bhow\b|\bsecret\b|\btruth\b|\bnobody\b",
        "superlative": r"\bbest\b|\bworst\b|\bfastest\b|\beasiest\b|\bonly\b|\bultimate\b",
        "wtf": r"\binsane\b|\bcrazy\b|\bimpossible\b|\bunbelievable\b|\bwtf\b|\bwhat if\b",
    }
    hits = {name: sum(1 for r in top if re.search(p, r["title"], re.I)) for name, p in pats.items()}
    total = len(top)
    return {
        "status": "ok", "n_top": total,
        "share": {k: round(v / total, 2) for k, v in hits.items()},
        "titles": [r["title"] for r in top[:5]],
    }


def psych_profile(rows: list[dict]) -> dict:
    """Map winning structures onto the drives they exploit. Labelled, not asserted."""
    f = funnel(rows)
    if f.get("status") != "ok":
        return {"status": f.get("status", "empty"),
                "detail": "psych prof_iles need a real sample; with %s videos this would be astrology" % f.get("n", 0)}
    s = f["share"]
    drivers = []
    if s["curiosity_gap"] >= 0.5:
        drivers.append(("curiosity gap", "open loop the brain must close", s["curiosity_gap"]))
    if s["contrarian"] >= 0.3:
        drivers.append(("contrarian", "threat to a belief the viewer already holds", s["contrarian"]))
    if s["wtf"] >= 0.2:
        drivers.append(("wtf / impossibility", "schema violation — the brain flags it as an error to resolve", s["wtf"]))
    if s["number_in_title"] >= 0.5:
        drivers.append(("specificity", "a number reads as evidence; vagueness reads as sales", s["number_in_title"]))
    if s["you_form"] >= 0.3:
        drivers.append(("self-reference", "the 'you' effect: self-relevant stimuli get more attention", s["you_form"]))
    if s["superlative"] >= 0.3:
        drivers.append(("ranking", "brains prefer a winner to a list", s["superlative"]))
    return {"status": "ok", "drivers": [{"driver": d, "mechanism": m, "share": v} for d, m, v in drivers],
            "note": "shares are measured on this sample's top decile, not a general law"}


# ------------------------------------------------------------------ saturation
def saturation(rows: list[dict]) -> dict:
    data = [r for r in rows if r.get("views") is not None]
    if not data:
        return {"status": "empty"}
    views = sorted((r["views"] for r in data), reverse=True)
    n = len(views)
    total = sum(views)
    top3 = sum(views[:3])
    ages = [a for a in (r.get("age_days") for r in data) if a]
    fresh = sum(1 for a in ages if a <= 30) / len(ages) if ages else None
    return {
        "status": "ok", "videos": n,
        "total_views": total,
        "median_views": views[n // 2],
        "top3_share": round(top3 / total, 3) if total else None,
        "winner_ratio": round(views[0] / max(1, views[n // 2]), 1),
        "fresh_share_30d": round(fresh, 2) if fresh is not None else None,
        "reading": (
            "concentrated — a few videos own the topic, a new entrant must out-execute them"
            if total and top3 / total > 0.7 else
            "distributed — no single video owns it, entry is feasible"
        ) if total else "",
    }


# --------------------------------------------------------------------------- comments
DEMAND_PHRASES = [
    # a request for more / next: the cheapest content brief that exists
    (r"\b(part|pt\.?)\s*(2|ii|two)\b|\bnext video\b|\bmore (of )?this\b|\bplease make\b|\bdo more\b", "asked for a sequel"),
    (r"\bwhat about\b|\bcan you (do|make|cover)\b|\bhow (do|did) you\b|\btutorial (on|for)\b", "asked for a sibling topic"),
    (r"\bwhere (can|do) i (get|find|download)\b|\bwhat (app|tool|software|site)\b|\bwhich (tool|software)\b", "asked which tool (buying intent)"),
]
OBJECTION_PHRASES = [
    (r"\b(didn'?t|doesn'?t|not) work\b|\bwrong\b|\bmisleading\b|\bclickbait\b", "said it did not work"),
    (r"\bexpensive\b|\btoo (much|costly)\b|\bpaid\b|\bnot free\b", "objected to cost"),
    (r"\btoo (fast|slow|long|short)\b|\bconfus(ing|ed)\b|\bhard to follow\b", "objected to pacing/clarity"),
]
WANT_PHRASES = [
    (r"\b(file|download|template|preset|project|link|checklist)\b", "wants the asset"),
    (r"\bcourse\b|\bmentorship\b|\bcoaching\b|\bconsult\b|\bhire\b", "wants to buy time/teaching"),
]


def comment_mining(comments: list[dict], min_n: int = 20) -> dict:
    """What the audience said, sorted into the three things that change a script.

    Deliberately phrase-led, not sentiment-scored: a general "sentiment: 0.62" reading is
    unfalsifiable and cannot be written into a video. "9 of 100 asked for part 2, 6 said it
    did not work" can be acted on tomorrow and checked next month.

    Refuses below `min_n` for the same reason as the title regression: shares computed on
    nine comments are a rumour with a decimal point.
    """
    texts = [c.get("text", "") for c in comments if c.get("text")]
    if len(texts) < min_n:
        return {
            "status": "insufficient", "n": len(texts), "required": min_n,
            "detail": "too few comments to read a pattern; widen the sample or pick a bigger video",
        }

    def share(bucket):
        hits = []
        for rx, label in bucket:
            n = sum(1 for t in texts if re.search(rx, t, re.I))
            if n:
                hits.append({"label": label, "n": n, "share": round(n / len(texts), 3)})
        return sorted(hits, key=lambda h: -h["n"])

    demand_asks = share(DEMAND_PHRASES)
    objections = share(OBJECTION_PHRASES)
    wants = share(WANT_PHRASES)

    top = sorted(comments, key=lambda c: -(c.get("likes") or 0))[:5]
    return {
        "status": "ok",
        "n": len(texts),
        "asks": demand_asks,
        "objections": objections,
        "wants": wants,
        "top_liked": [{"likes": c.get("likes"), "replies": c.get("replies"),
                       "text": (c.get("text") or "")[:220]} for c in top],
        "reading": _comment_reading(demand_asks, objections, wants),
        "caveat": "shares are of the comments fetched, not of everyone who watched; "
                  "a silent majority is invisible here by construction",
    }


def _comment_reading(asks: list[dict], objections: list[dict], wants: list[dict]) -> str:
    parts = []
    if asks:
        parts.append(f"the audience is asking for more: {asks[0]['label']} ({asks[0]['share']:.0%})")
    if objections:
        parts.append(f"the loudest objection is {objections[0]['label']} ({objections[0]['share']:.0%}) — fix that in the remake")
    if wants:
        parts.append(f"{wants[0]['label']} ({wants[0]['share']:.0%}) is the conversion surface")
    if not parts:
        return "no request, objection or asset-ask cleared the threshold — this comment field cannot brief a video"
    return "; ".join(parts)
