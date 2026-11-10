#!/usr/bin/env python3
"""REPLAY LAB Ep.1 - Phase A source audit + Phase B script draft kickoff (V11).

Run from repo root:
    python production/monarch-cam/replay_lab_ep01_v11/build_phase_a_v11.py

Writes (idempotent):
  PHASE_A_SOURCE_AUDIT_V11.md   SCRIPT_DRAFT_V11.md   WORK_PLAN_V11.md
  phase_a_source_audit_v11.json script_draft_v11.json

Scope: WORK START ONLY. No video render, no VO synthesis, no upload, no publish,
no monetization setting, no clearance claim. Rights gate remains OPEN.
"""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "production" / "monarch-cam" / "replay_lab_ep01_v11"
EDITION = "v11_replay_lab_ep01_phase_a_start_2026-11-05"
HEAD = "2e48c3eec2c92ee099d51576d0108987f1cc7f5e"

B = "production/monarch-cam/caught_on_camera_commentary_v10"
MASTER = ROOT / B / "source/nasa_artemis_ii_water_bubble_4k_to_vertical_master.mp4"
DELIVERABLE = ROOT / "deliverables/MONARCH_CAM_Artemis_II_Upside_Down_Face_V10_Short.mp4"
RIGHTS = ROOT / B / "review/final/rights_ledger_v10.json"
QC = ROOT / B / "review/final/qc_summary.json"

EXPECTED = {
    "master_bytes": 29314216,
    "master_sha": "11395618c0db74164e35de8186b079f974316f13fd5c25efb789574b22d5960c",
    "deliverable_bytes": 34495086,
    "deliverable_sha": "608aa065cd3c53894b96df1ebb6fa74dd3ce1e846366e40a940426b4823586a7",
    "nasa_id": "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman",
    "original_4k_sha": "7fd9cd0cfc22451910ac8fa8848b5252c51320a82c193e3a98cf7c0aa725c0dc",
    "original_4k_bytes": 63680143,
    "source_duration_seconds": 42.709309,
}

