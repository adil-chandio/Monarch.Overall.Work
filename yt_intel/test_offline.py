"""Offline tests: the maths must be right even where the network is not.

Run: python -m yt_intel.test_offline
These are the tests that protect against the real failure mode of a scraping tool —
publishing a confident number derived from nothing.
"""
import random
import sys

from . import client, decide, demand, forensic, ideas, reverse

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


def t_lockup_states():
    """'No views' and 'Streamed 2 years ago' are states, not missing data."""
    lv = {"contentId": "x", "metadata": {"lockupMetadataViewModel": {
        "title": {"simpleText": "t"},
        "metadata": {"contentMetadataViewModel": {"metadataRows": [
            {"metadataParts": [{"text": {"content": "Chan"}}, {"text": {"content": "No views"}},
                               {"text": {"content": "Streamed 2 years ago"}}]}]}}}}}
    r = client._from_lockup(lv)
    ok("'No views' reads as 0, not None", r["views"] == 0)
    ok("'Streamed 2 years ago' still yields an age", forensic.parse_age_days(r["published"]) == 730)


def t_age_vph():
    ok("3 weeks ago", forensic.parse_age_days("3 weeks ago") == 21)
    ok("8d ago (web lane)", forensic.parse_age_days("8d ago") == 8)
    ok("2w ago", forensic.parse_age_days("2w ago") == 14)
    ok("1mo ago is a month", forensic.parse_age_days("1mo ago") == 30.4)
    ok("2y ago", forensic.parse_age_days("2y ago") == 730)
    ok("45 min ago", forensic.parse_age_days("45 min ago") < 0.05)
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


def t_young_sample():
    """A sample that is all fresh and tiny is young, not crowded — and must say so."""
    young = {"status": "ok", "top3_share": 0.99, "fresh_share_30d": 1.0,
             "winner_ratio": 2595.0, "median_views": 16}
    mature = dict(young, median_views=113940, fresh_share_30d=0.18)
    ok("young sample is not judged concentrated", decide.winnability(young) == 70.0)
    ok("mature concentrated sample still scores low", decide.winnability(mature) < 40)
    r = decide.greenlight({"score": 57.8}, young, {"status": "ok", "share": {"number_in_title": 0.5}},
                          {"status": "ok", "strength": "firm"})
    ok("youngness reaches the objections", any("too new to judge" in a for a in r["strongest_against"]))
    ok("youngness asks for the older sample", any("older comparable sample" in m for m in r["missing"]))


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


def t_decide_access():
    r = decide.greenlight({}, {"status": "empty"}, {"status": "insufficient"}, {},
                          access={"status": "rate_limited", "detail": "429"})
    ok("blocked -> RETRY, not NO", r["verdict"] == "RETRY")
    ok("RETRY names the fix", "API_KEY" in r["next_probe"])


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


def t_comment_mining():
    """Comment shares must name what was said, and refuse to invent a pattern."""
    sample = [{"text": "Please make part 2", "likes": 40, "replies": 1},
              {"text": "what app did you use? where can i get the template", "likes": 9, "replies": 0},
              {"text": "this didn't work on davinci", "likes": 5, "replies": 3}] * 7
    r = forensic.comment_mining(sample)
    ok("comment mining ok above the gate", r["status"] == "ok" and r["n"] == 21)
    ok("finds the sequel ask", any("sequel" in a["label"] for a in r["asks"]))
    ok("finds the tool question", any("tool" in a["label"] for a in r["asks"]))
    ok("finds the objection", any("did not work" in o["label"] for o in r["objections"]))
    ok("names the asset want", any("asset" in w["label"] for w in r["wants"]))
    ok("reading is one actionable line", isinstance(r["reading"], str) and "objection" in r["reading"])
    ok("refuses a tiny sample", forensic.comment_mining(sample[:3])["status"] == "insufficient")
    ok("empty is insufficient, not 'no complaints'", forensic.comment_mining([])["status"] == "insufficient")


def t_ideas():
    out = ideas.generate("ai video", {"suggestions": ["ai video editing", "ai video editing free"]})
    ok("has both families", {i["family"] for i in out} >= {"trend", "curiosity"})
    ok("ranked", [i["rank"] for i in out] == list(range(1, len(out) + 1)))
    ok("every idea has a risk", all(i["risk"] for i in out))
    ok("wtf bank non-empty", len(ideas.wtf_bank("ai video")) >= 3)


if __name__ == "__main__":
    print("yt-intel offline tests")
    for fn in [t_duration, t_lockup_states, t_age_vph, t_saturation, t_young_sample, t_title_signal_refuses, t_title_signal_recovers,
               t_funnel_gate, t_hook_parsing, t_demand_scoring, t_decide_access, t_decide_never_silent, t_comment_mining, t_reverse, t_ideas]:
        fn()
    print(f"\n{PASS} assertions passed")
    sys.exit(0)
