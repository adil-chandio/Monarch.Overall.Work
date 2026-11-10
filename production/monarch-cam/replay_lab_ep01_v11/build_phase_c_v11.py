#!/usr/bin/env python3
"""REPLAY LAB Ep.1 - Phase C voice-preview pack (V11).

Run from repo root:
    python production/monarch-cam/replay_lab_ep01_v11/build_phase_c_v11.py

Writes (idempotent):
  PHASE_C_VOICE_V11.md   phase_c_voice_v11.json

Reads the 4 preview MP3s generated separately with the user-selected voice-02.
This script does NOT synthesize audio, does NOT render video, does NOT upload.
Previews are NOT the final mix: NASA native audio must remain in the master.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "production" / "monarch-cam" / "replay_lab_ep01_v11"
AUDIO = OUT / "audio"
MD = OUT / "PHASE_C_VOICE_V11.md"
JS = OUT / "phase_c_voice_v11.json"

EDITION = "v11_replay_lab_ep01_phase_c_preview_2026-11-05"
HEAD = "5f8fcdaf5c4220f472eddbb01137b2478988af58"
VOICE_ID = "voice-02"
LANGUAGE = "en"
AUDITION_TEXT = (
    "That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, "
    "because every replay hides a different layer. Forty-two seconds of NASA footage. About eleven minutes "
    "of asking how that happened. A curved boundary between air and water bends light."
)

CLIPS = [
    {"id": "H1", "file": "audio/vo_preview_h1_v11.mp3", "kind": "hook_variant",
     "text": "That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, because every replay hides a different layer.",
     "note": "Default / selected in the idea study. Pattern interrupt; 'not a lens' resolves honestly in Chapter 4."},
    {"id": "H2", "file": "audio/vo_preview_h2_v11.mp3", "kind": "hook_variant",
     "text": "A sphere of water, a face, and one impossible-looking flip. In the next ten minutes we will watch the same 42 seconds eight times, and each time something new will make sense.",
     "note": "Replay promise up front. No reach or shock claim."},
    {"id": "H3", "file": "audio/vo_preview_h3_v11.mp3", "kind": "hook_variant",
     "text": "Why is that face upside down? The answer is inside the water - not the camera. Let's replay it slowly, then slower, then with the sound still on.",
     "note": "Question-first; native audio mentioned in the hook itself."},
    {"id": "CH05", "file": "audio/vo_preview_ch05_liquid_lens_v11.mp3", "kind": "chapter_excerpt",
     "text": "Now the flip. A curved boundary between air and water bends light. Light crossing that boundary is refracted, and the curved surface sends the rays into a reversed arrangement, so the picture arrives upside down. The same bending makes rainbows in raindrops. So the sphere is behaving like a small optical element - a liquid lens. That is why the opening line said it is not a lens: there is no glass, no manufactured optic. The water is doing the job. Freeze here, at twenty-three seconds, and watch it at half speed.",
     "note": "Longest excerpt - pacing / pronunciation check for the core physics chapter (3:30-5:00)."},
]

SOURCES = [
    {"n": 1, "id": "SCRIPT_DRAFT", "title": "Phase B script draft v0", "url": "workspace://production/monarch-cam/replay_lab_ep01_v11/SCRIPT_DRAFT_V11.md",
     "used_for": "Exact preview text: 3 hook variants and Chapter 5 VO."},
    {"n": 2, "id": "PHASE_A_AUDIT", "title": "Phase A source audit", "url": "workspace://production/monarch-cam/replay_lab_ep01_v11/PHASE_A_SOURCE_AUDIT_V11.md",
     "used_for": "Voice guardrails, NASA native-audio rule, 3 open blockers/gates."},
    {"n": 3, "id": "NASA_IMAGES", "title": "NASA Images and Media Usage Guidelines", "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
     "used_for": "Factual source disclosure allowed; no implied NASA review/permission; no 'according to NASA' style attribution in SI-assisted products; insignia restrictions."},
    {"n": 4, "id": "YT_AI_USE", "title": "YouTube Help - Disclosing use of GenAI content", "url": "https://support.google.com/youtube/answer/14328491?hl=en",
     "used_for": "AI-use toggle is a human decision; disclosure alone doesn't limit audience or monetization eligibility."},
    {"n": 5, "id": "V10_AUDIO", "title": "V10 QC / audio ledger", "url": "workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/qc_summary.json",
     "used_for": "9 objective audio gates, 33/33 technical checks; technical_pass separate from human listening."},
    {"n": 6, "id": "MONETIZATION_CARD", "title": "V11 monetization-ON action card", "url": "workspace://research/long_form_viral_idea_v11/MONETIZATION_ON_IMMEDIATE_ACTION_V11.md",
     "used_for": "Rights gate and user-reported Short monetization ON remain open."},
]


def cite(n: int) -> str:
    s = next(x for x in SOURCES if x["n"] == n)
    return f"[{s['n']}]({s['url']})"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


GUARDRAILS = [
    "Generic synthetic narration only. No real-person voice clone, no astronaut voice imitation.",
    "No time-stretch / speed change of the generated speech.",
    "NASA native crew audio stays in the master; these previews are isolated narration files, NOT a replacement or a final mix " + cite(2) + " " + cite(5) + ".",
    "No music, SFX, procedural bed or audio substitution.",
    "VO text never says 'according to NASA' and never implies NASA reviewed or approved the analysis " + cite(3) + ".",
    "No 'official NASA', no insignia, no endorsement, no invented date/outcome/view claim.",
    "AI-use toggle remains a human decision at upload time " + cite(4) + ".",
    "Human listening, full-motion review, creative approval and legal review are all still pending " + cite(5) + ".",
]

BLOCKERS = [
    "16:9 source: local master is 1080x1920 vertical; original 4K not present locally.",
    "Render/QC toolchain (ffmpeg, ffprobe, numpy, bundled v10_deps) absent in this snapshot.",
    "NASA promotional / identifiable current-astronaut rights gate OPEN; user-reported Short monetization ON; human_legal_review=false; commercial_monetization_clearance=false " + cite(6) + ".",
]

NON_CLAIMS = {
    "final_voiceover_complete": False,
    "voiceover_mixed_with_nasa_native_audio": False,
    "captions_burned": False,
    "video_rendered": False,
    "sixteen_by_nine_master_created": False,
    "technical_qc_run_on_previews": False,
    "human_creative_approval": False,
    "human_native_audio_listening": False,
    "human_full_motion_review": False,
    "human_legal_review": False,
    "legal_opinion": False,
    "commercial_monetization_clearance": False,
    "written_astronaut_or_csa_permission": False,
    "nasa_endorsement": False,
    "official_nasa_status": False,
    "guaranteed_virality": False,
    "guaranteed_retention": False,
    "perfection_or_zero_omission": False,
    "rights_gate_closed": False,
    "upload_or_publish_performed": False,
    "monetization_changed_by_agent": False,
    "youtube_data_api_called": False,
}


def probe() -> list:
    out = []
    for c in CLIPS:
        p = OUT / c["file"]
        out.append({**c, "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else None,
                    "sha256": sha(p) if p.exists() else None,
                    "id3_header": p.read_bytes()[:3] == b"ID3" if p.exists() else False,
                    "words": len(c["text"].split())})
    return out


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "or").replace("\n", " ") for x in r) + " |")
    return out


def build_md(clips: list) -> str:
    m = []
    a = m.append
    a("# REPLAY LAB Ep.1 — Phase C: Voice Preview")
    a("")
    a("> **Aage badh gaye ✅** — aapne audition me **`voice-02`** chuni. Usi voice se 4 preview clips bane hain: "
      "3 hooks + Chapter 5 (liquid lens). Ye **preview** hain, final voiceover ya mix nahi. "
      "Koi video render, caption, upload ya publish nahi hua.")
    a("")
    a(f"**Edition:** `{EDITION}` · **HEAD:** `{HEAD}` · **Voice:** `{VOICE_ID}` · **Language:** `{LANGUAGE}`")
    a("")
    a("---")
    a("")
    a("## 1. Sunne ke liye 4 files")
    a("")
    m.extend(table(["Clip", "File", "Words", "Bytes", "Kyun"],
                   [[c["id"], "`" + c["file"] + "`", c["words"], c["bytes"], c["note"]] for c in clips]))
    a("")
    a("Sab 4 MP3 valid `ID3` header ke saath hain; SHA256 niche JSON me. File size se zyada koi audio QC "
      "claim nahi — is snapshot me ffprobe/numpy maujood nahi " + cite(2) + ".")
    a("")
    a("---")
    a("")
    a("## 2. Script se exact text")
    a("")
    for c in clips:
        a(f"**{c['id']}:** {c['text']}")
        a("")
    a("---")
    a("")
    a("## 3. Voice rules (V10 se aage)")
    a("")
    for g in GUARDRAILS:
        a(f"- {g}")
    a("")
    a("---")
    a("")
    a("## 4. Abhi bhi 3 rukavatein")
    a("")
    for b in BLOCKERS:
        a(f"- {b}")
    a("")
    a("---")
    a("")
    a("## 5. Non-claims (sab `false`)")
    a("")
    a(", ".join("`" + k + "`" for k in NON_CLAIMS))
    a("")
    a("---")
    a("")
    a("## 6. Status table")
    a("")
    m.extend(table(["Phase", "Status"], [
        ["A - Source audit", "DONE"], ["B - Script draft", "DONE"],
        ["C - Voice preview", "DONE (4 clips, voice-02) — final VO baaki"],
        ["D - Edit 16:9", "BLOCKED (source + tooling)"],
        ["E - QC", "BLOCKED (tooling)"],
        ["F - Metadata", "PENDING"],
    ]))
    a("")
    a("---")
    a("")
    a("## 7. Aapka agla faisla")
    a("")
    a("1. **Hook** final karein: `H1` (default) / `H2` / `H3` — 3 clip sun kar.")
    a("2. **Voice** `voice-02` theek hai? Nahi to dobara audition kar sakte hain.")
    a("3. **16:9 source** ka tarika: original 4K re-fetch, ya human-approved crop/pillarbox plan.")
    a("")
    a("Uske baad main 12 chapters ka poori VO + caption timings taiyar karunga; render tabhi jab blockers clear hon. "
      "Ye legal opinion, clearance, human approval ya guaranteed result ka dawa nahi hai.")
    a("")
    return "\n".join(m) + "\n"


def main() -> int:
    clips = probe()
    JS.write_text(json.dumps({
        "schema_version": "1.0", "edition": EDITION, "head_at_writing": HEAD,
        "status": "phase_c_previews_done_final_vo_pending",
        "voice": {"voice_id": VOICE_ID, "language": LANGUAGE,
                  "selected_by": "user_voice_audition_battle_02",
                  "audition_text": AUDITION_TEXT,
                  "real_person_clone": False, "time_stretch": False,
                  "generic_synthetic_narration": True},
        "clips": clips, "guardrails": GUARDRAILS, "blockers": BLOCKERS,
        "non_claims": NON_CLAIMS, "sources": SOURCES,
        "scope": "isolated_narration_previews_only_no_mix_no_render_no_upload",
        "related_files": ["SCRIPT_DRAFT_V11.md", "PHASE_A_SOURCE_AUDIT_V11.md", "WORK_PLAN_V11.md"],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD.write_text(build_md(clips), encoding="utf-8")
    print("Wrote", MD.relative_to(ROOT), "+", JS.relative_to(ROOT))
    print("Clips:", [(c["id"], c["bytes"], c["id3_header"]) for c in clips])
    print("Voice:", VOICE_ID, "| non-claims all false:", all(not v for v in NON_CLAIMS.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