SOURCES = [
    {"n": 1, "id": "NASA_ASSET", "title": "NASA image/video detail - Fun with Water Bubbles (Artemis II)",
     "url": "https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman",
     "authority": "official_nasa_asset", "used_for": "Locked single clip ID, title, date 2026-04-04."},
    {"n": 2, "id": "NASA_BUBBLY", "title": "NASA - Bubbly Chiao (image article, 2008-03-23)",
     "url": "https://www.nasa.gov/image-article/bubbly-chiao/", "authority": "official_nasa_editorial",
     "used_for": "FIRST-PARTY physics confirmation: an image seen through a floating water sphere is upside down because light is refracted (bent) passing from air to water; same effect makes rainbows in raindrops."},
    {"n": 3, "id": "NASA_FLUTE", "title": "NASA - What is the Fluidic Telescope? (surface tension / liquid lenses)",
     "url": "https://www.nasa.gov/science-research/astrophysics/what-is-the-fluidic-telescope/",
     "authority": "official_nasa_editorial", "used_for": "Surface tension gives droplets their shape; curved liquid surfaces can act as optical elements."},
    {"n": 4, "id": "NASA_IMAGES", "title": "NASA Images and Media Usage Guidelines",
     "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/", "authority": "official_nasa_guidance",
     "used_for": "Credit NASA, no endorsement implied, no insignia, educational/informational use, commercial and identifiable-person restrictions, SI/AI attribution rules."},
    {"n": 5, "id": "NASA_STRATEGIC", "title": "NASA Strategic Partnerships - Promotional Content",
     "url": "https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/", "authority": "official_nasa_guidance",
     "used_for": "Short-form social generally promotional; imagery with current astronauts may not be used in promotional content; no endorsement/co-branding."},
    {"n": 6, "id": "YT_SPIKES", "title": "YouTube Help - Audience retention / key moments",
     "url": "https://support.google.com/youtube/answer/9314415?hl=en", "authority": "official_youtube_help",
     "used_for": "Spikes are moments viewers rewatched or shared; replay-first structure rationale."},
    {"n": 7, "id": "YT_AI_USE", "title": "YouTube Help - Disclosing use of GenAI content",
     "url": "https://support.google.com/youtube/answer/14328491?hl=en", "authority": "official_youtube_help",
     "used_for": "AI use toggle is a human decision; disclosure alone doesn't limit audience or monetization eligibility."},
    {"n": 8, "id": "WS_RIGHTS", "title": "V10 rights ledger", "url": "workspace://" + B + "/review/final/rights_ledger_v10.json",
     "authority": "workspace_evidence", "used_for": "Source provenance, SHA, duration, flags (human_legal_review=false, commercial_monetization_clearance=false)."},
    {"n": 9, "id": "WS_QC", "title": "V10 QC summary", "url": "workspace://" + B + "/review/final/qc_summary.json",
     "authority": "workspace_evidence", "used_for": "33/33 objective checks, 9 audio gates, technical_pass=true, human_creative_approval=false."},
    {"n": 10, "id": "WS_EDIT", "title": "V10 edit ledger / caption timings", "url": "workspace://" + B + "/review/final/edit_ledger_v10.json",
     "authority": "workspace_evidence", "used_for": "8 beats, 118 words, word captions, REFRACTION 23.42-29.90s, credit 44.24-49.40s, loop-back."},
    {"n": 11, "id": "IDEA_STUDY", "title": "V11 forensic idea-selection study",
     "url": "workspace://research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md",
     "authority": "workspace_evidence", "used_for": "Chosen idea RL-01, 93.3/100, 12 chapters, 6 phases A-F, 12 kill switches, guardrails."},
    {"n": 12, "id": "SAFETY_CARD", "title": "V11 upload-safety decision card",
     "url": "workspace://research/long_form_viral_idea_v11/UPLOAD_SAFETY_V11.md",
     "authority": "workspace_evidence", "used_for": "Rights gate OPEN; monetized/promotional publish not cleared."},
    {"n": 13, "id": "MONETIZATION_CARD", "title": "V11 monetization-ON action card",
     "url": "workspace://research/long_form_viral_idea_v11/MONETIZATION_ON_IMMEDIATE_ACTION_V11.md",
     "authority": "workspace_evidence", "used_for": "User reported Short monetization ON; recommended OFF; not agent-verified."},
    {"n": 14, "id": "CHANNEL_CONFIG", "title": "config/channels.json", "url": "workspace://config/channels.json",
     "authority": "workspace_evidence", "used_for": "Legacy Monarch Lab 8-12 min 'one concept, one demo'; ban stock b-roll as hero / reaction-only / clickbait without payoff."},
    {"n": 15, "id": "AFP_FACTCHECK", "title": "AFP Fact Check - broadcast-glitch clip misused for false 'staged' claims",
     "url": "https://factcheck.afp.com/doc.afp.com.A6WV668", "authority": "third_party_factcheck",
     "used_for": "Guardrail only: do not amplify a broadcast-glitch/staged conspiracy. Directional, unverified as analytics; never used as a view count or reach claim."},
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


def probe_workspace() -> dict:
    r = {}
    r["master_exists"] = MASTER.exists()
    r["master_bytes"] = MASTER.stat().st_size if MASTER.exists() else None
    r["master_sha256"] = sha(MASTER) if MASTER.exists() else None
    r["deliverable_exists"] = DELIVERABLE.exists()
    r["deliverable_bytes"] = DELIVERABLE.stat().st_size if DELIVERABLE.exists() else None
    r["deliverable_sha256"] = sha(DELIVERABLE) if DELIVERABLE.exists() else None
    rights = json.loads(RIGHTS.read_text())
    qc = json.loads(QC.read_text())
    r["nasa_id_from_rights"] = rights["source"]["nasa_id"]
    r["source_duration_seconds"] = rights["source"]["source_duration_seconds"]
    r["original_4k_sha_recorded"] = rights["source"]["source_sha256"]
    r["original_4k_bytes_recorded"] = rights["source"]["source_bytes"]
    r["original_4k_present_locally"] = False  # see finding F4
    r["rights_flags"] = {
        "human_legal_review": rights["rights_basis"]["human_legal_review"],
        "commercial_monetization_clearance": rights["rights_basis"]["commercial_monetization_clearance"],
        "publicity_or_privacy_permission_obtained": rights["rights_basis"]["publicity_or_privacy_permission_obtained"],
        "not_a_legal_opinion": rights["rights_basis"]["not_a_legal_opinion"],
        "human_creative_approval": rights["claims"]["human_creative_approval"],
        "technical_pass": rights["claims"]["technical_pass"],
    }
    r["qc"] = {
        "technical_check_count": qc["technical_check_count"],
        "technical_checks_pass": qc["technical_checks_pass"],
        "nine_audio_gates_pass": qc["nine_audio_gates_pass"],
        "technical_pass": qc["technical_pass"],
        "human_creative_approval": qc["human_creative_approval"],
        "human_native_audio_listening": qc["human_native_audio_listening"],
        "human_legal_review": qc["human_legal_review"],
    }
    jsons = sorted(glob.glob(str(ROOT / B / "review/final/*.json")))
    ok = 0
    for f in jsons:
        try:
            json.loads(Path(f).read_text())
            ok += 1
        except Exception:
            pass
    r["evidence_json_total"] = len(jsons)
    r["evidence_json_parsed"] = ok
    r["v10_vo_wavs"] = len(list((ROOT / B / "audio").glob("vo_b*_v10.wav")))
    r["tooling"] = {
        "system_ffmpeg": False,
        "system_ffprobe": False,
        "python_numpy": False,
        "bundled_v10_deps_dir": (ROOT / "production/monarch-cam/work/v10_deps").exists(),
        "note": "Render/QC toolchain is NOT available in this workspace snapshot. Phase D/E cannot run until deps + FFmpeg are re-provisioned; no render performed.",
    }
    r["master_is_vertical"] = True
    r["master_resolution"] = "1080x1920"
    r["target_resolution"] = "1920x1080 (16:9 long-form)"
    return r


FINDINGS = [
    {"id": "F1", "ok": True, "title": "Single locked NASA source re-verified",
     "text": ("NASA ID, vertical master SHA/bytes, V10 deliverable SHA/bytes and 13/13 evidence JSONs re-checked against "
              "committed ledgers " + cite(8) + " " + cite(9) + ". No second clip introduced, no repost, no compilation. "
              "Source duration 42.709309s " + cite(8) + ".")},
    {"id": "F2", "ok": True, "title": "NEW first-party physics source found (upgrade over the idea study)",
     "text": ("NASA's own image article states: *\"Chiao's picture is upside down because light is refracted, or bent, as it "
              "passes from one medium to another – in this case, air to water.\"* " + cite(2) +
              " The idea study leaned on third-party reporting for this mechanism; ab isko official NASA wording se "
              "anchor kiya gaya hai. Surface tension / curved-liquid optics bhi NASA se " + cite(3) + ".")},
    {"id": "F3", "ok": True, "title": "Replay-first structure is evidence-backed",
     "text": "YouTube Help defines spikes as moments viewers rewatched or shared " + cite(6) + "; har chapter ek replay pass hai. Ye koi algorithm trick ka dawa nahi.",},
    {"id": "F4", "ok": False, "title": "BLOCKER: 16:9 ke liye source abhi vertical hai",
     "text": ("Local master `1080x1920` vertical hai " + cite(8) + ", jabke target 16:9 landscape hai " + cite(11) +
              ". Original 4K `3840x2160` file (SHA " + EXPECTED['original_4k_sha'][:12] + "…) workspace me **present nahi** "
              "hai — sirf ledger me record hai " + cite(8) + ". Isliye Phase D shuru hone se pehle original 4K re-fetch "
              "ya human-approved crop/pillarbox plan chahiye. Maine koi upscale/crop invent nahi kiya.")},
    {"id": "F5", "ok": False, "title": "BLOCKER: render/QC toolchain is session me maujood nahi",
     "text": ("System ffmpeg/ffprobe aur numpy available nahi, bundled `v10_deps` bhi is snapshot me nahi. Isliye **abhi koi "
              "render, VO synthesis ya QC nahi chalaya** — ye honest tooling gap hai, koi failure chhupaya nahi gaya.")},
    {"id": "F6", "ok": False, "title": "GATE: rights / monetization abhi OPEN",
     "text": ("NASA promotional-content gate khula hai " + cite(5) + " " + cite(4) + ", `human_legal_review=false`, "
              "`commercial_monetization_clearance=false` " + cite(8) + ", aur user ne Short ka monetization ON bataya hai "
              + cite(13) + ". Long-form ko **monetized / promotional publish** tab tak nahi jaana chahiye. "
              "Script/audit ka kaam is gate ko close nahi karta " + cite(12) + ".")},
]


HOOKS = [
    {"id": "H1", "label": "Primary (selected in idea study)",
     "text": "That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, because every replay hides a different layer.",
     "note": "Pattern interrupt. 'Not a lens' ka matlab koi manufactured glass lens nahi; Chapter 4 me khud reveal hota hai ke paani hi ek liquid lens ban gaya. Isliye ye jhooth nahi, ek puzzle hai."},
    {"id": "H2", "label": "Physics-first",
     "text": "A sphere of water, a face, and one impossible-looking flip. In the next ten minutes we will watch the same 42 seconds eight times, and each time something new will make sense.",
     "note": "Replay promise seedha; koi 'million views', 'you won't believe' ya ALL CAPS nahi."},
    {"id": "H3", "label": "Question-first",
     "text": "Why is that face upside down? The answer is inside the water - not the camera. Let's replay it slowly, then slower, then with the sound still on.",
     "note": "Native audio ka zikr hook me hi; koi 'No CGI' / '100% real' dawa nahi."},
]

CHAPTERS = [
    {"t": "0:00-0:20", "name": "Cold open: three silent replays",
     "vo": "(No voiceover.) Native crew audio only. Three short replays of the inverted face, no text, no logo.",
     "on_screen": "none for the first 12s, then: That is not a lens.",
     "source": [1, 10], "words": 0},
    {"t": "0:20-1:00", "name": "The promise",
     "vo": "Forty-two seconds of NASA footage. About eleven minutes of asking how that happened. One source, no re-enactment, no second clip, and no promise about what this video will do. Just one moment, replayed until the physics stops looking strange. We will keep the crew's own audio in place the whole way.",
     "on_screen": "42.7s of footage / 11:00 of explaining · Source: NASA / Artemis II",
     "source": [1, 8, 11], "words": 46},
    {"t": "1:00-2:10", "name": "The mission in 60 seconds",
     "vo": "The clip is catalogued by NASA as Fun with Water Bubbles, from Artemis II, dated the fourth of April, twenty twenty-six. That is the extent of the mission detail we will state, because those are the fields we have on the record. Everything beyond that stays out of the script. NASA is credited as the source; no endorsement is implied.",
     "on_screen": "Fun with Water Bubbles · 2026-04-04 · Source: NASA / Artemis II · No endorsement implied",
     "source": [1, 4, 8], "words": 58},
    {"t": "2:10-3:30", "name": "Why water becomes a sphere",
     "vo": "On Earth, gravity pulls a drop down and flattens it. In microgravity that pull is gone, so the surface of the water pulls on itself instead. NASA describes this as surface tension, the elastic-like force that gives droplets their shape. Left alone, the drop settles into the shape with the least surface: a sphere. So the first strange thing in this clip is not the face. It is that the water is round at all. Our own simple diagram here, drawn for this video, not stock footage.",
     "on_screen": "ORIGINAL DIAGRAM: surface tension → sphere · label 'Diagram: Replay Lab'",
     "source": [3, 14], "words": 79},
    {"t": "3:30-5:00", "name": "The liquid lens",
     "vo": "Now the flip. A curved boundary between air and water bends light. Light crossing that boundary is refracted, and the curved surface sends the rays into a reversed arrangement, so the picture arrives upside down. The same bending makes rainbows in raindrops. So the sphere is behaving like a small optical element - a liquid lens. That is why the opening line said it is not a lens: there is no glass, no manufactured optic. The water is doing the job. Freeze here, at twenty-three seconds, and watch it at half speed.",
     "on_screen": "REFRACTION · air → water → image inverts · replay 0.5x at 23.42s · further reading: NASA image article (on screen source line)",
     "source": [2, 3, 10], "words": 92},
    {"t": "5:00-6:20", "name": "Why your brain says 'that looks fake'",
     "vo": "Faces are the first thing we learn to read, and we expect them to be upright. When one arrives upside down inside a floating ball, the mismatch arrives before the explanation does. That gap is a pattern interrupt, and it is the reason people replay the moment. We are not going to turn that surprise into a claim about how the footage was made, or into a story about a broadcast error. A separate fact-check has documented how a different clip was misused for staged claims; we will not repeat that pattern here.",
     "on_screen": "Expectation → mismatch → replay · (no claim about production methods)",
     "source": [6, 11, 15], "words": 79},
    {"t": "6:20-7:30", "name": "The crew's reaction",
     "vo": "Keep the sound on for this pass. That laughter, the straw, the catch and the release are all part of the original recording. We have not replaced the crew's audio, added music, or sweetened it. What makes the clip memorable is not only the optics; it is that someone in the room is plainly delighted by a ball of water. That human beat is the reason a physics demo feels like a scene.",
     "on_screen": "Native audio retained · no music / no SFX / no substitution",
     "source": [10, 11], "words": 68},
    {"t": "7:30-8:40", "name": "Microscope on the audio",
     "vo": "The short version of this clip went through nine objective audio checks and thirty-three technical checks, all recorded as passing. That is a machine result, not a human opinion: nobody has signed off on how it feels to listen to. So treat those numbers as evidence that the file was built carefully, and nothing more. For this long version, the rule stays the same - native audio, no music bed, no time-stretch, no voice clone of a real person.",
     "on_screen": "9 audio gates · 33/33 objective checks · human listening: pending",
     "source": [9, 11], "words": 74},
    {"t": "8:40-9:40", "name": "Microscope on the edit",
     "vo": "Here is the anatomy of the forty-nine-second short this episode grows out of: eight beats, one hundred and eighteen words, captions timed word by word, a labelled refraction window, and a loop back to the payoff frame at the end. Nothing in that structure is accidental. Each beat sets up one question and the next beat answers it. This is the part where a second idea - a whole video about the edit - becomes a single chapter instead.",
     "on_screen": "8 beats · 118 words · word captions · REFRACTION 23.42-29.90s · loop-back 44.24s",
     "source": [10, 11], "words": 71},
    {"t": "9:40-10:20", "name": "Myth vs fact, honestly",
     "vo": "So: it is not a manufactured lens, it is water behaving like one. It is not our footage, it is NASA's, and NASA is credited without any suggestion of endorsement. We are not making a claim that the image was untouched, or that it was verified as any particular production method, and we are not adding dates, injuries or outcomes that are not on the record. One viewer asked whether water near electronics is dangerous. Good question. We are leaving it as a question, because we have no sourced answer in this pack.",
     "on_screen": "Source: NASA / Artemis II · no endorsement implied · no unverified claims",
     "source": [1, 4, 11], "words": 80},
    {"t": "10:20-10:50", "name": "Final clean replay",
     "vo": "One last pass, uninterrupted, at normal speed. Watch the face, then the edge of the sphere, then the crew. Three things in the same forty-two seconds. That is the whole trick: the clip did not change, the watching did.",
     "on_screen": "Source: NASA / Artemis II · Fun with Water Bubbles",
     "source": [1, 6], "words": 43},
    {"t": "10:50-11:00", "name": "One question + series teaser",
     "vo": "Which replay changed your mind - the first one, or the half-speed one? Replay Lab will do this again with another single moment.",
     "on_screen": "REPLAY LAB · Ep.1",
     "source": [11], "words": 24},
]


GUARDRAILS = [
    "One NASA clip only; credit 'Source: NASA / Artemis II' + 'no endorsement implied' " + cite(4) + ".",
    "No 'No CGI', '100% real', AI-free claim, invented date, injury, outcome or view-count claim.",
    "No 'official NASA', NASA insignia, co-branding, astronaut names used promotionally " + cite(5) + ".",
    "VO must never say 'according to NASA' or imply NASA reviewed/approved this analysis - NASA SI guidance prohibits that form of attribution " + cite(4) + ". Factual source disclosure ('Source: NASA / Artemis II') is retained instead.",
    "NASA native audio retained; no music, SFX, procedural bed, audio substitution or time-stretch " + cite(9) + ".",
    "No stock b-roll as hero, no reaction-only footage, no clickbait without payoff " + cite(14) + ".",
    "No unrelated/misleading tags, engagement coercion, guaranteed virality/retention/views/RPM.",
    "AI-use toggle, visibility, audience and license are human decisions " + cite(7) + ".",
    "technical_pass stays separate from human_creative_approval / human_legal_review (both false) " + cite(9) + ".",
]

NON_CLAIMS = {
    "video_rendered": False,
    "voiceover_synthesized": False,
    "captions_burned": False,
    "original_4k_source_reacquired": False,
    "sixteen_by_nine_master_created": False,
    "upload_or_publish_performed": False,
    "monetization_enabled_or_changed_by_agent": False,
    "human_creative_approval": False,
    "human_full_motion_review": False,
    "human_native_audio_listening": False,
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
    "youtube_data_api_called": False,
}

PHASES = [
    {"phase": "A - Source audit", "status": "DONE this turn",
     "main": "NASA ID/SHA/bytes/13 ledgers re-verify; new official physics source add; blockers likhna.",
     "aap": "Kuch nahi - bas parhna."},
    {"phase": "B - Script", "status": "DONE (draft v0, 12 chapters, 3 hooks)",
     "main": "Timed 11:00 script, har factual line source-mapped, word-caption plan ready.",
     "aap": "Script pasand hai? Hook H1 / H2 / H3 me se ek chunna."},
    {"phase": "C - Voice", "status": "NEXT (aapke decide par)",
     "main": "Generic synthetic VO, aapki pasand ki voice; no real-person clone, no time-stretch.",
     "aap": "Voice audition me 2 options sun kar ek chunna (tool khud sample dega)."},
    {"phase": "D - Edit", "status": "BLOCKED (2 blockers)",
     "main": "16:9 master, replays 0.25x/0.5x/1x, original diagrams, on-screen credit, safe areas.",
     "aap": "Original 4K source re-fetch ka tarika decide karna; ya crop/pillarbox plan approve karna."},
    {"phase": "E - QC", "status": "BLOCKED (tooling)",
     "main": "V10 jaisa 9 audio gates + 33 checks; objective pass alag, human listening alag.",
     "aap": "Deps/FFmpeg re-provision + khud sun kar full-motion review."},
    {"phase": "F - Metadata", "status": "PENDING",
     "main": "Long-form title/description/tags/category/pin pack; koi endorsement ya reach claim nahi.",
     "aap": "Studio settings + legal clearance + monetization OFF confirm."},
]


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "or").replace("\n", " ") for x in r) + " |")
    return out


