#!/usr/bin/env python3
"""V12 render PLANNER - refuses to render while the rights gate is open.

This script NEVER invokes ffmpeg and NEVER writes an MP4. It only:
  * checks all 8 Phase B dossiers, and
  * prints a deterministic assembly plan.

    python render_pipeline_v12.py --check-gate   # default: BLOCKED while pending
    python render_pipeline_v12.py --dry-run      # same check, then the plan if cleared
    python render_pipeline_v12.py --self-test    # proves a forged clearance is rejected

A dossier may be 'cleared' ONLY with human_legal_review=true, a named
reviewer + date + decision, and zero NULL rights fields.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "phase_b_rights_gate_v12.json"
EDL = HERE / "phase_d_production_kit_v12.json"


def problems(d: dict) -> list[str]:
    out = []
    for dossier in d["dossiers"]:
        n = dossier["slot"]
        if dossier.get("clearance_status") != "cleared":
            out.append(f"slot {n}: clearance_status={dossier.get('clearance_status')} (needs 'cleared')")
        if dossier.get("human_legal_review") is not True:
            out.append(f"slot {n}: human_legal_review is not true")
        nulls = [k for k, v in dossier.get("rights_gate", {}).items() if v is None]
        if nulls:
            out.append(f"slot {n}: {len(nulls)} NULL rights fields")
        so = dossier.get("sign_off") or {}
        missing = [k for k in ("reviewer_name", "review_date", "decision") if not so.get(k)]
        if missing:
            out.append(f"slot {n}: sign_off missing {', '.join(missing)}")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check-gate", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()

    gate = json.loads(GATE.read_text(encoding="utf-8"))
    kit = json.loads(EDL.read_text(encoding="utf-8"))

    if a.self_test:
        forged = {"dossiers": [{"slot": 99, "clearance_status": "cleared",
                               "human_legal_review": False,
                               "rights_gate": {r["field"]: None for r in gate["field_rules"]},
                               "sign_off": {}}]}
        bad = problems(forged)
        print("SELF-TEST: forged 'cleared' dossier rejected =", bool(bad))
        print("SELF-TEST: reasons =", len(bad))
        return 0 if bad else 1

    issues = problems(gate)
    if issues:
        print("BLOCKED - render NOT permitted. Reasons:")
        for i in issues[:24]:
            print("  -", i)
        print(f"... {len(issues)} total. NO MP4, NO VO, NO upload was attempted.")
        return 2

    print("Gate clear. Deterministic plan (PLAN ONLY - this script still does not render):")
    print(f"  canvas   : {kit['render_spec']['canvas']}")
    print(f"  frames   : {kit['render_spec']['total_frames']} @ {kit['render_spec']['fps']}fps")
    print(f"  chapters : {len(kit['edl'])}")
    print("  ffmpeg   : WOULD be invoked by a separate, human-approved render job.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
