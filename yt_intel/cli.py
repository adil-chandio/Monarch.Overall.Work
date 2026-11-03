"""yt-intel CLI.

Every command prints JSON on `--json` and a human report otherwise. The human report is
the one that matters: it is written in the order a decision is actually made.

  python -m yt_intel demand "ai video editing"
  python -m yt_intel topic  "ai video editing" --limit 30 --json out.json
  python -m yt_intel channel @mkbhd
  python -m yt_intel reverse dQw4w9WgXcQ
  python -m yt_intel ideas  "ai video editing"
  python -m yt_intel lanes
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from . import client, decide, demand as demand_mod, forensic, ideas as ideas_mod, reverse


def thumbprint():
    """Imported lazily: it needs numpy + pillow, and the demand/forensic path does not.

    A topic report must keep working on a machine where only the standard library is
    installed — the image forensics is the optional part, not the price of entry.
    """
    from . import thumbprint as tp
    return tp


def _p(obj):
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def _bar(v, width=18):
    if v is None:
        return "—"
    n = int(round(max(0, min(100, v)) / 100 * width))
    return "█" * n + "·" * (width - n)


# ------------------------------------------------------------------ commands
def cmd_lanes(args):
    info = {
        "lane": client.lane(),
        "api_key_present": bool(client.API_KEY),
        "quota_remaining": client.BUDGET.remaining,
        "quota_calls": client.BUDGET.state.get("calls", {}),
        "cache_dir": client.http.CACHE_DIR,
        "notes": [],
    }
    if not client.API_KEY:
        info["notes"].append(
            "no YOUTUBE_API_KEY: running keyless (autocomplete + RSS + public pages + transcripts). "
            "Add a free key for exact view counts and 50-item search pages."
        )
    if args.json:
        return _p(info)
    print(f"lane            {info['lane']}")
    print(f"api key         {'yes' if info['api_key_present'] else 'no (keyless mode)'}")
    print(f"quota remaining {info['quota_remaining']} / {client.BUDGET.DAILY}")
    for n in info["notes"]:
        print(f"note            {n}")


def cmd_doctor(args):
    """Prove the key works before it is trusted with a research run.

    Order matters: the cheapest possible call first (channels.list, 1 unit), then a
    single search (100 units) only if the first one passed. A key that is valid but has
    the API disabled returns 403 accessNotConfigured, which looks like a bad key — this
    separates the two.
    """
    checks = []
    quiet = getattr(args, "json_only", False)  # machine-readable mode: stdout carries JSON only

    def say(line=""):
        if not quiet:
            print(line)

    def rec(name, ok, detail=""):
        checks.append({"check": name, "ok": ok, "detail": detail})
        mark = "PASS" if ok else "FAIL"
        say(f"  {mark}  {name}" + (f" — {detail}" if detail else ""))

    key = client.API_KEY
    if not key:
        say("\nDOCTOR\n  FAIL  no YOUTUBE_API_KEY in the environment")
        say("  → see docs/setup/YOUTUBE-API-KEY.md (5 minutes, free, no card)")
        if args.json or quiet:
            _p({"checks": [{"check": "key present", "ok": False,
                            "detail": "no YOUTUBE_API_KEY in the environment"}],
                "quota_used": client.BUDGET.state["used"]})
        return 1
    rec("key present", True, f"{key[:6]}…{key[-4:]} ({len(key)} chars)")
    # shape is a hint, not a gate: the only real proof is a successful call
    shape_ok = key.startswith("AIza")
    rec("key shape looks right", True,
        f"starts with {key[:4]}…{'' if shape_ok else ' (expected AIza — check you copied the whole key)'}")

    try:
        data = client._api("channels", {"part": "snippet,statistics", "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw"}, "channels")
        n = len(data.get("items", []))
        rec("channels.list", n > 0, f"{n} channel returned (1 quota unit)")
    except Exception as e:  # noqa: BLE001
        msg = str(e)[:200]
        if "accessNotConfigured" in msg:
            rec("channels.list", False, "API not enabled on this project — enable YouTube Data API v3")
        elif "API_KEY_INVALID" in msg or "400" in msg:
            rec("channels.list", False, "key rejected — check for a stray space or a deleted key")
        else:
            rec("channels.list", False, msg)
        say("\n  Quota spent so far: " + str(client.BUDGET.state["used"]))
        return 1

    try:
        # This used to touch `client.demand`, which does not exist — so this check failed
        # unconditionally with "module has no attribute 'demand'" even on a perfectly good key.
        c = client.search("api test", limit=1)
        rec("search.list", c.status == "ok",
            f"lane={c.lane} status={c.status} items={len(c.items)} (100 quota units)")
    except Exception as e:  # noqa: BLE001
        rec("search.list", False, str(e)[:160])

    say(f"\n  quota used today : {client.BUDGET.state['used']} / {client.BUDGET.DAILY} units")
    say(f"  searches left    : {client.BUDGET.remaining // 100}")
    say("  next             : python -m yt_intel topic \"your topic\" --limit 30")
    if args.json or quiet:
        _p({"checks": checks, "quota_used": client.BUDGET.state["used"],
            "quota_remaining": client.BUDGET.remaining})
    return 0 if all(c["ok"] for c in checks) else 1


def cmd_demand(args):
    d = demand_mod.analyse(args.topic, deep=args.deep, with_trends=not args.no_trends)
    data = d.to_dict()
    data["verdict"] = demand_mod.verdict(d.score, d.confidence)
    if args.json:
        return _p(data)
    print(f"\nDEMAND · {d.topic}")
    print(f"  score        {(f'{d.score:.1f}' if d.score is not None else '—'):>6}   {_bar(d.score)}   confidence {d.confidence}")
    if d.score is None:
        print("  NOTE         an absent signal is not a zero. See the notes below before reading this as 'no demand'.")
    print(f"  verdict      {data['verdict']}")
    for k, v in d.parts.items():
        print(f"  {k:<12} {v if v is not None else '—'}")
    if d.position:
        print(f"  suggestion   rank #{d.position} for the exact phrase")
    if d.spread:
        print(f"  spread       {d.spread} distinct sub-intents")
    if d.intent:
        print(f"  intent       {', '.join(d.intent[:5])}")
    if d.trends.get("status") == "ok":
        for q, s in d.trends["series"].items():
            print(f"  trends       {q}: mean {s['mean']} · {s['direction']} ({s['slope_per_week']:+.2f}/wk)")
    print("\n  top suggestions")
    for s in d.suggestions[:12]:
        print(f"    · {s}")
    for n in d.notes:
        print(f"  note: {n}")


def _decorate(row: dict) -> dict:
    """Add the derived columns every downstream measurement reads.

    One function, called from every command that scores rows, so a new command cannot
    quietly skip the age normalisation and report a different number for the same video.
    """
    row["age_days"] = forensic.parse_age_days(row.get("published", ""))
    row["vph"] = forensic.vph(row.get("views"), row["age_days"])
    row["duration_s"] = forensic.parse_duration(row.get("duration", ""))
    return row


def cmd_topic(args):
    corpus = client.search(args.topic, limit=args.limit, order=args.order)
    rows = [dict(r) for r in corpus.items]
    for r in rows:
        _decorate(r)
    sat = forensic.saturation(rows)
    t_sig = forensic.title_signal(rows)
    words = forensic.word_signal(rows)
    fun = forensic.funnel(rows)
    psych = forensic.psych_profile(rows)
    dem = None
    if not args.no_demand:
        dem = demand_mod.analyse(args.topic, deep=False, with_trends=not args.no_trends)
    verdict = decide.greenlight(
        dem.to_dict() if dem else {}, sat, fun, t_sig,
        trends=(dem.trends if dem else None),
        access={"status": corpus.status, "detail": corpus.detail},
    )
    out = {
        # Everything in the report is downstream of this one fetch. Without a timestamp the
        # index cannot order reports by recency, and a report looks timeless when it is stale.
        "fetched_at": int(time.time()),
        "topic": args.topic, "lane": corpus.lane, "order": args.order, "status": corpus.status,
        "detail": corpus.detail, "count": len(rows),
        "rows": rows, "saturation": sat, "title_signal": t_sig,
        "word_signal": words, "funnel": fun, "psych": psych,
        "demand": dem.to_dict() if dem else None,
        "decision": verdict,
    }
    if args.json:
        with open(args.json, "w") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.json} ({len(rows)} rows)")
        return
    print(f"\nTOPIC · {args.topic}   [{corpus.lane} lane · {corpus.status}]")
    if corpus.detail:
        print(f"  detail: {corpus.detail}")
    if sat.get("status") == "ok":
        print(f"\n  SATURATION  {sat['videos']} videos · median {sat['median_views']:,} views")
        print(f"    top-3 share {sat['top3_share']:.0%} · winner ratio {sat['winner_ratio']}x · fresh 30d {sat['fresh_share_30d']}")
        print(f"    {sat['reading']}")
    if t_sig.get("status") == "ok":
        print(f"\n  TITLE MATH  n={t_sig['n']} ({t_sig['strength']}) · {t_sig['read']}")
        print(f"    {t_sig['caveat']}")
    elif t_sig.get("status") == "insufficient":
        print(f"\n  TITLE MATH  skipped — {t_sig['detail']}")
    if words.get("status") == "ok":
        print("\n  WINNING WORDS  " + ", ".join(f"{w['word']}({w['lift']}x)" for w in words["winners"][:8]))
    if fun.get("status") == "ok":
        print("\n  HOOK PATTERNS IN THE TOP QUARTILE")
        for k, v in sorted(fun["share"].items(), key=lambda kv: -kv[1]):
            print(f"    {k:<18} {v:>5.0%}")
    if psych.get("status") == "ok":
        for d in psych["drivers"][:5]:
            print(f"    → {d['driver']:<20} {d['mechanism']}")
    print("\n  TOP VIDEOS")
    for r in sorted(rows, key=lambda r: -(r.get("views") or 0))[:10]:
        print(f"    {(r.get('views') or 0):>10,}  {r.get('vph') or 0:>9} v/h  {r.get('title','')[:70]}")
    print("\n  DECISION")
    print(f"    {verdict['verdict']}  {verdict['score']}  ({verdict['reason']})")
    for f_ in verdict["strongest_for"][:4]:
        print(f"      + {f_}")
    for a in verdict["strongest_against"][:4]:
        print(f"      - {a}")
    if verdict["missing"]:
        print(f"      ? missing: {', '.join(verdict['missing'])}")
    print(f"      → next probe: {verdict['next_probe']}")


def cmd_comments(args):
    """Mine the comment field of one video: asks, objections, asset wants."""
    c = client.comments(args.video, limit=args.limit, order=args.order)
    mined = forensic.comment_mining(c.items)
    # When the lane cannot fetch at all, mining an empty list would report "insufficient
    # sample" — a measurement problem — instead of "no access", which is the real one.
    out = {"video": args.video, "status": c.status, "detail": c.detail, "lane": c.lane,
           **({"status": c.status, "detail": c.detail} if c.status != "ok" else {}),
           **(mined if c.status == "ok" else {"mining": "skipped — nothing was fetched",
                                               "caveat": "no comment data; this is an access result"})}
    if args.json:
        with open(args.json, "w") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.json} ({mined.get('n', 0)} comments)")
        return
    print(f"\nCOMMENTS · {args.video}   [{c.lane} lane · {c.status}]")
    if c.detail:
        print(f"  detail: {c.detail}")
    if c.status != "ok":
        print("  not a comment pattern — nothing was fetched; fix access and re-run")
        return
    if mined.get("status") != "ok":
        print(f"  {mined.get('status')}: {mined.get('detail')}")
        return
    print(f"  {mined['n']} comments · {mined['reading']}")
    for bucket in ("asks", "objections", "wants"):
        for h in mined[bucket][:4]:
            print(f"    {bucket:<11} {h['share']:>5.0%}  {h['label']}")
    print("\n  most-liked")
    for c_ in mined["top_liked"][:3]:
        print(f"    {c_['likes']:>5}♥  {c_['text'][:110]}")
    print(f"\n  caveat: {mined['caveat']}")


def cmd_channel(args):
    c = client.channel(args.channel)
    if c.status != "ok":
        return _p({"status": c.status, "detail": c.detail})
    ids = [i["id"] for i in c.items]
    print(f"\nCHANNEL · {args.channel}  ({len(ids)} recent uploads)")
    try:
        fps = thumbprint().channel_fingerprint(ids)
    except ImportError as e:
        fps = {"status": "unavailable", "detail": f"numpy/pillow not installed: {e}"}
        print(f"  thumbnails   skipped ({fps['detail']})")
    if fps.get("status") == "ok":
        print(f"  thumbnails   face-led rate {fps['face_rate']:.0%} · {fps['reading']}")
        print(f"  colour       {fps['top_hexes']}")
        print(f"  contrast     {fps['avg_contrast']} · busy {fps['avg_busy']}")
    for i in c.items[:10]:
        print(f"    {i['published'][:10]}  {i['title'][:70]}")
    if args.json:
        _p({"channel": c.to_dict(), "thumbprint": fps})


def cmd_reverse(args):
    t = reverse.teardown(args.video, fetch_transcript=not args.no_transcript)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(t, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.json}")
        return
    r = t.get("receipt", {})
    print(f"\nREVERSE · {r.get('title') or t['id']}")
    print(f"  views {r.get('views')} · age {r.get('age_days')}d · {r.get('vph')} views/hour · {t.get('duration_seconds')}s")
    print(f"  transcript: {t.get('transcript_status')}")
    s = t.get("script")
    if s:
        print("\n  SCRIPT")
        print(f"    {s['reading']}")
        print(f"    CTAs {s['cta_count']} · numbers/100w {s['numbers_per_100w']} · filler {s['filler_rate']:.1%}")
        print(f"    first 30 words: {s['first_30_words']}")
    h = t.get("hook")
    if h:
        print("\n  HOOK")
        print(f"    {h['first_3s_words']}")
        print(f"    claim type: {h['claim_type']}")
    st = t.get("structure")
    if st:
        print("\n  STRUCTURE")
        for part in st:
            print(f"    {part['at']:>6}  {part['title']}")
    p = t.get("psychology", {})
    for d in p.get("drivers", []):
        print(f"    → {d['driver']}: {d['effect']}")
    rep = t.get("replication", {})
    print("\n  REPLICATION")
    for k in ("keep", "change", "beat"):
        for v in rep.get(k, []):
            print(f"    {k:<6} {v}")


def cmd_style(args):
    """Production-style forensics on a local file (our own cut, or a reference clip)."""
    from . import style as style_mod
    res = style_mod.analyse(args.file)
    if res.get("status") != "ok":
        return _p(res)
    if args.compare:
        other = style_mod.analyse(args.compare)
        res["compare"] = style_mod.compare(res, other)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(res, f, indent=2)
        print(f"wrote {args.json}")
        return
    print(f"\nPRODUCTION STYLE · {res['path']}  ({res['duration_s']}s)")
    print(f"  cuts            {res['cuts']}  ({res['cuts_per_minute']}/min)")
    agr = res.get("cut_agreement") or {}
    if agr.get("second_only") or agr.get("primary_only"):
        print(f"  second opinion  {res.get('adaptive_cuts')} cuts — {agr.get('verdict')}")
    print(f"  hook cuts 0-3s  {res['hook_cuts_first_3s']}")
    print(f"  shot length     median {res['shot_median_s']}s · p10 {res['shot_p10_s']} · p90 {res['shot_p90_s']} · longest {res['longest_shot_s']}")
    print(f"  motion          mean {res['motion_mean']} · peak {res['motion_peak']} · quiet {res['motion_quiet_share']:.0%}")
    print(f"  look            saturation {res['saturation_mean']} · contrast {res['contrast_mean']}")
    print(f"  lower-third     edge density mean {res['overlay_density_mean']} · peak {res['overlay_density_peak']}")
    print(f"  pacing          {res['pacing_verdict']}")
    if res.get("compare"):
        print("\n  VS REFERENCE")
        for k, v in res["compare"].items():
            print(f"    {k:<22} ours {v['ours']:<8} theirs {v['theirs']:<8} ratio {v['ratio']}")


def cmd_ideas(args):
    dem = demand_mod.analyse(args.topic, deep=False, with_trends=False)
    out = ideas_mod.generate(args.topic, dem.to_dict(), limit=args.limit, **{k: v for k, v in {
        "n_big": args.n, "days": args.days}.items()})
    if args.json:
        return _p({"topic": args.topic, "ideas": out, "wtf_bank": ideas_mod.wtf_bank(args.topic)})
    print(f"\nIDEAS · {args.topic}\n")
    for i in out:
        print(f"  {i['rank']:>2}. [{i['family']}/{i['structure']}] {i['idea']}")
        print(f"      why: {i['why_it_works']}")
        print(f"      risk: {i['risk']}\n")
    print("  WTF BANK")
    for w in ideas_mod.wtf_bank(args.topic):
        print(f"    · {w}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="yt-intel", description="YouTube intelligence, $0, keyless-first")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("lanes", help="which access lane is active and how much quota is left")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_lanes)

    s = sub.add_parser("doctor", help="prove the API key works before trusting it")
    s.add_argument("--json", action="store_true")
    s.add_argument("--json-only", action="store_true",
                   help="stdout is ONLY the JSON object — for CI files, never for humans")
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser("demand", help="is anyone actually asking for this?")
    s.add_argument("topic")
    s.add_argument("--deep", action="store_true", help="alphabet expansion (slower, richer)")
    s.add_argument("--no-trends", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_demand)

    s = sub.add_parser("topic", help="saturation + title math + hook patterns + verdict")
    s.add_argument("topic")
    s.add_argument("--limit", type=int, default=30)
    s.add_argument("--order", default="relevance", choices=sorted(client.SP))
    s.add_argument("--no-demand", action="store_true")
    s.add_argument("--no-trends", action="store_true")
    s.add_argument("--json", help="write the full report to this path")
    s.set_defaults(fn=cmd_topic)

    s = sub.add_parser("comments", help="comment mining: what the audience asked for and objected to")
    s.add_argument("video", help="video id")
    s.add_argument("--limit", type=int, default=100)
    s.add_argument("--order", default="relevance", choices=["relevance", "time"])
    s.add_argument("--json")
    s.set_defaults(fn=cmd_comments)

    s = sub.add_parser("channel", help="channel roster + thumbnail fingerprint")
    s.add_argument("channel", help="@handle or UC… id")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_channel)

    s = sub.add_parser("reverse", help="teardown a video that already won")
    s.add_argument("video")
    s.add_argument("--no-transcript", action="store_true")
    s.add_argument("--json")
    s.set_defaults(fn=cmd_reverse)

    s = sub.add_parser("style", help="production-style forensics: cuts, pacing, look (local file)")
    s.add_argument("file")
    s.add_argument("--compare", help="a second file to diff against (e.g. a reference clip)")
    s.add_argument("--json")
    s.set_defaults(fn=cmd_style)

    s = sub.add_parser("ideas", help="trend + evergreen curiosity idea families")
    s.add_argument("topic")
    s.add_argument("--limit", type=int, default=12)
    s.add_argument("--n", type=int, default=7)
    s.add_argument("--days", type=int, default=30)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_ideas)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