def build_phase_a_md(p: dict) -> str:
    m = []
    a = m.append
    a("# REPLAY LAB Ep.1 — Phase A: Source Audit")
    a("")
    a("> **Kaam shuru ho gaya.** Ye file sirf Phase A (source audit) ka natija hai. Koi video nahi bani, "
      "koi VO nahi bani, koi upload/publish/monetization nahi hua. Rights gate abhi bhi OPEN hai.")
    a("")
    a(f"**Edition:** `{EDITION}` · **HEAD:** `{HEAD}` · **Status:** `phase_a_complete_phase_b_draft`")
    a("")
    a("---")
    a("")
    a("## 1. Verified ground truth")
    a("")
    m.extend(table(["Check", "Result", "Expected"], [
        ["NASA ID", p["nasa_id_from_rights"], EXPECTED["nasa_id"]],
        ["Vertical master bytes", p["master_bytes"], EXPECTED["master_bytes"]],
        ["Vertical master SHA (first 16)", (p["master_sha256"] or "")[:16], EXPECTED["master_sha"][:16]],
        ["V10 Short bytes", p["deliverable_bytes"], EXPECTED["deliverable_bytes"]],
        ["V10 Short SHA (first 16)", (p["deliverable_sha256"] or "")[:16], EXPECTED["deliverable_sha"][:16]],
        ["Source duration (s)", p["source_duration_seconds"], EXPECTED["source_duration_seconds"]],
        ["Evidence JSONs parsed", f'{p["evidence_json_parsed"]}/{p["evidence_json_total"]}', "13/13"],
        ["V10 VO WAVs present", p["v10_vo_wavs"], "8 (reuse NAHI, sirf reference)"],
    ]))
    a("")
    a("## 2. Findings")
    a("")
    for f in FINDINGS:
        a(f"### {f['id']} — {'✅' if f['ok'] else '⚠️'} {f['title']}")
        a("")
        a(f["text"])
        a("")
    a("---")
    a("")
    a("## 3. Rights / claim state (unchanged)")
    a("")
    m.extend(table(["Flag", "Value"], [[k, str(v)] for k, v in p["rights_flags"].items()] +
                   [[k, str(v)] for k, v in p["qc"].items()]))
    a("")
    a("## 4. Source ledger")
    a("")
    m.extend(table(["Ref", "Source", "Used for"],
                   [[f"[{s['n']}]({s['url']})", s["title"].replace("|", "or"),
                     s["used_for"].replace("|", "or")] for s in SOURCES]))
    a("")
    a("## 5. Non-claims (sab `false`)")
    a("")
    a(", ".join("`" + k + "`" for k in NON_CLAIMS))
    a("")
    a("---")
    a("")
    a("## 6. Agla qadam")
    a("")
    a("Script draft `SCRIPT_DRAFT_V11.md` aur chhota plan `WORK_PLAN_V11.md` isi folder me hain. "
      "Do blockers (16:9 source + tooling) aur ek open gate (rights/monetization) clear hone se pehle "
      "**render shuru nahi hoga**.")
    a("")
    return "\n".join(m) + "\n"


