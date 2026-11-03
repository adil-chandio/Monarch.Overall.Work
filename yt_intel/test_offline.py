"""Offline tests: the maths must be right even where the network is not.

Run: python -m yt_intel.test_offline
These are the tests that protect against the real failure mode of a scraping tool —
publishing a confident number derived from nothing.
"""
import random
import sys

from . import decide, demand, forensic, ideas, reverse

PASS = 0


def ok(name, cond, detail=""):
    global PASS
    if not cond:
        raise AssertionError(f"{name} {detail}")
    PASS += 1
    print(f"  ok  {name}")


def t_duration():
    ok("PT1H2M3S", forensic.parse_duration("PT1H2M3S") == 3723)
    ok("12:03", forensic.parse_duration("12:03") == 723)
    ok("1:00:00", forensic.parse_duration("1:00:00") == 3600)
    ok("empty", forensic.parse_duration("") == 0)


def t_age_vph():
    ok("3 weeks ago", forensic.parse_age_days("3 weeks ago") == 21)
    ok("iso date", forensic.parse_age_days("2026-11-01") is not None)
    ok("vph", forensic.vph(1000, 10) == round(1000 / 240, 2))
    ok("vph needs age", forensic.vph(1000, None) is None)


def t_saturation():
    rows = [{"views": v} for v in (1000, 2000, 3000, 4000)]
    s = forensic.saturation(rows)
    ok("median", s["median_views"] == 3000 or s["median_views"] == 2000, s["median_views"])
    ok("total", s["total_views"] == 10000)
    ok("empty", forensic.saturation([])["status"] == "empty")


def t_title_signal_refuses():
    small = [{"title": f"t{i}", "views": 100 * i} for i in range(1, 8)]
    r = forensic.title_signal(small)
    ok("refuses n<20", r["status"] == "insufficient" and "coef" not in r)


def t_title_signal_recovers():
    random.seed(3)
    rows = []
    for i in range(120):
        num = i % 2 == 0
        title = ("100 " if num else "") + "a" * random.randint(20, 60)
        # ground truth: numbers worth 3x
        views = int((2600 if num else 900) * random.uniform(0.6, 1.6))
        rows.append({"title": title, "views": views})
    r = forensic.title_signal(rows)
    ok("fits", r["status"] == "ok" and r["n"] == 120)
    ok("detects the planted number effect", r["effect_pct"]["has_number_pct"] > 100, r["effect_pct"])
    ok("reports fit", 0 <= r["fit"]["r2"] <= 1, r["fit"])


def t_funnel_gate():
    ok("funnel refuses small", forensic.funnel([{"views": 1, "title": "x"}])["status"] == "insufficient")
    ok("psych refuses small", forensic.psych_profile([{"views": 1, "title": "x"}])["status"] == "insufficient")


def t_hook_parsing():
    rows = [{"title": f"Best {i} AI tool 2026?", "views": 10 ** (3 + i % 4)} for i in range(40)]
    f = forensic.funnel(rows)
    ok("funnel ok at 40", f["status"] == "ok")
    ok("number share 1.0", f["share"]["number_in_title"] == 1.0)
    ok("question share 1.0", f["share"]["question"] == 1.0)


def t_demand_scoring():
    d = demand.Demand(topic="x")
    _, s, c = demand.score(d)
    ok("no data -> no score", s is None and c == 0.0)
    d.suggestions = ["x", "x y"]
    d.position = 1
    d.spread = 6
    parts, s2, c2 = demand.score(d)
    ok("partial data -> partial confidence", s2 is not None and 0 < c2 < 1)


def t_decide_never_silent():
    r = decide.greenlight({}, {"status": "empty"}, {"status": "insufficient"}, {})
    ok("no data -> NO", r["verdict"] == "NO")
    ok("always has an objection", len(r["strongest_against"]) >= 1)
    ok("always has a next probe", bool(r["next_probe"]))
    good = decide.greenlight({"score": 80, "trends": {"status": "ok", "series": {"x": {"direction": "rising"}}}},
                             {"status": "ok", "top3_share": 0.4, "fresh_share_30d": 0.3, "winner_ratio": 5},
                             {"status": "ok", "share": {"number_in_title": .6, "curiosity_gap": .7, "contrarian": .4, "you_form": .3}},
                             {"status": "ok", "strength": "firm"},
                             fit={"assets_ready": True, "skills_ready": True, "hours_estimate": 8})
    ok("strong data -> GO", good["verdict"] == "GO", good)
    ok("GO still lists objections", len(good["strongest_against"]) >= 1)


def t_reverse():
    ok("reading grade low for simple text",
       reverse.reading_grade("This is short. It is clear. It is easy.") < 4)
    ok("claim type contrarian", reverse._claim_type("nobody tells you this") == "contrarian correction")
    ok("claim type hypothetical", reverse._claim_type("what if you could") == "hypothetical")
    ok("hook window respects wpm", len(reverse.hook_window([str(i) for i in range(40)])) == 8)
    t = {"receipt": {"age_days": 400}, "hook": {"opens_with_number": False},
         "script": {"reading_grade": 11, "cta_count": 5, "wpm": 100}}
    rep = reverse._replication(t)
    ok("replication always actionable", rep["change"] and rep["beat"])


def t_ideas():
    out = ideas.generate("ai video", {"suggestions": ["ai video editing", "ai video editing free"]})
    ok("has both families", {i["family"] for i in out} >= {"trend", "curiosity"})
    ok("ranked", [i["rank"] for i in out] == list(range(1, len(out) + 1)))
    ok("every idea has a risk", all(i["risk"] for i in out))
    ok("wtf bank non-empty", len(ideas.wtf_bank("ai video")) >= 3)


if __name__ == "__main__":
    print("yt-intel offline tests")
    for fn in [t_duration, t_age_vph, t_saturation, t_title_signal_refuses, t_title_signal_recovers,
               t_funnel_gate, t_hook_parsing, t_demand_scoring, t_decide_never_silent, t_reverse, t_ideas]:
        fn()
    print(f"\n{PASS} assertions passed")
    sys.exit(0)
