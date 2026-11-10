#!/usr/bin/env python3
"""Strict validation + idempotency proof for V12 Phase B + C packs.

Run from repo root:
    python research/multi_clip_long_form_v12/validate_phase_bc_v12.py

Calls NO API, downloads NO clip, records NO voice, renders NOTHING. Re-runs
the local generator once to prove byte-idempotency and cross-checks every
headline figure against the committed real-API evidence.
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
EV_A = D / "api_evidence" / "phase_a"
EV_BC = D / "api_evidence" / "phase_bc"
GEN = D / "build_phase_bc_v12.py"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"

FILES = [
    D / "PHASE_B_RIGHTS_GATE_V12.md", D / "phase_b_rights_gate_v12.json",
    D / "PHASE_C_SCRIPT_DRAFT_V12.md", D / "phase_c_script_draft_v12.json",
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


def words(t: str) -> list[str]:
    return re.findall(r"\b\w+\b", t)


def syllables(w: str) -> int:
    w = w.lower()
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


def grade(t: str) -> float:
    s = max(1, len(re.findall(r"[.!?]+", t)))
    ws = words(t)
    return round(0.39 * (len(ws) / s) + 11.8 * (sum(syllables(w) for w in ws) / len(ws)) - 15.59, 1)


def main() -> int:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(GEN)], cwd=ROOT,
                       capture_output=True, text=True)
    ok(r.returncode == 0, f"generator py_compile failed: {r.stderr}")
    for f in FILES:
        ok(f.exists(), f"missing file {f.relative_to(ROOT)}")
    if errors:
        print("RESULT: FAIL (files missing)")
        for e in errors:
            print(" -", e)
        return 1

    gate_md = (D / "PHASE_B_RIGHTS_GATE_V12.md").read_text(encoding="utf-8")
    script_md = (D / "PHASE_C_SCRIPT_DRAFT_V12.md").read_text(encoding="utf-8")
    gate = load(D / "phase_b_rights_gate_v12.json")
    script = load(D / "phase_c_script_draft_v12.json")
    na = NEXT_ACTION.read_text(encoding="utf-8")
    ledger = {s["n"]: s["url"] for s in load(D / "sources_v12.json")["sources"]}
    run_bc = load(EV_BC / "run.json")

    # --- 0. run receipt
    ok(run_bc["run_id"] == "42905149277", "BC run id mismatch")
    ok(run_bc["key_present"] is True and run_bc["secret_value_printed_or_stored"] is False,
       "BC secret flags wrong")
    ok(len(run_bc["angle_probes"]) == 3 and len(run_bc["reverse_targets"]) == 6, "BC run plan wrong")
    ok(len(run_bc["reports_produced"]) == 9, "BC reports produced not 9")

    # --- 1. citation integrity in both MDs
    for name, text in [("gate_md", gate_md), ("script_md", script_md)]:
        refs = [int(n) for n in re.findall(r"\[(\d+)\]\(", text)]
        ok(all(1 <= n <= len(ledger) for n in refs), f"{name}: out-of-ledger ref")
        bad = [n for n in set(refs) if f"[{n}]({ledger[n]})" not in text]
        ok(not bad, f"{name}: citation URL mismatch {bad}")
        ok("cite(" not in text, f"{name}: leaked literal cite( token")

    # --- 2. real angle probes cross-checked against committed reports
    angles = gate["phase_bc_real_evidence"]["angle_probes"]
    ok(len(angles) == 3, "angle probe count not 3")
    for a in angles:
        real = load(EV_BC / f"{a['slug']}.json")
        rows = real.get("rows") or []
        mv = [x for x in rows if isinstance(x.get("views"), int) and x["views"] >= 1_000_000]
        sat = real.get("saturation") or {}
        dec = real.get("decision") or {}
        ok(a["count"] == len(rows), f"{a['slug']}: count mismatch")
        ok(a["million_plus"] == len(mv), f"{a['slug']}: 1M+ mismatch")
        ok(a["median_views"] == sat.get("median_views"), f"{a['slug']}: median mismatch")
        ok(a["top3_share"] == sat.get("top3_share"), f"{a['slug']}: top3_share mismatch")
        ok(a["fresh_share_30d"] == sat.get("fresh_share_30d"), f"{a['slug']}: fresh_share mismatch")
        ok(a["verdict"] == dec.get("verdict") and a["score"] == dec.get("score"),
           f"{a['slug']}: verdict/score mismatch")
        ok(real.get("lane") == "api" and real.get("status") == "ok", f"{a['slug']}: not a real api ok report")
        real_ids = {x["id"] for x in rows}
        ok(all(x["id"] in real_ids for x in a["top_rows"]), f"{a['slug']}: invented top row id")
    ok(any(a["count"] == 1 for a in angles), "narrow 1-result query not present")
    ok("sirf 1 result" in gate_md, "1-result sampling caveat missing from gate MD")
    ok("artifact" in gate_md.lower(), "fresh_share artifact caveat missing")
    ok("Watch TWICE" in gate_md, "real watch-twice title signal missing")
    ok("1H5M35S" in gate_md or "1H5M" in gate_md, "long-form frame-by-frame precedent missing")

    # --- 3. real teardowns: 6, exactly one transcript OK, failures disclosed
    td = gate["phase_bc_real_evidence"]["winner_teardowns"]
    ok(len(td) == 6, f"teardown count not 6 (got {len(td)})")
    ok(sum(1 for x in td if x["transcript_status"] == "ok") == 1, "expected exactly one OK transcript")
    ok(all(isinstance(x["views"], int) and x["views"] > 0 for x in td), "a teardown receipt is not real")
    for x in td:
        real = load(EV_BC / x["file"])
        ok(real["receipt"]["views"] == x["views"], f"{x['file']}: view count mismatch")
        ok(real["transcript_status"]["status"] == x["transcript_status"],
           f"{x['file']}: transcript status mismatch")
    ok("5 transcripts nahi mile" in gate_md, "transcript failure count not disclosed")
    ok("bot check" in gate_md.lower() or "bot-check" in gate_md.lower(), "bot-check reason missing")
    ok("point-in-time" in gate_md.lower(), "point-in-time count caveat missing")
    rb = script["real_script_benchmark"]
    ok(rb is not None and rb["id"] == "k5s1cMNTmGs", "real script benchmark missing/wrong")
    if rb:
        real = load(EV_BC / "reverse-k5s1cMNTmGs.json")
        sc = real.get("script") or {}
        ok(rb["script_words"] == sc.get("words") and rb["wpm"] == sc.get("wpm"),
           "real script benchmark words/wpm mismatch")
        ok(rb["reading_grade"] == sc.get("reading_grade"), "real reading grade mismatch")
        ok(len(rb["structure"] or []) == 7, "real structure map not 7 beats")
        ok("200 wpm" in script_md and "8.1" in script_md, "real benchmark numbers missing from script MD")

    # --- 4. executable rights gate
    ok(gate["status"] == "ALL_8_DOSSIERS_PENDING_NO_CLIP_CLEARED", "gate status wrong")
    ok("NO clip enters the edit" in gate["hard_stop"], "hard stop missing")
    ok(gate["gate_enforcement"]["rejected"] is True and gate["gate_enforcement"]["expected_rejected"] is True,
       "gate enforcement test did not reject the fabricated cleared slot")
    ok(len(gate["field_rules"]) == 18 and len(gate["kill_conditions"]) == 8
       and len(gate["attribution_templates"]) == 5, "gate rule counts wrong")
    ok([x["field"] for x in gate["field_rules"]] == list(gate["dossiers"][0]["rights_gate"].keys()),
       "field rules != dossier fields")
    ok(len(gate["dossiers"]) == 8, "dossier count not 8")
    ok([d["slot"] for d in gate["dossiers"]] == list(range(1, 9)), "dossier slots not 1..8")
    for d in gate["dossiers"]:
        ok(d["clearance_status"] == "pending" and d["human_legal_review"] is False
           and d["not_a_legal_opinion"] is True, f"dossier {d['slot']}: not pending")
        ok(all(v is None for v in d["rights_gate"].values()), f"dossier {d['slot']}: a field is not NULL")
        ok(len(d["rights_gate"]) == 18, f"dossier {d['slot']}: field count not 18")
        ok(all(v is None for v in d["sign_off"].values()), f"dossier {d['slot']}: sign-off prefilled")
        ok(len(d["real_api_probe_targets"]) == 3, f"dossier {d['slot']}: probe targets not 3")
        ok("NOT cleared source clips" in d["probe_target_boundary"],
           f"dossier {d['slot']}: probe boundary missing")
        slug = {"1": "slot-01-07-expectation-violation", "2": "slot-02-03-physics-timing",
                "3": "slot-02-03-physics-timing", "4": "slot-04-scale-illusion",
                "5": "slot-05-06-08-sound-reaction-callback",
                "6": "slot-05-06-08-sound-reaction-callback",
                "7": "slot-01-07-expectation-violation",
                "8": "slot-05-06-08-sound-reaction-callback"}[str(d["slot"])]
        real = load(EV_A / (slug + ".json"))
        real_ids = {x["id"] for x in real["rows"]}
        ok(all(x["id"] in real_ids for x in d["real_api_probe_targets"]),
           f"dossier {d['slot']}: invented probe ID")
    ok("art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman" in str(gate["excluded_existing_short_clip"]),
       "V10/Short exclusion missing")
    ok("legal advice nahi" in gate_md, "not-a-legal-opinion disclaimer missing")
    ok("rejected=True" in gate_md or "rejected=true" in gate_md.lower(), "enforcement result missing from MD")

    # --- 5. full script draft
    ok(script["status"] == "DRAFT_NOT_FOR_RENDER_NOT_RECORDED", "script status wrong")
    ok(script["winner"] == "MC-01 THE REPLAY CODE: 8 Moments, One Hidden Rule", "winner changed")
    ok(script["runtime_seconds"] == 600 and script["chapters"] == 13, "runtime/chapters wrong")
    ch = script["chapter_ledger"]
    ok(len(ch) == 13 and [x["n"] for x in ch] == list(range(1, 14)), "chapter ledger wrong")
    ok(script["vo_words_budget"] == 1150, "VO budget not 1150")
    ok(900 <= script["vo_words_actual"] <= 1400, "draft word count out of range")
    ok(script["vo_words_actual"] == sum(x["vo_words_actual"] for x in ch), "word count sum mismatch")
    ok(120 <= script["vo_wpm_estimate"] <= 175, f"VO rate {script['vo_wpm_estimate']} wpm out of long-form range")
    ok(grade(" ".join(x["vo_text"] for x in ch)) == script["vo_reading_grade"],
       "reported reading grade does not match recomputation")
    ok(script["vo_reading_grade"] <= 9.0, "draft reading grade too dense for spoken word")
    ok(len(script["hooks"]) == 3, "hook variants not 3")
    ok(script["hooks"][0]["text"].startswith("Eight different clips"), "primary hook lost")
    ok(len(script["edit_decisions"]) == 7, "edit decisions not 7")
    for c in ch:
        ok(len(c["vo_text"]) > 80, f"chapter {c['n']}: VO text too short")
        ok(c["status"] == "DRAFT_NOT_RECORDED_NOT_RENDERED", f"chapter {c['n']}: status wrong")
    clip_chapters = [c for c in ch if 4 <= c["n"] <= 11]
    ok(len(clip_chapters) == 8, "clip chapters not 8")
    ok(all("SOURCE PENDING RIGHTS GATE" in c["vo_text"] and "SOURCE PENDING RIGHTS GATE" in c["shot_list"]
           for c in clip_chapters), "a clip chapter lacks the rights placeholder")
    all_vo = " ".join(c["vo_text"] for c in ch)
    real_ids_all = set()
    for p in list(EV_A.glob("*.json")) + list(EV_BC.glob("*.json")):
        try:
            d = load(p)
        except Exception:
            continue
        if isinstance(d.get("rows"), list):
            real_ids_all |= {x.get("id") for x in d["rows"] if isinstance(x, dict)}
        if isinstance(d.get("id"), str) and (d.get("receipt") or {}).get("views"):
            real_ids_all.add(d["id"])
    ok(not any(vid and vid in all_vo for vid in real_ids_all),
       "a real third-party video ID leaked into the VO as a source clip")
    ok("NO real clip" in script_md and "record nahi" in script_md, "placeholder rule missing from MD")
    ok("co-occurrence" in script_md, "causal-claim guard missing")
    ok("Poora 13-chapter script" in script_md, "full-script banner missing")

    # --- 6. metadata draft
    md = script["metadata_draft"]
    ok(md["status"] == "DRAFT_NOT_UPLOADED_NOT_PUBLISHED", "metadata status wrong")
    ok(md["category"]["human_must_confirm"] is True, "category human confirmation missing")
    ok(0 < len(md["hashtags"]) <= 3, "more than 3 displayed hashtags")
    ok(md["working_title_chars"] == len(md["working_title"]), "title char count mismatch")
    ok("DRAFT_NOT_UPLOADED" in script_md and "human_must_confirm" in script_md,
       "metadata draft disclaimers missing from MD")

    # --- 7. non-claims + banned positives
    ok(all(v is False for v in gate["non_claims"].values()), "gate non-claim is True")
    ok(all(v is False for v in script["non_claims"].values()), "script non-claim is True")
    ok(len(script["non_claims"]) == 19, f"script non-claim count not 19 (got {len(script['non_claims'])})")
    for text, name in [(gate_md.lower(), "gate_md"), (script_md.lower(), "script_md")]:
        for s in ["we verified the best growing channels", "million views guaranteed", "views are guaranteed",
                  "human legal review completed", "perfection achieved", "zero flaws confirmed",
                  "retention graph obtained", "we downloaded the competitor videos", "cleared for monetization",
                  "clip cleared for this episode", "nasa endorses this", "render complete",
                  "vo recorded", "uploaded successfully", "published successfully",
                  "transcript teardown succeeded for all"]:
            ok(s not in text, f"{name}: banned positive claim '{s}'")
    for s in ["no legal clearance", "no guaranteed views", "no human approval", "no render",
              "no upload", "no publish", "no monetization change"]:
        ok(s in gate_md.lower() or s in script_md.lower(), f"missing disclaimer: {s}")

    # --- 8. NEXT_ACTION markers exactly once + standing line
    for marker in ["## V12 addendum - MULTI-CLIP correction",
                   "## V12 PHASE A addendum - real API clip-moment scouting",
                   "## V12 PHASE B/C addendum - executable rights gate + VO script DRAFT"]:
        ok(na.count(marker) == 1, f"NEXT_ACTION marker count wrong: {marker}")
    ok("await human full-motion/native-audio review" in na, "standing review line lost")

    # --- 9. idempotency
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
    print(f"Phase B: 8 dossiers x 18 NULL fields, gate enforcement REJECTS fabricated clearance | "
          f"Phase C: {script['vo_words_actual']} words / 13 chapters / ~{script['vo_wpm_estimate']} wpm / "
          f"grade {script['vo_reading_grade']} | real transcript benchmark 1/6 | hard stop OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