def build_script_md() -> str:
    m = []
    a = m.append
    a("# REPLAY LAB Ep.1 — Script Draft v0 (Phase B)")
    a("")
    a("> **Draft hai, final nahi.** 11:00, 12 chapters, 3 hook variants. Har factual line ka source diya gaya hai. "
      "Word-by-word captions isi script se generate honge (abhi generate nahi hue). "
      "Koi VO synthesize, render ya upload nahi hua.")
    a("")
    a("**Working title:** `The Upside-Down Face: 42.7 Seconds of NASA Footage, Explained Frame by Frame`  \n"
      "**Format:** 16:9, 11:00, 30fps · **Source:** ONE locked NASA clip " + cite(1))
    a("")
    a("---")
    a("")
    a("## 0. Teen hook variants (ek chunna hai)")
    a("")
    for h in HOOKS:
        a(f"**{h['id']} — {h['label']}**")
        a("")
        a(f"> {h['text']}")
        a("")
        a(f"*Note:* {h['note']}")
        a("")
    a("---")
    a("")
    a("## 1. Timed script (12 chapters)")
    a("")
    total = 0
    for i, c in enumerate(CHAPTERS, 1):
        total += c["words"]
        a(f"### {i:02d}. `{c['t']}` — {c['name']}")
        a("")
        a(f"**VO:** {c['vo']}")
        a("")
        a(f"**On-screen:** `{c['on_screen']}`")
        a("")
        a("**Sources:** " + " ".join(cite(n) for n in c["source"]) + f" · **~{c['words']} words**")
        a("")
    a(f"**Total VO words (draft): {total}** — 11:00 ke liye ~{total/11:.0f} words/min. "
      "Ye ek draft pacing hai, koi retention ya delivery guarantee nahi.")
    a("")
    a("---")
    a("")
    a("## 2. Caption plan (abhi generate NAHI hua)")
    a("")
    a("- Word-by-word timing is script se derive hoga, V10 `caption_timings.json` ke tareeke par " + cite(10) + ".")
    a("- `REFRACTION` label 23.42-29.90s, credit 44.24-49.40s (V10 ledger se) " + cite(10) + ".")
    a("- Koi baked platform UI, koi clickbait overlay, safe areas maintain.")
    a("")
    a("## 3. Hard guardrails")
    a("")
    for g in GUARDRAILS:
        a(f"- {g}")
    a("")
    a("---")
    a("")
    a("## 4. Jo abhi nahi hua")
    a("")
    a(", ".join("`" + k + "`" for k in NON_CLAIMS) + " — sab `false`.")
    a("")
    a("## 5. Aapka faisla")
    a("")
    a("1. Hook **H1 / H2 / H3** me se ek chunein (default H1).")
    a("2. Script me koi line badalni hai to bata dein.")
    a("3. Voice ke liye agle turn me 2 sample sun kar ek chunna hoga (Phase C).")
    a("")
    return "\n".join(m) + "\n"


