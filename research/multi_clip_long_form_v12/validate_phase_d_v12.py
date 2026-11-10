#!/usr/bin/env python3
"""Strict validation + idempotency proof for the V12 Phase D production kit.

Run from repo root:
    python research/multi_clip_long_form_v12/validate_phase_d_v12.py

Calls NO API, downloads NO clip, records NO voice, renders NO MP4. Re-runs
the local generator once to prove byte-idempotency, and actually EXECUTES the
render planner to prove it blocks while the rights gate is open.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "research" / "multi_clip_long_form_v12"
ASSETS = D / "assets_v12"
GEN = D / "build_phase_d_production_kit_v12.py"
PIPELINE = D / "render_pipeline_v12.py"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"

FILES = [
    D / "PHASE_D_PRODUCTION_KIT_V12.md", D / "phase_d_production_kit_v12.json",
    D / "ONE_PAGE_REVIEWER_CHECKLIST_V12.md", D / "index.html",
    D / "render_pipeline_v12.py", NEXT_ACTION,
] + [ASSETS / f"diagram_{i:02d}.svg" for i in range(1, 11)]

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
    r = subprocess.run([sys.executable, "-m", "py_compile", str(GEN), str(PIPELINE)], cwd=ROOT,
                       capture_output=True, text=True)
    ok(r.returncode == 0, f"py_compile failed: {r.stderr}")
    for f in FILES:
        ok(f.exists(), f"missing file {f.relative_to(ROOT)}")
    if errors:
        print("RESULT: FAIL (files missing)")
        for e in errors:
            print(" -", e)
        return 1

    kit = load(D / "phase_d_production_kit_v12.json")
    md = (D / "PHASE_D_PRODUCTION_KIT_V12.md").read_text(encoding="utf-8")
    checklist = (D / "ONE_PAGE_REVIEWER_CHECKLIST_V12.md").read_text(encoding="utf-8")
    html_txt = (D / "index.html").read_text(encoding="utf-8")
    na = NEXT_ACTION.read_text(encoding="utf-8")
    gate = load(D / "phase_b_rights_gate_v12.json")
    FOOTER = "ORIGINAL DIAGRAM - Monarch Cam - no endorsement implied - no third-party asset"

    # --- 1. status + non-claims
    ok(kit["status"] == "ASSETS_AND_PLANS_ONLY_NOT_RENDERED", "kit status wrong")
    ok(all(v is False for v in kit["non_claims"].values()), "a non-claim is True")
    ok(len(kit["non_claims"]) == 18, f"non-claim count not 18 (got {len(kit['non_claims'])})")
    ok("NO clip enters the edit" in kit["hard_stop"], "hard stop missing")
    ok("art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman" in str(kit["excluded_existing_short_clip"]),
       "V10/Short exclusion missing")

    # --- 2. original SVGs: valid XML, own shapes only, no external content
    svgs = kit["original_assets"]
    ok(len(svgs) == 10, f"asset count not 10 (got {len(svgs)})")
    ok([s["slot"] for s in svgs[:8]] == list(range(1, 9)), "first 8 diagrams not mapped to slots 1..8")
    for s in svgs:
        p = D / s["file"]
        raw = p.read_text(encoding="utf-8")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            ok(False, f"{s['file']}: invalid XML: {e}")
            continue
        ok(root.tag.endswith("svg"), f"{s['file']}: root is not svg")
        ok(root.attrib.get("width") == "1920" and root.attrib.get("height") == "1080",
           f"{s['file']}: wrong canvas")
        ok(root.attrib.get("data-license") == "own_work", f"{s['file']}: licence marker missing")
        ok(FOOTER in raw, f"{s['file']}: footer missing")
        ok("<image" not in raw and "href=" not in raw and "xlink" not in raw,
           f"{s['file']}: embedded/external image reference found")
        ok("http" not in raw.replace("http://www.w3.org/2000/svg", ""),
           f"{s['file']}: unexpected external URL")
        titles = [e.text for e in root.iter() if e.tag.endswith("title")]
        descs = [e.text for e in root.iter() if e.tag.endswith("desc")]
        ok(bool(titles) and bool(descs), f"{s['file']}: title/desc missing")
        ok(f'"{s["file"]}"' in html_txt, f"{s['file']}: missing from index.html")
    ok(html_txt.count("<figure>") == 10, "index.html figure count not 10")
    ok("NO CLIP CLEARED" in html_txt and "NO RENDER" in html_txt, "index.html status banner missing")

    # --- 3. EDL frame maths
    edl = kit["edl"]
    spec = kit["render_spec"]
    ok(len(edl) == 13, "EDL chapters not 13")
    ok(spec["fps"] == 30 and spec["runtime_seconds"] == 600 and spec["total_frames"] == 18000,
       "render spec wrong")
    ok([e["chapter"] for e in edl] == list(range(1, 14)), "EDL chapter numbers wrong")
    ok(edl[0]["start_frame"] == 0 and edl[-1]["end_frame_exclusive"] == 18000,
       "EDL does not span 0..18000")
    ok(all(edl[i]["end_frame_exclusive"] == edl[i + 1]["start_frame"] for i in range(12)),
       "EDL has a frame gap or overlap")
    ok(sum(e["duration_frames"] for e in edl) == 18000, "EDL frame durations do not sum to 18000")
    ok(all(e["status"] == "PLAN_ONLY_NOT_RENDERED" for e in edl), "an EDL row claims render")
    ok(all(e["clip_in_frame"] is None and e["clip_out_frame"] is None
           and e["clip_media_path"] is None and e["clip_sha256"] is None for e in edl),
       "an EDL row has a real clip path/in-out")
    clip_rows = [e for e in edl if e["clip_slot"]]
    ok(len(clip_rows) == 8 and [e["clip_slot"] for e in clip_rows] == list(range(1, 9)),
       "clip slots not 1..8")
    ok(all(e["original_diagram_asset"] for e in clip_rows), "a clip chapter has no diagram asset")
    ok(sum(e["vo_words"] for e in edl) == 1238, "EDL VO word total mismatch with script draft")
    ok("18,000" in md and "18000" in str(kit), "frame count not stated in MD")

    # --- 4. QC / A-B / captions
    qc = kit["qc_checklist"]
    ok(len(qc) == 20, f"QC items not 20 (got {len(qc)})")
    ok(all(q["status"] == "not_run" for q in qc), "a QC item claims it ran")
    ok(any("nine_gate_audio" in q["check"] for q in qc), "V10 nine-gate audio item missing")
    ok(any("v10_short_asset_absent" in q["check"] for q in qc), "Short-exclusion QC item missing")
    ab = kit["ab_test_plan"]
    ok(ab["status"] == "NOT_RUN", "A/B plan claims it ran")
    ok(len(ab["hook_variants"]) == 3 and len(ab["title_variants"]) == 3
       and len(ab["thumbnail_concepts"]) == 3, "A/B variant counts wrong")
    ok("CONTRADICT" in ab["honest_caveat"], "A/B contradictory-signal caveat missing")
    caps = kit["captions_skeleton"]
    ok(len(caps) == 13 and all(c["text"] is None for c in caps), "captions skeleton wrong")
    ok(all(c["timing_status"] == "WORD_LEVEL_TIMING_PENDING_AFTER_ACTUAL_VO_RECORDING" for c in caps),
       "captions timing wrongly claimed")
    ok(not list(D.glob("*.srt")), "an SRT file was created (must not be)")
    ok(not list(D.glob("*.mp4")), "an MP4 file was created (must not be)")

    # --- 5. render planner ACTUALLY blocks
    p_text = PIPELINE.read_text(encoding="utf-8")
    ok("NEVER invokes ffmpeg" in p_text and "subprocess" not in p_text,
       "render planner might invoke an external process")
    r1 = subprocess.run([sys.executable, str(PIPELINE), "--check-gate"], cwd=ROOT,
                        capture_output=True, text=True)
    ok(r1.returncode == 2, f"render planner did not BLOCK (exit {r1.returncode})")
    ok("BLOCKED" in r1.stdout and "NO MP4" in r1.stdout, "render planner block message missing")
    r2 = subprocess.run([sys.executable, str(PIPELINE), "--self-test"], cwd=ROOT,
                        capture_output=True, text=True)
    ok(r2.returncode == 0 and "rejected = True" in r2.stdout, "render planner self-test failed")
    r3 = subprocess.run([sys.executable, str(PIPELINE), "--dry-run"], cwd=ROOT,
                        capture_output=True, text=True)
    ok(r3.returncode == 2 and "BLOCKED" in r3.stdout, "dry-run bypassed the gate")
    ok(len(gate["dossiers"]) == 8 and all(d["clearance_status"] == "pending" for d in gate["dossiers"]),
       "gate dossiers no longer pending")

    # --- 6. one-page checklist
    fields = [r["field"] for r in gate["field_rules"]]
    ok(len(fields) == 18, "gate field rules not 18")
    ok(all(f in checklist for f in fields), "a rights field missing from one-page checklist")
    ok(checklist.count("☐") >= 26, "checklist has too few fillable boxes")
    ok("APPROVE | REJECT | REVISE" in checklist, "checklist decision block missing")
    ok("not_a_legal_opinion : true" in checklist, "legal-opinion disclaimer missing")
    ok("EXCLUDED" in checklist, "V10/Short exclusion missing from checklist")
    ok("Agent ye fields khud" in checklist, "human-only note missing")
    for k in gate["kill_conditions"]:
        ok(k.replace("|", "or") in checklist, f"kill condition missing from checklist: {k[:40]}")
    ok("ONE_PAGE_REVIEWER_CHECKLIST_V12.md" in md, "kit MD does not point at the one-pager")

    # --- 7. banned positives / required disclaimers
    low = (md + checklist + html_txt).lower()
    for s in ["we verified the best growing channels", "million views guaranteed", "views are guaranteed",
              "human legal review completed", "perfection achieved", "zero flaws confirmed",
              "retention graph obtained", "we downloaded the competitor videos", "cleared for monetization",
              "clip cleared for this episode", "nasa endorses this", "render complete",
              "vo recorded successfully", "uploaded successfully", "published successfully"]:
        ok(s not in low, f"banned positive claim: {s}")
    for s in ["no legal clearance", "no guaranteed views", "no human approval", "no render",
              "no upload", "no publish", "no monetization change", "spec target"]:
        ok(s in low, f"missing disclaimer: {s}")
    ok("RESULT: ALL PASS" not in md, "MD must not fake validator output")

    # --- 8. NEXT_ACTION markers
    for marker in ["## V12 addendum - MULTI-CLIP correction",
                   "## V12 PHASE A addendum - real API clip-moment scouting",
                   "## V12 PHASE B/C addendum - executable rights gate + VO script DRAFT",
                   "## V12 PHASE D addendum - original artwork, EDL, QC kit, render gate"]:
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
    print(f"Phase D: 10 original SVGs | 13-chapter EDL 0..18000 frames | 20 QC items not_run | "
          f"A/B 3x3x3 not_run | render planner BLOCKS (exit 2) | hard stop OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
