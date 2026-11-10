#!/usr/bin/env python3
"""V12 PHASE D - production kit that needs NO cleared clips.

Everything here is ORIGINAL (our own SVG diagrams, our own timeline maths,
our own checklists) or a PLAN. No third-party clip is downloaded, embedded or
named as a source. No VO is recorded, no MP4 is rendered, nothing is uploaded.

Deterministic / idempotent. Produces:
  * assets_v12/diagram_01.svg .. diagram_10.svg   (original artwork)
  * index.html                                    (visual preview of all artwork)
  * PHASE_D_PRODUCTION_KIT_V12.md + .json         (EDL, QC, A/B, captions, spec)
  * ONE_PAGE_REVIEWER_CHECKLIST_V12.md            (the human's one-pager)
  * render_pipeline_v12.py                        (REFUSES to render while gate is open)
  * a Phase D addendum in NEXT_ACTION.md
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "research" / "multi_clip_long_form_v12"
ASSETS = D / "assets_v12"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"
ADDENDUM_MARKER = "## V12 PHASE D addendum - original artwork, EDL, QC kit, render gate"

EDITION = "v12_phase_d_production_kit"
FPS = 30
RUNTIME = 600
TOTAL_FRAMES = FPS * RUNTIME
W, H = 1920, 1080
FOOTER = "ORIGINAL DIAGRAM - Monarch Cam - no endorsement implied - no third-party asset"
NASA_ID_EXCLUDED = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"

# ---------------------------------------------------------------------------
# Small SVG toolbox (all shapes are ours; no images, no external refs)
# ---------------------------------------------------------------------------
def esc(t: str) -> str:
    return html.escape(str(t), quote=True)


def txt(x, y, s, size=30, fill="#e8eef7", anchor="start", weight="400", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{extra}>{esc(s)}</text>')


def box(x, y, w, h, fill="#131c2b", stroke="#2c3f5c", sw=2, rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def line(x1, y1, x2, y2, stroke="#5bd6d0", sw=4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def dot(x, y, r=9, fill="#ffc06a"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


def svg_shell(title: str, subtitle: str, body: str, accent: str = "#5bd6d0") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d" data-origin="original_made_for_v12" data-license="own_work">\n'
        f'  <title id="t">{esc(title)}</title>\n'
        f'  <desc id="d">{esc(subtitle)}</desc>\n'
        f'  {box(0, 0, W, H, fill="#0a101a", stroke="none", sw=0, rx=0)}\n'
        f'  <rect x="0" y="0" width="{W}" height="10" fill="{accent}"/>\n'
        f'  {txt(80, 96, title, 52, "#f4f8ff", weight="700")}\n'
        f'  {txt(80, 146, subtitle, 26, "#9fb2cc")}\n'
        f'  {line(80, 178, W - 80, 178, "#24344c", 2)}\n'
        f'  {body}\n'
        f'  {line(80, 990, W - 80, 990, "#24344c", 2)}\n'
        f'  {txt(80, 1034, FOOTER, 22, "#7f92ad")}\n'
        '</svg>\n'
    )


def panel(x, y, w, h, label, accent="#5bd6d0"):
    return box(x, y, w, h) + txt(x + 28, y + 52, label, 30, accent, weight="700")


DIAGRAMS: list[dict] = []


def add(slug, slot, chapter, title, subtitle, body, accent="#5bd6d0"):
    DIAGRAMS.append({"slug": slug, "slot": slot, "chapter": chapter, "title": title,
                     "subtitle": subtitle, "body": body, "accent": accent,
                     "file": f"assets_v12/{slug}.svg"})


# 01 - expected vs actual
_b = (panel(90, 230, 840, 620, "EXPECTED", "#9fb2cc") +
      panel(990, 230, 840, 620, "ACTUAL", "#ffc06a") +
      line(160, 700, 860, 700, "#3a4d69", 3) +
      line(160, 700, 500, 420, "#9fb2cc", 5) + line(500, 420, 860, 420, "#9fb2cc", 5) +
      line(1060, 700, 1760, 700, "#3a4d69", 3) +
      line(1060, 700, 1330, 420, "#ffc06a", 5) + line(1330, 420, 1330, 300, "#ffc06a", 5) +
      line(1330, 300, 1760, 300, "#ffc06a", 5) +
      dot(1330, 420, 14, "#ff6b6b") +
      txt(1355, 400, "violation frame", 24, "#ff9c9c") +
      txt(160, 790, "prediction", 26, "#9fb2cc") + txt(1060, 790, "measured", 26, "#ffc06a"))
add("diagram_01", 1, "1:40-2:55", "Expected vs Actual", "Slot 1 - the exact frame where a prediction stops working", _b)

# 02 - ray / force
_b = (panel(90, 230, 1740, 620, "MECHANISM (original ray / force schematic)") +
      '<ellipse cx="960" cy="540" rx="150" ry="230" fill="none" stroke="#5bd6d0" stroke-width="5"/>' +
      txt(960, 552, "medium", 28, "#5bd6d0", "middle") +
      line(160, 380, 810, 470, "#9fb2cc", 4) + line(810, 470, 1420, 470, "#5bd6d0", 4) +
      line(160, 540, 810, 540, "#9fb2cc", 4) + line(1110, 540, 1760, 540, "#5bd6d0", 4) +
      line(160, 700, 810, 610, "#9fb2cc", 4) + line(810, 610, 1420, 470, "#5bd6d0", 4) +
      dot(1420, 470, 14, "#ffc06a") + txt(1450, 445, "where the reason appears", 24, "#ffc06a") +
      txt(120, 800, "FACT: verify against a FIRST-PARTY official source for this clip before recording", 24, "#ff9c9c"))
add("diagram_02", 2, "2:55-4:05", "The Late Explanation", "Slot 2 - eyes register the event; the reason needs a sentence", _b, "#ffc06a")

# 03 - three speed bands
_b = panel(90, 230, 1740, 620, "SAME FOOTAGE - THREE LABELLED PASSES")
for i, (label, n, col) in enumerate([("1x  full speed", 8, "#9fb2cc"),
                                     ("0.5x  half speed", 16, "#5bd6d0"),
                                     ("0.25x  quarter speed", 32, "#ffc06a")]):
    y = 320 + i * 165
    _b += txt(130, y, label, 30, col, weight="700")
    for k in range(n):
        x = 620 + k * (1200 // n)
        _b += box(x, y - 38, max(6, 1200 // n - 6), 54,
                  fill=("#ff6b6b" if (i == 2 and k == n // 2) else "#17243a"),
                  stroke=col, sw=1, rx=3)
    if i == 2:
        _b += txt(620 + (n // 2) * (1200 // n) + 4, y + 48, "the frame that carries the surprise", 22, "#ff9c9c")
_b += txt(130, 810, "Slowing down does not create the rewatch impulse - it reveals where it was hiding.", 26, "#9fb2cc")
add("diagram_03", 3, "4:05-5:10", "Three Speed Passes", "Slot 3 - 1x / 0.5x / 0.25x, same frames", _b)

# 04 - scale
_b = (panel(90, 230, 1740, 620, "SCALE NEEDS A KNOWN REFERENCE") +
      box(220, 420, 220, 300, fill="#17243a") + txt(330, 780, "unknown", 26, "#9fb2cc", "middle") +
      box(560, 500, 90, 220, fill="#5bd6d0") + txt(605, 780, "reference", 26, "#5bd6d0", "middle") +
      line(560, 760, 650, 760, "#ffc06a", 4) + txt(605, 810, "1 unit", 24, "#ffc06a", "middle") +
      box(1000, 340, 420, 380, fill="#17243a", stroke="#ffc06a") +
      txt(1210, 560, "same object", 30, "#ffc06a", "middle") +
      txt(1210, 610, "two readings", 26, "#9fb2cc", "middle") +
      txt(1000, 790, "Remove or mislead the reference and the prediction breaks.", 26, "#9fb2cc"))
add("diagram_04", 4, "5:10-6:15", "Scale Error", "Slot 4 - an original scale diagram with a labelled reference", _b, "#ffc06a")

# 05 - A/B audio
_b = panel(90, 230, 1740, 620, "PASS A  vs  PASS B  (same frames)")
for i, (label, col) in enumerate([("A - native audio", "#5bd6d0"), ("B - muted + commentary", "#ffc06a")]):
    y = 350 + i * 250
    _b += txt(130, y, label, 30, col, weight="700")
    for k in range(40):
        x = 620 + k * 29
        if i == 0:
            hh = 18 + (k * 37 % 95)
        else:
            hh = 12 if k % 3 else 46
        _b += box(x, y + 60 - hh // 2, 18, hh, fill=col, stroke="none", sw=0, rx=2)
_b += txt(130, 810, "No music or SFX substitution: the comparison is only valid with the real audio.", 26, "#9fb2cc")
add("diagram_05", 5, "6:15-7:10", "Sound vs Silence", "Slot 5 - drawn A/B beat diagram, not sampled audio", _b)

# 06 - attention reset
_b = (panel(90, 230, 1740, 620, "ATTENTION RESET TIMELINE") +
      line(160, 700, 1760, 700, "#3a4d69", 3) +
      line(160, 700, 620, 700, "#9fb2cc", 5) + line(620, 700, 620, 330, "#ff6b6b", 6) +
      line(620, 330, 900, 470, "#ffc06a", 5) + line(900, 470, 1760, 470, "#5bd6d0", 5) +
      dot(620, 330, 14, "#ff6b6b") + txt(650, 315, "reaction beat", 26, "#ff9c9c") +
      txt(160, 790, "prediction", 26, "#9fb2cc") + txt(1300, 440, "explanation resumes", 26, "#5bd6d0") +
      txt(130, 830, "No person named, no endorsement implied, no face crop reused as thumbnail.", 24, "#7f92ad"))
add("diagram_06", 6, "7:10-8:00", "The Reaction Beat", "Slot 6 - a reaction delays closure by one beat", _b, "#ffc06a")

# 07 - converging
_b = (panel(90, 230, 1740, 620, "TWO INDEPENDENT TRACKS, ONE FRAME") +
      line(160, 380, 1000, 380, "#5bd6d0", 5) + line(1000, 380, 1300, 540, "#5bd6d0", 5) +
      line(160, 700, 1000, 700, "#ffc06a", 5) + line(1000, 700, 1300, 540, "#ffc06a", 5) +
      dot(1300, 540, 18, "#ff6b6b") + txt(1330, 520, "verification frame", 26, "#ff9c9c") +
      txt(160, 340, "track 1", 24, "#5bd6d0") + txt(160, 680, "track 2", 24, "#ffc06a") +
      txt(130, 810, "No invented date, injury, outcome or quote. Rewatch = a verification loop.", 26, "#9fb2cc"))
add("diagram_07", 7, "8:00-8:45", "The Near-Miss", "Slot 7 - converging timeline, sourced facts only", _b)

# 08 - callback grid
_b = panel(90, 230, 1740, 620, "EIGHT DIFFERENT CLIPS - ONE RULE")
for i in range(8):
    col, row = i % 4, i // 4
    x, y = 140 + col * 430, 300 + row * 250
    fill = "#2a3d24" if i == 7 else "#17243a"
    stroke = "#ffc06a" if i == 7 else "#2c3f5c"
    _b += box(x, y, 380, 200, fill=fill, stroke=stroke, sw=3)
    _b += txt(x + 190, y + 90, f"SLOT {i+1}", 34,
              "#ffc06a" if i == 7 else "#e8eef7", "middle", "700")
    _b += txt(x + 190, y + 140, "PREDICT" if i == 7 else "proved", 24,
              "#ffc06a" if i == 7 else "#9fb2cc", "middle")
_b += txt(130, 810, "Play slot 8 with NO explanation. Ask the viewer to predict the replay point.", 26, "#9fb2cc")
add("diagram_08", 8, "8:45-9:25", "The Prediction Test", "Slot 8 - callback grid, one cell per DIFFERENT clip", _b, "#ffc06a")

# 09 - six-step rule
_b = panel(90, 230, 1740, 620, "THE RULE, RESTATED")
steps = ["1  PREDICTION", "2  VIOLATION", "3  SHORT DELAY", "4  REPAIR", "5  REPLAY", "6  SHARE"]
for i, s in enumerate(steps):
    col, row = i % 3, i // 3
    x, y = 140 + col * 580, 300 + row * 250
    _b += box(x, y, 530, 180, fill="#17243a", stroke="#5bd6d0", sw=3)
    _b += txt(x + 265, y + 108, s, 34, "#e8eef7", "middle", "700")
_b += txt(130, 810, "Honest limits: public counts only; no private analytics, no human review, no clearance.", 26, "#ff9c9c")
add("diagram_09", None, "9:25-9:50", "The Six-Step Rule", "Chapter 12 - the rule and its limits on one screen", _b)

# 10 - cold-open montage
_b = panel(90, 230, 1740, 620, "COLD OPEN - 8 DIFFERENT MOMENTS, 0.8-1.2s EACH")
for i in range(8):
    col, row = i % 4, i // 4
    x, y = 140 + col * 430, 300 + row * 250
    _b += box(x, y, 380, 200, fill="#17243a", stroke="#5bd6d0", sw=2)
    _b += txt(x + 190, y + 95, f"CLIP {i+1}", 32, "#e8eef7", "middle", "700")
    _b += txt(x + 190, y + 145, f"{0.8 + i*0.05:.2f}s", 24, "#9fb2cc", "middle")
_b += txt(130, 810, "No logo, no greeting, native audio only - then the one-line hook.", 26, "#9fb2cc")
add("diagram_10", None, "0:00-0:20", "Cold-Open Montage", "Chapter 1 - eight distinct clips, no reused Short asset", _b)


# ---------------------------------------------------------------------------
# EDL / QC / A-B / captions (all deterministic, all PLAN)
# ---------------------------------------------------------------------------
def tc(t: str) -> int:
    m, s = t.split(":")
    return (int(m) * 60 + int(s)) * FPS


def build_edl() -> list[dict]:
    script = json.loads((D / "phase_c_script_draft_v12.json").read_text(encoding="utf-8"))
    out = []
    for c in script["chapter_ledger"]:
        a, b = c["t"].split("-")
        sf, ef = tc(a), tc(b)
        slot = c["n"] - 3 if 4 <= c["n"] <= 11 else None
        asset = next((x["file"] for x in DIAGRAMS if x["slot"] == slot), None) if slot else \
            next((x["file"] for x in DIAGRAMS if x["chapter"] == c["t"]), None)
        out.append({
            "chapter": c["n"], "timecode": c["t"], "name": c["name"],
            "start_frame": sf, "end_frame_exclusive": ef, "duration_frames": ef - sf,
            "duration_seconds": round((ef - sf) / FPS, 2),
            "vo_words": c["vo_words_actual"], "shot_list": c["shot_list"],
            "clip_slot": slot, "clip_in_frame": None, "clip_out_frame": None,
            "clip_media_path": None, "clip_sha256": None,
            "original_diagram_asset": asset,
            "replay_passes": ["1x", "0.5x", "0.25x"] if slot == 3 else (["1x", "0.5x"] if slot == 2 else []),
            "native_audio": "PENDING_RIGHTS_GATE" if slot else "n/a",
            "status": "PLAN_ONLY_NOT_RENDERED",
        })
    return out


QC_TARGETS = [
    {"check": "duration_600s", "target": "600.000s", "source": "V12 runtime spec", "status": "not_run"},
    {"check": "frames_18000", "target": "18000 frames @ 30fps", "source": "frame maths", "status": "not_run"},
    {"check": "landscape_1920x1080", "target": "1920x1080", "source": "V12 format (V10 was vertical 1080x1920)", "status": "not_run"},
    {"check": "fps_30", "target": "30/1", "source": "V10 technical_checks", "status": "not_run"},
    {"check": "audio_48k_stereo", "target": "48000 Hz, 2 ch", "source": "V10 technical_checks", "status": "not_run"},
    {"check": "integrated_loudness", "target": "-14 LUFS (spec target copied from V10 QC: -14.60 LUFS measured there)", "source": "V10 technical_checks", "status": "not_run"},
    {"check": "true_peak", "target": "within V10 chain limit", "source": "V10 technical_checks", "status": "not_run"},
    {"check": "no_sample_clipping_runs", "target": "0 runs", "source": "V10 technical_checks", "status": "not_run"},
    {"check": "no_click_runs", "target": "0 runs", "source": "V10 technical_checks", "status": "not_run"},
    {"check": "nine_gate_audio", "target": "V10's 9/9 gate list (items not enumerated here)", "source": "V10 short_35 qc_summary.json", "status": "not_run"},
    {"check": "source_share_max_13_3pct", "target": "<=80s of source / 600s", "source": "V12 hard guardrail", "status": "not_run"},
    {"check": "each_clip_max_10s", "target": "8 slots, each <=300 frames", "source": "V12 hard guardrail", "status": "not_run"},
    {"check": "eight_distinct_clips", "target": "8 different asset IDs / hashes", "source": "user correction", "status": "not_run"},
    {"check": "v10_short_asset_absent", "target": NASA_ID_EXCLUDED + " not present", "source": "user correction", "status": "not_run"},
    {"check": "no_insignia_current_crew", "target": "0 frames", "source": "NASA promotional gate", "status": "not_run"},
    {"check": "native_audio_retained", "target": "no music/SFX substitution", "source": "V12 edit decisions", "status": "not_run"},
    {"check": "original_diagrams_only", "target": "10 own SVG assets", "source": "this kit", "status": "not_run"},
    {"check": "ai_use_disclosure", "target": "present if synthetic/altered media used", "source": "official help", "status": "not_run"},
    {"check": "human_full_motion_native_audio_review", "target": "completed by a human", "source": "standing continuity line", "status": "not_run"},
    {"check": "human_creative_approval", "target": "completed by a human", "source": "standing continuity line", "status": "not_run"},
]


def build_ab() -> dict:
    script = json.loads((D / "phase_c_script_draft_v12.json").read_text(encoding="utf-8"))
    md = script["metadata_draft"]
    return {
        "status": "NOT_RUN",
        "studio_feature": "Test & Compare supports up to 3 titles + 3 thumbnails; use it, do not guess",
        "hook_variants": [h["id"] + ": " + h["text"] for h in script["hooks"]],
        "title_variants": [md["working_title"]] + md["alt_titles"],
        "thumbnail_concepts": [
            "eight numbered cells, one highlighted - matches the callback grid",
            "single freeze frame with a drawn violation marker",
            "plain text rule card, no face, no logo",
        ],
        "honest_caveat": "Number-in-title signals CONTRADICT across the real Phase A samples (-65% to +389%, one with r2=0.093). A/B is a test, not a proven winner.",
        "no_claim": "No CTR, retention, views or revenue outcome is predicted.",
    }


def build_captions(edl) -> list[dict]:
    return [{"chapter": e["chapter"], "timecode": e["timecode"],
             "start_frame": e["start_frame"], "end_frame_exclusive": e["end_frame_exclusive"],
             "vo_word_count": e["vo_words"],
             "timing_status": "WORD_LEVEL_TIMING_PENDING_AFTER_ACTUAL_VO_RECORDING",
             "text": None, "status": "SKELETON_ONLY_NOT_AN_SRT"} for e in edl]


RENDER_PIPELINE = '''#!/usr/bin/env python3
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
'''


def build_kit(edl) -> dict:
    return {
        "edition": EDITION, "phase": "D - production kit that needs NO cleared clips",
        "status": "ASSETS_AND_PLANS_ONLY_NOT_RENDERED",
        "render_spec": {"canvas": "1920x1080 landscape", "fps": FPS,
                        "runtime_seconds": RUNTIME, "total_frames": TOTAL_FRAMES,
                        "video_codec": "H.264", "audio_codec": "AAC 48kHz stereo",
                        "loudness_target": "-14 LUFS (spec target, NOT a V12 measurement)",
                        "source_footage_max_seconds": 80, "source_share_max_pct": 13.3},
        "original_assets": DIAGRAMS,
        "edl": edl,
        "qc_checklist": QC_TARGETS,
        "ab_test_plan": build_ab(),
        "captions_skeleton": build_captions(edl),
        "render_pipeline": {"file": "render_pipeline_v12.py",
                            "mode": "PLANNER_ONLY_NEVER_INVOKES_FFMPEG",
                            "gate_check": "reads phase_b_rights_gate_v12.json; exits 2 while any dossier is pending",
                            "self_test": "forged cleared dossier is rejected"},
        "excluded_existing_short_clip": NASA_ID_EXCLUDED,
        "hard_stop": "NO clip enters the edit until every rights field is verified and human_legal_review=true for that clip.",
        "non_claims": {
            "clip_downloaded": False, "clip_cleared": False, "vo_recorded": False,
            "render_done": False, "mp4_created": False, "captions_file_created": False,
            "thumbnail_created": False, "ab_test_run": False, "qc_run": False,
            "upload_done": False, "publish_done": False, "monetization_changed": False,
            "human_legal_review": False, "human_creative_approval": False,
            "legal_clearance": False, "guaranteed_views": False,
            "perfection": False, "nasa_endorsement": False,
        },
    }


def table(headers, rows) -> list[str]:
    e = lambda s: str(s).replace("|", "or").replace("\n", " ")
    return (["| " + " | ".join(e(h) for h in headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"] +
            ["| " + " | ".join(e(c) for c in r) + " |" for r in rows])


def build_kit_md(kit: dict) -> str:
    m = []
    a = m.append
    a("# V12 PHASE D - Production Kit (original artwork + executable plans)")
    a("")
    a("> **Aage ka kaam jo gate ke bina bhi ho sakta tha, kar diya.** 10 **asli original SVG "
      "diagrams** (hamare apne shapes/text, koi teesre-party image nahi), frame-accurate **EDL "
      "(18,000 frames)**, 20-item QC checklist, A/B plan, captions skeleton, aur ek **render "
      "planner jo gate khula hone par chal hi nahi sakta**. Koi clip, VO, MP4, upload nahi.")
    a("")
    a(f"**Edition:** `{EDITION}` · **Status:** `{kit['status']}` · "
      f"**Canvas:** `{kit['render_spec']['canvas']}` · **Frames:** `{TOTAL_FRAMES}` @ {FPS}fps")
    a("**Machine-readable:** `phase_d_production_kit_v12.json`, `render_pipeline_v12.py`, "
      "`ONE_PAGE_REVIEWER_CHECKLIST_V12.md`, `index.html` (visual preview)")
    a("")
    a("---")
    a("")
    a("## 0. Seedha jawab")
    a("")
    a(f"- **{len(DIAGRAMS)} original diagrams** `assets_v12/` me — har ek ka `<title>/<desc>`, "
      "koi `<image>` tag nahi, koi external URL nahi, koi logo/insignia nahi.")
    a(f"- **13-chapter EDL** — har chapter ke exact `start_frame` / `end_frame` / `duration_frames` "
      f"hain; total **{TOTAL_FRAMES}** frames, contiguous, 600.00s. Clip in/out sab `null`.")
    a("- **Render planner `BLOCKED`** — `python render_pipeline_v12.py --check-gate` abhi exit 2 "
      "karta hai (8 pending dossiers). `--self-test` farzi clearance ko reject karta hai. "
      "**Ye script kabhi ffmpeg nahi chalata.**")
    a("- **Ek-page checklist** aap / reviewer ke liye — 18 fields + 8 slot rows + sign-off.")
    a("- **`index.html`** = tamam diagrams ka visual preview (live preview me dekh sakte hain).")
    a("")
    a("---")
    a("")
    a("## 1. 10 original diagrams")
    a("")
    m.extend(table(["#", "File", "Slot", "Chapter", "Kya dikhata hai"],
                   [[str(i + 1), f"`{d['file']}`", str(d["slot"] or "-"), d["chapter"],
                     d["title"] + " - " + d["subtitle"]] for i, d in enumerate(DIAGRAMS)]))
    a("")
    a("> Ye sirf **spec nahi, ban chuke assets** hain. SVG hai isliye text editable hai, "
      "raster nahi, aur kisi aur ka content isme nahi. Footer har file me: "
      "`" + FOOTER + "`.")
    a("")
    a("---")
    a("")
    a("## 2. Frame-accurate EDL")
    a("")
    m.extend(table(["#", "Timecode", "Start f", "End f", "Frames", "VO words", "Diagram", "Clip"],
                   [[str(e["chapter"]), e["timecode"], str(e["start_frame"]),
                     str(e["end_frame_exclusive"]), str(e["duration_frames"]), str(e["vo_words"]),
                     (e["original_diagram_asset"] or "-").split("/")[-1],
                     f"SLOT {e['clip_slot']} - PENDING" if e["clip_slot"] else "-"]
                    for e in kit["edl"]]))
    a("")
    a(f"**Frame math:** {RUNTIME}s × {FPS}fps = **{TOTAL_FRAMES}** frames. Har chapter ka "
      "`end_frame` agle ke `start_frame` se milta hai; aakhri `18000`. Clip media path / SHA / "
      "in-out sab `null` — kyunki koi clip clear nahi hua.")
    a("")
    a("---")
    a("")
    a("## 3. QC checklist (20 items, sab `not_run`)")
    a("")
    m.extend(table(["#", "Check", "Target", "Source"],
                   [[str(i + 1), q["check"], q["target"], q["source"]]
                    for i, q in enumerate(kit["qc_checklist"])]))
    a("")
    a("> V10 ke `technical_checks` se 9 core checks liye gaye, **long-form ke liye adapt** kiye "
      "(vertical → landscape, 1482 → 18000 frames). −14 LUFS **spec target** hai, V12 ka "
      "measurement nahi; V10 me −14.60 LUFS measured tha. `technical_pass` kabhi creative "
      "approval nahi hota.")
    a("")
    a("---")
    a("")
    a("## 4. A/B plan (test hai, proven winner nahi)")
    a("")
    ab = kit["ab_test_plan"]
    a(f"- **Status:** `{ab['status']}` · {ab['studio_feature']}")
    a(f"- **Hooks:** {len(ab['hook_variants'])} · **Titles:** {len(ab['title_variants'])} · "
      f"**Thumbnail concepts:** {len(ab['thumbnail_concepts'])} (sirf description, koi image nahi bani)")
    a(f"- **Caveat:** {ab['honest_caveat']}")
    a(f"- **No claim:** {ab['no_claim']}")
    a("")
    a("## 5. Captions skeleton")
    a("")
    a(f"{len(kit['captions_skeleton'])} chapter windows with frame ranges. `text=null`, "
      "`timing_status=WORD_LEVEL_TIMING_PENDING_AFTER_ACTUAL_VO_RECORDING`. **Koi SRT file nahi "
      "bani** — word-level timing VO record hone ke baad hi sach me nikal sakti hai.")
    a("")
    a("---")
    a("")
    a("## 6. Render gate (executable)")
    a("")
    a("```text")
    a("$ python render_pipeline_v12.py --check-gate")
    a("BLOCKED - render NOT permitted. Reasons:")
    a("  - slot 1: clearance_status=pending (needs 'cleared')")
    a("  - slot 1: human_legal_review is not true")
    a("  - slot 1: 18 NULL rights fields")
    a("  ... NO MP4, NO VO, NO upload was attempted.")
    a("```")
    a("")
    a("`--self-test` ek **farzi `cleared` dossier** banata hai aur usse reject karta hai. "
      "Yani gate ko config se ya jumlon se bypass nahi kiya ja sakta.")
    a("")
    a("---")
    a("")
    a("## 7. Jo abhi bhi nahi hua")
    a("")
    for k in kit["non_claims"]:
        a(f"- `{k}` = **False**")
    a("")
    a("NO legal clearance, NO guaranteed views, NO human approval, NO render, NO upload, "
      "NO publish, NO monetization change, NO NASA endorsement, NO perfection.")
    a("")
    a("---")
    a("")
    a("## 8. Ab aapka ek hi qadam")
    a("")
    a("`ONE_PAGE_REVIEWER_CHECKLIST_V12.md` bhartein (18 fields × 8 slots + sign-off). Jaise hi "
      "wo complete ho, main seedha VO recording → edit → QC → metadata par ja sakta hoon. "
      "Usse pehle koi MP4 banana **gate todna** hoga — isliye nahi banaya.")
    a("")
    return "\n".join(m) + "\n"


FIELDS = [r["field"] for r in json.loads((D / "phase_b_rights_gate_v12.json").read_text(encoding="utf-8"))["field_rules"]]


def build_checklist_md() -> str:
    m = []
    a = m.append
    a("# V12 - ONE-PAGE HUMAN REVIEWER CHECKLIST")
    a("")
    a("> **Ye ek hi page aapko bharna hai.** Iske baad recording/edit shuru ho sakta hai. "
      "Agent ye fields khud **nahi** bhar sakta — inme se har ek ko insaan ne verify karna hai. "
      "**Ye legal advice nahi** (`not_a_legal_opinion=true`).")
    a("")
    a(f"**Video:** `MC-01 THE REPLAY CODE: 8 Moments, One Hidden Rule` · 10:00 · "
      f"8 DIFFERENT clips · source share <=13.3% · V10/Short asset `{NASA_ID_EXCLUDED}` **EXCLUDED**")
    a("")
    a("**Reviewer:** ____________________  **Date:** __________  **Overall decision:** ☐ APPROVE  ☐ REJECT  ☐ REVISE")
    a("")
    a("---")
    a("")
    a("## A. Har clip ke liye 18 fields (har row me tick + value)")
    a("")
    m.extend(table(["#", "Field", "Kya likhna hai"],
                   [[str(i + 1), f, "☐ verified  →  value: ____________________________________"]
                    for i, f in enumerate(FIELDS)]))
    a("")
    a("## B. 8 slots - ek line har clip")
    a("")
    m.extend(table(["Slot", "Analytic job", "Official source URL / asset ID", "Licence basis", "SHA-256", "Duration", "Score >=78", "Decision"],
                   [[str(n),
                     ["expectation violation", "physics / optics surprise", "timing / slow-motion frame",
                      "scale / size illusion", "native sound vs silence", "human reaction beat",
                      "near-miss / coincidence", "prediction test / callback"][n - 1],
                     "________________", "____________", "____________", "____s", "☐", "☐ OK / ☐ NO"]
                    for n in range(1, 9)]))
    a("")
    a("## C. Kill conditions - koi ek bhi mila to slot REJECT")
    a("")
    for k in json.loads((D / "phase_b_rights_gate_v12.json").read_text(encoding="utf-8"))["kill_conditions"]:
        a(f"- ☐ checked / ☐ not applicable — {k}")
    a("")
    a("## D. Sign-off")
    a("")
    a("```text")
    a("reviewer_name : ____________________________")
    a("review_date   : ____________________________")
    a("decision      : APPROVE | REJECT | REVISE")
    a("notes         : ____________________________")
    a("not_a_legal_opinion : true")
    a("```")
    a("")
    a("> **Rule:** `clearance_status='cleared'` sirf tab jab **sab 18 fields verified**, "
      "`human_legal_review=true`, aur upar sign-off me naam + tareekh + decision ho. "
      "`render_pipeline_v12.py` ye khud check karta hai aur warna **BLOCKED** deta hai.")
    a("")
    a("---")
    a("")
    a("**Yaad:** Public upload + monetization ON par likhit clearance, identifiable-person "
      "permission aur human legal review chahiye. Uploaded V10 Short ka monetization OFF karna "
      "abhi bhi pending hai. Koi guaranteed views / retention / virality / perfection ka dawa nahi.")
    a("")
    return "\n".join(m) + "\n"


def build_index_html() -> str:
    cards = "\n".join(
        f'''    <figure>
      <img src="{d['file']}" alt="{esc(d['title'])}" loading="lazy" />
      <figcaption><strong>{esc(str(i+1).zfill(2))} · {esc(d['title'])}</strong>
        <span>{esc(d['subtitle'])}</span>
        <code>{esc(d['file'])}</code></figcaption>
    </figure>''' for i, d in enumerate(DIAGRAMS))
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>V12 Phase D - original diagram kit</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; background:#080d16; color:#e8eef7;
         font-family: system-ui, -apple-system, "Segoe UI", Arial, sans-serif; }}
  header {{ padding:34px 5vw 22px; border-bottom:1px solid #24344c; }}
  h1 {{ margin:0 0 8px; font-size:30px; letter-spacing:.2px; }}
  .sub {{ color:#9fb2cc; font-size:15px; line-height:1.6; max-width:1000px; }}
  .badge {{ display:inline-block; margin-top:14px; padding:7px 13px; border-radius:999px;
            background:#3a2318; border:1px solid #ffc06a; color:#ffc06a; font-size:13px; font-weight:700; }}
  main {{ padding:26px 5vw 70px; display:grid; gap:26px;
          grid-template-columns:repeat(auto-fill,minmax(520px,1fr)); }}
  figure {{ margin:0; background:#0f1826; border:1px solid #24344c; border-radius:14px; overflow:hidden; }}
  img {{ display:block; width:100%; height:auto; background:#0a101a; }}
  figcaption {{ padding:14px 18px 18px; display:flex; flex-direction:column; gap:5px; }}
  figcaption strong {{ font-size:16px; }}
  figcaption span {{ color:#9fb2cc; font-size:13px; }}
  figcaption code {{ color:#5bd6d0; font-size:12px; }}
  footer {{ padding:24px 5vw 50px; color:#7f92ad; font-size:13px; border-top:1px solid #24344c; }}
  a {{ color:#5bd6d0; }}
</style></head>
<body>
<header>
  <h1>V12 Phase D — original diagram kit</h1>
  <div class="sub">Ten ORIGINAL SVG diagrams made for <strong>MC-01 THE REPLAY CODE: 8 Moments, One Hidden Rule</strong>.
  Own shapes and text only — no third-party images, logos, insignia or clips. These are assets for the
  10-minute long-form video, not the video itself.</div>
  <div class="badge">STATUS: ASSETS + PLANS ONLY · NO CLIP CLEARED · NO VO · NO RENDER · NO UPLOAD</div>
</header>
<main>
{cards}
</main>
<footer>
  Frame plan: 600s × 30fps = 18,000 frames · 13 chapters · source footage ≤80s (≤13.3%) ·
  V10/Short NASA water-bubble asset EXCLUDED from all 8 slots.<br/>
  Human rights gate is <strong>OPEN</strong>. See
  <a href="ONE_PAGE_REVIEWER_CHECKLIST_V12.md">ONE_PAGE_REVIEWER_CHECKLIST_V12.md</a>,
  <a href="PHASE_D_PRODUCTION_KIT_V12.md">PHASE_D_PRODUCTION_KIT_V12.md</a> and
  <a href="PHASE_C_SCRIPT_DRAFT_V12.md">PHASE_C_SCRIPT_DRAFT_V12.md</a>.
  No legal advice, no guaranteed views, no NASA endorsement.
</footer>
</body></html>
'''


def patch_next_action() -> None:
    txt = NEXT_ACTION.read_text(encoding="utf-8")
    if ADDENDUM_MARKER in txt:
        return
    add = (
        ADDENDUM_MARKER + " (assets + plans, NO render)\n\n"
        "- Phase D built from scratch without any cleared clip: 10 ORIGINAL SVG diagrams under "
        "`research/multi_clip_long_form_v12/assets_v12/` (own shapes/text only, no images, no external URLs, "
        "no logos/insignia), `index.html` visual preview, a frame-accurate 13-chapter EDL "
        "(600s x 30fps = 18,000 contiguous frames; all clip in/out, media paths and SHA values NULL), "
        "a 20-item QC checklist adapted from V10 technical_checks (all `not_run`), an A/B plan "
        "(3 hooks / 3 titles / 3 thumbnail concepts, NOT run), a captions SKELETON (no SRT file), "
        "and `render_pipeline_v12.py` which EXITS 2 with BLOCKED while any of the 8 dossiers is pending "
        "and rejects a forged cleared dossier in --self-test. It NEVER invokes ffmpeg.\n"
        "- `ONE_PAGE_REVIEWER_CHECKLIST_V12.md`: the single human-fillable page (18 fields, 8 slot rows, "
        "8 kill conditions, sign-off). This is the ONLY remaining blocker before VO recording / edit / QC.\n"
        "- HARD STOP UNCHANGED: no clip downloaded/cleared, no VO recorded, no MP4/render, no captions file, "
        "no thumbnail, no A/B test, no QC run, no upload/publish, no monetization change, no human approval, "
        "no legal clearance, no guaranteed views. Winner unchanged: MC-01, 8 DIFFERENT clips, 10:00, "
        "<=13.3% source share; V10/Short NASA asset still EXCLUDED.\n"
        "- This addendum does NOT supersede the standing 'await human full-motion/native-audio review' line below.\n\n"
    )
    NEXT_ACTION.write_text(add + txt, encoding="utf-8")


def dumps(o) -> str:
    return json.dumps(o, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for d in DIAGRAMS:
        (D / d["file"]).write_text(svg_shell(d["title"], d["subtitle"], d["body"], d["accent"]),
                                   encoding="utf-8")
    edl = build_edl()
    kit = build_kit(edl)
    (D / "phase_d_production_kit_v12.json").write_text(dumps(kit), encoding="utf-8")
    (D / "PHASE_D_PRODUCTION_KIT_V12.md").write_text(build_kit_md(kit), encoding="utf-8")
    (D / "ONE_PAGE_REVIEWER_CHECKLIST_V12.md").write_text(build_checklist_md(), encoding="utf-8")
    (D / "index.html").write_text(build_index_html(), encoding="utf-8")
    (D / "render_pipeline_v12.py").write_text(RENDER_PIPELINE, encoding="utf-8")
    patch_next_action()
    print(f"Wrote Phase D kit: {len(DIAGRAMS)} original SVGs + index.html + EDL ({TOTAL_FRAMES} frames) "
          f"+ {len(kit['qc_checklist'])} QC items + render gate")
    print(f"Gate status: pending (render planner will BLOCK) | all non-claims false: "
          f"{all(not v for v in kit['non_claims'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