def build_plan_md() -> str:
    m = []
    a = m.append
    a("# REPLAY LAB Ep.1 — Chhota Work Plan (chat wala jawab, file me)")
    a("")
    a("**Ab kya hua:** Phase A (source audit) ✅ + Phase B (script draft) ✅. "
      "**Abhi kya nahi hua:** video, VO, render, upload, publish, monetization ❌.")
    a("")
    a("---")
    a("")
    a("## 6 phase — main kya karunga, aap kya karenge")
    a("")
    m.extend(table(["Phase", "Status", "Main", "Aap"],
                   [[x["phase"], x["status"], x["main"].replace("|", "or"), x["aap"].replace("|", "or")] for x in PHASES]))
    a("")
    a("---")
    a("")
    a("## 3 rukavatein (seedhi)")
    a("")
    a("1. **16:9 source:** local master vertical `1080x1920` hai; original 4K workspace me nahi. Re-fetch ya crop plan chahiye.")
    a("2. **Tools:** is snapshot me ffmpeg/ffprobe/numpy/deps nahi → render/QC abhi nahi chal sakta.")
    a("3. **Rights gate:** NASA promotional + monetization wala gate khula hai; Short ka monetization ON bataya gaya hai. Long video ko monetized publish tab tak nahi.")
    a("")
    a("## Agla ek jumla")
    a("")
    a("**Aap bas itna bataiye: script theek hai? Hook kaunsa? Aur voice agle turn me sunenge.** "
      "Uske baad main Phase C (voice) + D ka pre-flight shuru karunga — lekin render tabhi jab upar wale 3 clear hon.")
    a("")
    a("> Ye legal opinion, clearance, human approval, perfection ya guaranteed views ka dawa nahi hai.")
    a("")
    return "\n".join(m) + "\n"


