"""Offline tests: the maths must be right even where the network is not.

Run: python -m yt_intel.test_offline
These are the tests that protect against the real failure mode of a scraping tool —
publishing a confident number derived from nothing.
"""
import random
import sys

from . import client, decide, demand, forensic, http, ideas, reverse

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


def t_thumbprint_accent():
    """The accent must be a colour, not the darkest corner of the frame.

    Regression: the first version quantised RGB and took the biggest cube. On twelve real
    thumbnails it returned #0c1213, #080c0c, #0d0705 — near-black — for every one, and the
    channel-level hex table read as "no house colour" for a channel that clearly had one.
    """
    import numpy as np
    from . import thumbprint

    dark = np.full((360, 480, 3), 0.03, np.float32)
    dark[100:250, 120:380] = np.array([0.02, 0.45, 0.95], np.float32)
    r = thumbprint.analyse(dark, "synthetic")
    ok("accent is the blue block, not the black frame",
       r["dominant"] is not None and r["dominant"]["hue_deg"] is not None
       and 190 <= r["dominant"]["hue_deg"] <= 240)
    ok("accent hex is blue-dominant", int(r["dominant"]["hex"][5:7], 16) > int(r["dominant"]["hex"][1:3], 16))

    flat = np.full((360, 480, 3), 0.5, np.float32)
    ok("a flat grey frame has no accent to report", thumbprint.analyse(flat, "synthetic")["dominant"] is None)


def t_hue_families_sum():
    """Families must partition the sample. Regression: 22 and 7 degrees listed separately,
    each with 6, over a sample of 12 thumbnails — 22 counted faces in a 12-face sample."""
    from . import thumbprint
    fam = thumbprint._hue_families([22, 7, 202, 187, 7, 22, 7, 22, 202, 187, 7, 22])
    ok("families sum to exactly the sample size", sum(n for _, n in fam) == 12)
    ok("22 and 7 degrees are one family", [n for name, n in fam if name == "red"] == [8])
    ok("families are named, not degree numbers", all(isinstance(k, str) for k, _ in fam))
    ok("an empty sample yields no families", thumbprint._hue_families([]) == [])


def t_style_calibration():
    """The shipped cut threshold must not be the one that under-counts by a third."""
    from . import style
    ok("threshold is the calibrated value, not the old 0.22", style.CUT_THRESHOLD <= 0.16)
    ok("threshold still ignores noise-level motion", style.CUT_THRESHOLD >= 0.08)


def t_saturation():
    rows = [{"views": v} for v in (1000, 2000, 3000, 4000)]
    s = forensic.saturation(rows)
    ok("median", s["median_views"] == 3000 or s["median_views"] == 2000, s["median_views"])
    ok("total", s["total_views"] == 10000)
    ok("empty", forensic.saturation([])["status"] == "empty")

    # Regression: a `thisMonth` sample is 100% fresh and freshly-published, so its views are
    # a stopwatch, not a verdict. It used to be read as "concentrated — a new entrant must
    # out-execute them", which libelled an empty market as a crowded one.
    young = [{"views": v, "age_days": 3} for v in (2, 5, 9, 40)]
    ok("young sample is not called concentrated", "too young" in forensic.saturation(young)["reading"])
    settled = [{"views": v, "age_days": 400} for v in (1000, 2000, 3000, 90000)]
    ok("settled sample still reads concentration", "concentrated" in forensic.saturation(settled)["reading"])
    thin = [{"views": v, "age_days": 400} for v in (4, 8, 12, 30)]
    ok("low-volume settled sample reads thin, not concentrated", "thin volume" in forensic.saturation(thin)["reading"])


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


def t_order_vocabulary():
    """Both lanes must understand the same words for 'what is landing right now'."""
    ok("thisMonth maps to date order", client.normalise_order("thisMonth") == "date")
    ok("thisMonth sets a 30-day window", client.API_WINDOW_DAYS["thisMonth"] == 30)
    ok("thisWeek sets a 7-day window", client.API_WINDOW_DAYS["thisWeek"] == 7)
    ok("every keyless filter is accepted", all(o in client.API_ORDER for o in client.SP))
    try:
        client.normalise_order("lastQuarter")
        ok("nonsense is rejected", False)
    except ValueError:
        ok("nonsense is rejected", True)


def t_no_secret_escapes():
    """An error string is committed to public JSON — the key must never be inside it."""
    leaky = "gave up on https://www.googleapis.com/youtube/v3/channels?part=x&key=AIzaSECRET123"
    clean = http.scrub(leaky)
    ok("query key is redacted", "AIzaSECRET123" not in clean and "<redacted>" in clean)
    ok("other params survive", "part=x" in clean)
    ok("headers-style key is redacted too", "abc" not in http.scrub("x?access_token=abc"))
    ok("empty stays empty", http.scrub("") == "")


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


def t_comment_noise_floor():
    """One comment out of a hundred is not "the audience's objection"."""
    tiny = [{"text": "this did not work", "likes": 1}] + [{"text": "lol", "likes": 5}] * 99
    r = forensic.comment_mining(tiny)
    ok("1% is not a reading", "nothing cleared" in r["reading"])
    ok("...but the bucket still shows the raw count", r["objections"][0]["n"] == 1)
    real = [{"text": "please make a part 2", "likes": 2}] * 8 + [{"text": "nice", "likes": 1}] * 92
    ok("8% is a reading", "asking for more" in forensic.comment_mining(real)["reading"])


def t_go_needs_a_mechanism():
    """GO may not claim a readable mechanism while the mechanism part says otherwise."""
    sat = {"status": "ok", "top3_share": 0.44, "fresh_share_30d": 0.18,
           "winner_ratio": 3.5, "median_views": 113940}
    weak = {"status": "ok", "share": {"number_in_title": 0.0}}
    strong = {"status": "ok", "share": {"number_in_title": 0.5, "question": 0.4,
                                        "you_form": 0.4, "contrarian": 0.4}}
    a = decide.greenlight({"score": 83.9}, sat, weak, {"status": "ok", "strength": "firm"})
    b = decide.greenlight({"score": 83.9}, sat, strong, {"status": "ok", "strength": "firm"})
    ok("high score + no mechanism is not GO", a["verdict"] != "GO")
    ok("...and it says why", "cannot yet see how the winners are built" in a["reason"])
    ok("high score + clear mechanism is GO", b["verdict"] == "GO")
    ok("every verdict still carries a reason", all(x["reason"] for x in (a, b)))


def t_comment_refusal_speaks():
    """A refusal must say why on the card, and the miner must not pick a video that cannot
    clear the gate. The first sweep produced one card with an empty reading (a 6-comment
    video) and spent a quota unit to be told what the row count already said."""
    from . import forensic
    r = forensic.comment_mining([{"text": "nice", "likes": 1}] * 6)
    ok("a too-small sample is refused", r["status"] == "insufficient")
    ok("the refusal carries a reading, not an empty string", bool(r.get("reading")) and "6 comments" in r["reading"])


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
    for fn in [t_duration, t_lockup_states, t_age_vph, t_style_calibration, t_thumbprint_accent, t_hue_families_sum, t_saturation, t_order_vocabulary, t_no_secret_escapes, t_young_sample, t_title_signal_refuses, t_title_signal_recovers,
               t_funnel_gate, t_hook_parsing, t_demand_scoring, t_decide_access, t_decide_never_silent, t_comment_noise_floor, t_comment_refusal_speaks, t_go_needs_a_mechanism, t_comment_mining, t_reverse, t_ideas]:
        fn()
    print(f"\n{PASS} assertions passed")
    sys.exit(0)
