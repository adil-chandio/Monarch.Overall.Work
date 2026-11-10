#!/usr/bin/env python3
"""Strict validation + idempotency proof for the V12 Phase A scout pack.

Run from repo root:
    python research/multi_clip_long_form_v12/validate_phase_a_scout_v12.py

Calls NO API, downloads NO clip, renders NOTHING. It re-runs the local
generator once to prove byte-idempotency, and cross-checks every headline
figure against the committed real-API reports.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "research" / "multi_clip_long_form_v12"
EV = D / "api_evidence" / "phase_a"
GEN = D / "build_phase_a_scout_v12.py"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"

FILES = [
    D / "PHASE_A_CLIP_SCOUT_V12.md",
    D / "phase_a_clip_scout_v12.json",
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


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(GEN)], cwd=ROOT,
                       capture_output=True, text=True)
    ok(r.returncode == 0, f"generator py_compile failed: {r.stderr}")

    for f in FILES:
        ok(f.exists(), f"missing file {f.relative_to(ROOT)}")
    for slug in ["slot-01-07-expectation-violation", "slot-02-03-physics-timing",
                 "slot-04-scale-illusion", "slot-05-06-08-sound-reaction-callback",
                 "rights-lane-nasa-agency-probe"]:
        ok((EV / f"{slug}.json").exists(), f"missing real API report {slug}")
    ok((EV / "run.json").exists(), "missing phase_a/run.json")
    if errors:
        print("RESULT: FAIL (files missing)")
        for e in errors:
            print(" -", e)
        return 1

    md = (D / "PHASE_A_CLIP_SCOUT_V12.md").read_text(encoding="utf-8")
    led = load(D / "phase_a_clip_scout_v12.json")
    na = NEXT_ACTION.read_text(encoding="utf-8")
    run = load(EV / "run.json")
    reports = {p.stem: load(p) for p in EV.glob("*.json") if p.name != "run.json"}

    # 1. run receipt
    ok(run["run_id"] == "42895703914", "run id mismatch")
    ok(run["phase"].startswith("A -"), "phase label wrong")
    ok(run["key_present"] is True, "key_present not true")
    ok(run["secret_value_printed_or_stored"] is False, "secret value flag wrong")
    ok(run["not_a_legal_opinion"] is True, "legal-opinion flag wrong")
    ok(len(run["queries"]) == 5 and len(run["reports_produced"]) == 5, "run query/report count not 5")
    ok("42895703914" in md and "42895703914" in na, "run id missing from docs")

    # 2. every headline figure is REAL (cross-checked against the API reports)
    ok(led["status"] == "SCOUT_CANDIDATES_FOUND_NO_CLIP_ACQUIRED_NO_CLIP_CLEARED", "status wrong")
    ok(len(led["api_evidence"]["reports"]) == 5, "ledger report summaries not 5")
    api_by_slug = {r["slug"]: r for r in led["api_evidence"]["reports"]}
    for slug, real in reports.items():
        s = api_by_slug[slug]
        rows = real.get("rows") or []
        mv = [x for x in rows if isinstance(x.get("views"), int) and x["views"] >= 1_000_000]
        sat = real.get("saturation") or {}
        dec = real.get("decision") or {}
        ok(s["count"] == len(rows), f"{slug}: count mismatch")
        ok(s["million_plus"] == len(mv), f"{slug}: 1M+ count mismatch")
        ok(s["top_views"] == max((x.get("views") or 0) for x in rows), f"{slug}: top_views mismatch")
        ok(s["total_views"] == sat.get("total_views"), f"{slug}: total_views mismatch")
        ok(s["median_views"] == sat.get("median_views"), f"{slug}: median_views mismatch")
        ok(s["top3_share"] == sat.get("top3_share"), f"{slug}: top3_share mismatch")
        ok(s["verdict"] == dec.get("verdict"), f"{slug}: verdict mismatch")
        ok(s["score"] == dec.get("score"), f"{slug}: score mismatch")
        ok(real.get("lane") == "api" and real.get("status") == "ok", f"{slug}: not a real api ok report")
        ok(all(x["verdict"] == "NO" for x in [dec]), f"{slug}: verdict not honestly NO")

    # 3. the MD must carry the actual real numbers, not invented ones
    ok("363,151,838" in md, "real top view count missing from MD")
    ok("20/20" in md, "NASA 20/20 1M+ finding missing")
    ok("19,234,336" in md, "NASA median views missing")
    ok("0.398" in md, "NASA top3_share missing")
    ok("weak" in md.lower(), "weak r2 warning missing")
    ok("sampling artifact" in md.lower(), "fresh_share sampling-artifact warning missing")

    # 4. 8 slots, all distinct, all pending, all benchmarks labelled
    slots = led["slots"]
    ok(len(slots) == 8, "slot count not 8")
    ok([s["slot"] for s in slots] == list(range(1, 9)), "slot numbers not 1..8")
    jobs = [s["analytic_job"] for s in slots]
    ok(len(jobs) == len(set(jobs)), "analytic jobs not distinct")
    ok(all(s["max_on_screen_seconds"] == 10 for s in slots), "a slot >10s on screen")
    ok(sum(s["vo_word_budget"] for s in slots) == 130 + 135 + 120 + 120 + 105 + 95 + 85 + 75,
       "per-slot VO budgets wrong")
    for s in slots:
        ok(len(s["real_benchmark_candidates"]) == 3, f"slot {s['slot']}: benchmark count not 3")
        ok(all(isinstance(b["views"], int) and b["views"] > 0 and b["id"] for b in s["real_benchmark_candidates"]),
           f"slot {s['slot']}: benchmark is not a real video")
        ok("STRUCTURAL BENCHMARKS ONLY" in s["benchmark_boundary"], f"slot {s['slot']}: boundary missing")
        ok(s["clearance_status"] == "pending" and s["human_legal_review"] is False
           and s["clip_downloaded"] is False and s["clip_cleared"] is False
           and s["sha256_after_download"] is None and s["not_a_legal_opinion"] is True,
           f"slot {s['slot']}: not fully pending")
        ok(all(v is None for v in s["rights_gate"].values()),
           f"slot {s['slot']}: a rights field is not null")
        ok(len(s["rights_gate"]) == 18, f"slot {s['slot']}: rights field count not 18")
        ok(s["scout_query"]["report"].startswith("api_evidence/phase_a/"),
           f"slot {s['slot']}: scout query path wrong")
        # benchmark IDs must actually exist in the referenced report
        ref = load(EV / (s["scout_query"]["report"].split("/")[-1]))
        real_ids = {x["id"] for x in ref["rows"]}
        ok(all(b["id"] in real_ids for b in s["real_benchmark_candidates"]),
           f"slot {s['slot']}: benchmark ID invented")
        ok("DIFFERENT assets only" in " ".join(s["candidate_source_lanes"]),
           f"slot {s['slot']}: different-assets lane missing")

    # 5. V10/Short exclusion + agency probe exclusions
    ex = led["excluded_existing_short_clip"]
    ok("EXCLUDED" in ex["rule"] and "all 8 slots" in ex["rule"], "V10/Short exclusion rule missing")
    ok(ex["nasa_asset_id"] == "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman", "excluded asset id wrong")
    ag = led["agency_rights_lane_probe"]
    ok(len(ag) == 10, f"agency rows not 10 (got {len(ag)})")
    ok(all(isinstance(x["views"], int) and x["id"] for x in ag), "an agency row is not real")
    ok(any(x["status"] == "EXCLUDED_PENDING_HUMAN_LEGAL_REVIEW" for x in ag),
       "current-crew Artemis II rows not excluded")
    ok(any(x["status"] == "REJECT_FOR_NOW" and "Wringing out Water" in x["title"] for x in ag),
       "CSA water-bubble same-physics-family rejection missing")
    ok("REJECT FOR NOW" in md and "EXCLUDED" in md, "agency exclusions missing from MD")

    # 6. production blueprint is SPEC ONLY
    ok(len(led["chapter_ledger"]) == 13, "chapter ledger not 13")
    ok(led["vo_total_word_budget"] == sum(c["vo_words"] for c in led["chapter_ledger"]), "VO budget sum wrong")
    ok(led["vo_total_word_budget"] == 1150, "VO budget not 1150")
    ok(led["edit_spec_NOT_EXECUTED"]["status"] == "SPEC_ONLY_NOT_RENDERED", "edit spec status wrong")
    ok(led["edit_spec_NOT_EXECUTED"]["runtime_seconds"] == 600, "runtime spec wrong")
    ok(led["edit_spec_NOT_EXECUTED"]["source_footage_max_seconds"] == 80, "source footage cap wrong")
    ok(led["edit_spec_NOT_EXECUTED"]["source_share_max_pct"] == 13.3, "source share cap wrong")
    ok("final VO script nahi" in md, "final-script disclaimer missing")
    ok("SPEC ONLY" in md, "spec-only banner missing")

    # 7. winner unchanged / hard stop / open gates
    ok(led["winner_unchanged"]["id"] == "MC-01" and led["winner_unchanged"]["clip_count"] == 8,
       "winner changed")
    ok("NO clip enters the edit" in led["hard_stop"], "hard stop missing")
    ok("human_legal_review=true" in led["hard_stop"], "hard stop lacks human legal review")
    ok("NO clip enters the edit" in md, "hard stop missing from MD")
    ok(len(led["open_gates"]) == 6, "open gates not 6")

    # 8. non-claims all False; banned positives absent from MD
    ok(all(v is False for v in led["non_claims"].values()), "a non-claim is True")
    ok(len(led["non_claims"]) == 22, f"non-claim count not 22 (got {len(led['non_claims'])})")
    low = md.lower()
    for s in ["we verified the best growing channels", "million views guaranteed", "views are guaranteed",
              "human legal review completed", "perfection achieved", "zero flaws confirmed",
              "retention graph obtained", "we downloaded the competitor videos", "cleared for monetization",
              "clip cleared for this episode", "nasa endorses this", "final vo script is ready",
              "render complete", "transcript teardown succeeded"]:
        ok(s not in low, f"banned positive claim present: {s}")
    for s in ["koi clip download/clear nahi hua", "hard stop", "human legal review",
              "structural benchmarks", "sampling artifact", "not a source clip",
              "pending", "no legal clearance", "no guaranteed views"]:
        ok(s.lower() in low or s in md, f"missing disclaimer: {s}")

    # 9. NEXT_ACTION addendum exactly once, standing line preserved
    ok(na.count("## V12 PHASE A addendum - real API clip-moment scouting") == 1,
       "Phase A addendum not exactly once")
    ok("await human full-motion/native-audio review" in na, "standing review line lost")
    ok("## V12 addendum - MULTI-CLIP correction" in na, "V12 addendum lost")

    # 10. idempotency
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
    print(f"Phase A: run 42895703914 | 5 real reports | {sum(s['count'] for s in api_by_slug.values())} rows | "
          f"8 scouted slots | 10 agency probes | 0 clips acquired | hard stop OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