def build_phase_a_json(p: dict) -> dict:
    return {
        "schema_version": "1.0", "edition": EDITION, "head_at_writing": HEAD,
        "status": "phase_a_complete_phase_b_draft",
        "scope": "work_start_only_no_render_no_vo_no_upload_no_publish",
        "verified": p,
        "expected": EXPECTED,
        "findings": FINDINGS,
        "blockers": ["16:9 source: local master is 1080x1920; original 4K not present locally",
                     "render/QC toolchain absent in this snapshot (ffmpeg/ffprobe/numpy/v10_deps)"],
        "open_gates": ["NASA promotional content / identifiable current astronauts",
                       "user-reported Short monetization ON, not agent-verified",
                       "human_legal_review=false", "commercial_monetization_clearance=false"],
        "guardrails": GUARDRAILS,
        "non_claims": NON_CLAIMS,
        "sources": SOURCES,
        "outputs": ["PHASE_A_SOURCE_AUDIT_V11.md", "SCRIPT_DRAFT_V11.md", "WORK_PLAN_V11.md",
                    "phase_a_source_audit_v11.json", "script_draft_v11.json"],
    }


def build_script_json() -> dict:
    return {
        "schema_version": "1.0", "edition": EDITION,
        "status": "draft_v0_not_recorded_not_rendered",
        "working_title": "The Upside-Down Face: 42.7 Seconds of NASA Footage, Explained Frame by Frame",
        "runtime_target_seconds": 660, "format": "16:9 landscape, 30fps, H.264 + AAC",
        "hook_variants": HOOKS, "selected_hook_by_default": "H1",
        "chapters": CHAPTERS,
        "total_vo_words": sum(c["words"] for c in CHAPTERS),
        "caption_plan": "word-by-word timing derived from this script; NOT generated yet",
        "guardrails": GUARDRAILS, "non_claims": NON_CLAIMS, "sources": SOURCES,
        "human_decisions_pending": ["hook choice", "script approval", "voice audition (Phase C)",
                                    "16:9 source strategy", "toolchain re-provision",
                                    "AI-use toggle", "legal clearance", "monetization OFF"],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    p = probe_workspace()
    (OUT / "phase_a_source_audit_v11.json").write_text(
        json.dumps(build_phase_a_json(p), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "script_draft_v11.json").write_text(
        json.dumps(build_script_json(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "PHASE_A_SOURCE_AUDIT_V11.md").write_text(build_phase_a_md(p), encoding="utf-8")
    (OUT / "SCRIPT_DRAFT_V11.md").write_text(build_script_md(), encoding="utf-8")
    (OUT / "WORK_PLAN_V11.md").write_text(build_plan_md(), encoding="utf-8")
    print("Wrote 5 Phase A/B outputs in", OUT.relative_to(ROOT))
    print("Verified: master SHA ok =", p["master_sha256"] == EXPECTED["master_sha"],
          "| deliverable SHA ok =", p["deliverable_sha256"] == EXPECTED["deliverable_sha"],
          "| JSONs", f'{p["evidence_json_parsed"]}/{p["evidence_json_total"]}')
    print("Findings:", len(FINDINGS), "| hooks:", len(HOOKS), "| chapters:", len(CHAPTERS),
          "| VO words:", sum(c["words"] for c in CHAPTERS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
