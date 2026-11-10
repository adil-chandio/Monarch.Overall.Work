#!/usr/bin/env python3
"""Strict validation + idempotency proof for the V12 multi-clip forensic pack.

Run from repo root:
    python research/multi_clip_long_form_v12/validate_multi_clip_forensic_v12.py

Prints RESULT: ALL PASS only if every check passes. Does NOT call any API,
does NOT render, upload, publish, download a clip, or change any setting.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "research" / "multi_clip_long_form_v12"
V11 = ROOT / "research" / "long_form_viral_idea_v11"
PHASEABC = ROOT / "production" / "monarch-cam" / "replay_lab_ep01_v11"
NEXT_ACTION = ROOT / "docs/continuity/channels/monarch-cam/NEXT_ACTION.md"
GEN = D / "build_multi_clip_forensic_v12.py"

FILES = [
    D / "MULTI_CLIP_VIRAL_IDEA_FORENSIC_STUDY_V12.md",
    D / "multi_clip_viral_idea_v12.json",
    D / "candidate_scoring_v12.json",
    D / "sources_v12.json",
    D / "api_capability_audit_v12.json",
    D / "clip_sourcing_gate_v12.json",
    V11 / "SUPERSEDED_BY_V12.md",
    PHASEABC / "SUPERSEDED_BY_V12.md",
    NEXT_ACTION,
]

errors: list[str] = []
checks = 0


def ok(cond: bool, label: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(label)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(name: str):
    return json.loads((D / name).read_text())


def main() -> int:
    # 0. syntax
    r = subprocess.run([sys.executable, "-m", "py_compile", str(GEN)], cwd=ROOT,
                       capture_output=True, text=True)
    ok(r.returncode == 0, f"generator py_compile failed: {r.stderr}")

    # 1. load
    for f in FILES:
        ok(f.exists(), f"missing file {f.relative_to(ROOT)}")
    if errors:
        print("RESULT: FAIL (files missing)")
        for e in errors:
            print(" -", e)
        return 1

    md = (D / "MULTI_CLIP_VIRAL_IDEA_FORENSIC_STUDY_V12.md").read_text()
    idea = load("multi_clip_viral_idea_v12.json")
    score = load("candidate_scoring_v12.json")
    src = load("sources_v12.json")
    api = load("api_capability_audit_v12.json")
    gate = load("clip_sourcing_gate_v12.json")
    raw_json = {f.name: f.read_text() for f in FILES if f.suffix == ".json"}

    # 2. ONE idea, multi-clip, 8-10 min
    ok(idea["status"] == "multi_clip_idea_selected_video_not_built", "status must be idea-selected-not-built")
    ok(idea["scoring_summary"]["winner"] == idea["chosen_idea"]["id"], "winner != chosen_idea id")
    ok(idea["chosen_idea"]["id"] == "MC-01", "chosen idea must be MC-01")
    ok(len([x for x in score["candidates"] if x["id"] == "MC-01"]) == 1, "MC-01 not unique")
    ok(not next(x for x in score["candidates"] if x["id"] == "MC-01")["kill_switches_hit"], "winner hit a kill switch")
    w = next(x for x in score["candidates"] if x["id"] == "MC-01")
    ok(w["weighted_total"] >= score["rubric"]["min_total"], "winner below min_total")
    ok(w["weighted_total"] <= score["rubric"]["max_score"], "winner above max_score")
    ok(480 <= idea["chosen_idea"]["runtime_target_seconds"] <= 600, "runtime not 8-10 min")
    ok("8-10 min" in idea["chosen_idea"]["format"], "format string missing 8-10 min")
    cc = idea["chosen_idea"]["clip_count_target"]
    ok(cc >= 8, "clip_count_target < 8")
    ok(len(idea["chosen_idea"]["clip_slots"]) == cc, "clip_slots count != clip_count_target")
    jobs = [x["analytic_job"] for x in idea["chosen_idea"]["clip_slots"]]
    ok(len(jobs) == len(set(jobs)), "clip analytic jobs not all distinct")
    ok(all(x["max_on_screen_seconds"] <= 10 for x in idea["chosen_idea"]["clip_slots"]), "a clip slot >10s")
    share = idea["chosen_idea"]["clip_share_max_seconds"] / idea["chosen_idea"]["runtime_target_seconds"]
    ok(share <= 0.1334, f"source share {share:.4f} > 13.34%")
    ok(len(idea["chosen_idea"]["chapters"]) == 13, "chapter ledger not 13")
    ok(len(idea["chosen_idea"]["hooks"]) == 3, "hook variants not 3")
    ok(len(idea["chosen_idea"]["production_phases_NOT_EXECUTED"]) == 7, "production phases not 7")
    ok(len(idea["10x_lenses"]) == 12, "microscope lenses not 12")
    ok(len(idea["open_gates"]) == 6, "open gates not 6")
    ok(all(g["status"] == "OPEN" for g in idea["open_gates"]), "an open gate is not OPEN")

    # 3. V11 single-clip direction is explicitly killed and superseded
    v11c = next(x for x in score["candidates"] if x["id"] == "MC-06")
    ok(any("single_clip_scope_violation" in k for k in v11c["kill_switches_hit"]), "V11 one-clip idea not disqualified")
    ok(any("single_clip_scope_violation" in k for k in idea["kill_switches"]), "kill switch missing from main idea JSON")
    ok(len(idea["kill_switches"]) == 16, "kill switches not 16")
    ok(len(score["rubric"]["kill_switches"]) == 16, "scoring kill switches not 16")
    for p, name in [(V11 / "SUPERSEDED_BY_V12.md", "V11 study"), (PHASEABC / "SUPERSEDED_BY_V12.md", "Phase A/B/C")]:
        t = p.read_text()
        ok("SUPERSEDED BY V12" in t and "not deleted" in t.lower(), f"{name} superseded marker invalid")
    na = NEXT_ACTION.read_text()
    ok(na.count("## V12 addendum - MULTI-CLIP correction") == 1, "NEXT_ACTION V12 addendum not exactly once")
    ok("single-clip V11 superseded" in na and "await human full-motion/native-audio review" in na,
       "NEXT_ACTION addendum lost standing review line")

    # 4. Source ledger + citation integrity
    ok(src["count"] == 60 and len(src["sources"]) == 60, "source count not 60")
    ok([x["n"] for x in src["sources"]] == list(range(1, 61)), "source n not sequential 1..60")
    ok(all(all(k in x for k in ("n", "id", "title", "url", "authority", "kind", "reliability", "used_for"))
           for x in src["sources"]), "a source lacks required fields")
    ok(sum(1 for x in src["sources"] if x["reliability"] == "third_party_directional_unverified") >= 10,
       "third-party directional sources missing")
    ok(sum(1 for x in src["sources"] if x["authority"].startswith("official")) >= 25,
       "official first-party sources missing")
    ledger = {x["n"]: x["url"] for x in src["sources"]}
    for text_name, text in [("MD", md)] + list(raw_json.items()):
        refs = [int(n) for n in re.findall(r"\[(\d+)\]\(", text)]
        ok(all(1 <= n <= 60 for n in refs), f"{text_name} has out-of-ledger ref")
        bad = [n for n in set(refs) if f"[{n}]({ledger[n]})" not in text]
        ok(not bad, f"{text_name} citation URL mismatch for refs {bad}")
        ok("cite(" not in text, f"{text_name} leaked a literal cite( token")
    ok(md.count("[1](") >= 1 and md.count("[60](") >= 1, "first/last source not cited in MD")

    # 5. API honesty
    ok(api["youtube_data_api_calls_made"] == 0, "API calls not 0")
    ok(api["api_key_in_workspace"] is False, "api_key_in_workspace not false")
    ok(api["workspace_check_results"]["api_key_value_ever_printed_or_stored"] is False, "key handling flagged true")
    ok(len(api["ready_to_run_queries_NOT_EXECUTED"]) == 4, "ready queries not 4")
    ok(all("key=REDACTED" in q and "REDACTED" in q for q in api["ready_to_run_queries_NOT_EXECUTED"]),
       "a ready query exposes a key")
    ok(any(x["method"] == "captions.download" and "own" in x["would_return"].lower()
           and "OAuth" in x["quota"] for x in api["official_capability"]),
       "captions ownership limit missing")
    ok(any("OWNER-ONLY" in x for x in api["hard_limits_even_with_key"]), "owner-only analytics limit missing")
    ok(api["research_actually_done"]["youtube_data_api_responses"] == 0, "research_actually_done API responses not 0")
    ok("NOT asserted" in api["research_actually_done"]["note"], "exact tool-call counts wrongly asserted")

    # 6. Clip sourcing gate: NOTHING acquired / cleared
    ok(gate["status"] == "NO_CLIP_ACQUIRED_NO_CLIP_CLEARED", "clip gate status wrong")
    ok(len(gate["slots"]) == 8, "clip gate slots not 8")
    ok(all(s["clearance_status"] == "pending" and s["sha256_after_download"] is None
           and s["official_source_url"] is None and s["human_legal_review"] is False
           and s["not_a_legal_opinion"] is True for s in gate["slots"]),
       "a clip slot is not fully pending/unsigned")
    ok(len(gate["banned_source_types"]) >= 5, "banned source types missing")
    ex = gate.get("excluded_existing_short_clip", {})
    ok("EXCLUDED" in ex.get("rule", "") and "all 8 slots" in ex.get("rule", ""),
       "excluded-existing-Short-clip rule missing")
    ok(any("V10/Short NASA water-bubble asset" in b for b in gate["banned_source_types"]),
       "Short clip not listed as a banned source type")
    ok("DIFFERENT assets only" in gate["candidate_lanes"][0], "NASA lane not restricted to different assets")

    # 7. Non-claims: every flag must be False
    for label, obj in [("idea", idea["non_claims"]), ("api", api["non_claims"]), ("gate", gate["non_claims"])]:
        ok(all(v is False for v in obj.values()), f"{label} non_claims contains a True")
    ok(len(idea["non_claims"]) == 29, "idea non-claims not 29")
    ok(idea["non_claims"]["v10_short_clip_reused_as_hero"] is False, "Short clip reuse flag not false")

    # 8. Banned positive claims must be ABSENT; honest disclaimers PRESENT
    forbidden_positive = [
        "we verified the best growing channels", "million views guaranteed", "views are guaranteed",
        "NASA endorses this", "NASA approved this video", "official NASA video", "human approved the video",
        "human legal review completed", "perfection achieved", "zero flaws confirmed",
        "retention graph obtained", "we downloaded the competitor videos", "cleared for monetization",
    ]
    low = md.lower()
    for s in forbidden_positive:
        ok(s.lower() not in low, f"banned positive claim present: {s}")
    required_disclaimers = [
        "0 live api calls", "koi clip download nahi", "0 clips acquired", "no render",
        "no upload", "no human approval", "no legal clearance", "no guaranteed views",
        "youtube data api key workspace me nahi hai", "best growing channels", "flawless",
        "excluded from all 8 slots", "29 non-claims",
    ]
    for s in required_disclaimers:
        ok(s in low, f"missing disclaimer: {s}")
    ok("MC-01" in md and "THE REPLAY CODE" in md, "winner not named in MD")
    ok("SUPERSEDED" in md, "V11 supersession not stated in MD")
    ok("15 research lanes" in md, "research lane count wrong in MD")
    ok("16 kill switches" in md and "60-source ledger" in md, "forensic counts wrong in MD")
    ok("RESULT: ALL PASS" not in md, "MD must not fake validator output")

    # 9. Idempotency: re-run generator, every byte must be identical
    before = {f: sha(f) for f in FILES}
    r = subprocess.run([sys.executable, str(GEN)], cwd=ROOT, capture_output=True, text=True)
    ok(r.returncode == 0, f"generator re-run failed: {r.stderr}")
    after = {f: sha(f) for f in FILES}
    for f in FILES:
        ok(before[f] == after[f], f"NON-IDEMPOTENT: {f.relative_to(ROOT)}")

    if errors:
        print(f"RESULT: FAIL ({len(errors)} of {checks} checks failed)")
        for e in errors:
            print(" -", e)
        return 1
    print(f"RESULT: ALL PASS ({checks} strict checks, idempotency verified)")
    print(f"Winner: MC-01 {w['weighted_total']}/100 | clips={cc} | runtime={idea['chosen_idea']['runtime_target_seconds']}s | sources={src['count']} | API calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
