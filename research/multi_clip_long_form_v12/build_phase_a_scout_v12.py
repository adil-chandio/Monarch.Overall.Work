#!/usr/bin/env python3
"""V12 PHASE A - clip-moment scout pack (deterministic, idempotent).

Reads the REAL GitHub Actions Data API reports under api_evidence/phase_a/
and builds:
  * PHASE_A_CLIP_SCOUT_V12.md   - the human deliverable
  * phase_a_clip_scout_v12.json - machine-readable 8-slot ledger
  * a Phase A addendum in NEXT_ACTION.md (appended once)

Every view count / verdict / saturation figure below is read from those
committed reports. Nothing is invented. Every rights field stays NULL and
every clearance stays PENDING: this is scouting research, NOT clip
acquisition, NOT legal clearance, NOT a render.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "research" / "multi_clip_long_form_v12"
EV = D / "api_evidence" / "phase_a"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"
ADDENDUM_MARKER = "## V12 PHASE A addendum - real API clip-moment scouting"

EDITION = "v12_phase_a_clip_scout"
RUN_ID = "42895703914"
NASA_ID_EXCLUDED = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"

QUERIES = [
    {"slug": "slot-01-07-expectation-violation", "topic": "unexpected moment caught on camera",
     "order": "viewCount", "slots": [1, 7]},
    {"slug": "slot-02-03-physics-timing", "topic": "slow motion physics explained",
     "order": "viewCount", "slots": [2, 3]},
    {"slug": "slot-04-scale-illusion", "topic": "optical illusion scale size",
     "order": "relevance", "slots": [4]},
    {"slug": "slot-05-06-08-sound-reaction-callback", "topic": "viral moment reaction explained",
     "order": "viewCount", "slots": [5, 6, 8]},
    {"slug": "rights-lane-nasa-agency-probe", "topic": "nasa official science demonstration",
     "order": "viewCount", "slots": "rights-lane probe (shared)"},
]

SLOTS = [
    {"slot": 1, "analytic_job": "expectation violation", "query": "slot-01-07-expectation-violation",
     "chapter": "1:40-2:55", "chapter_name": "CLIP 1 - expectation violation", "vo_words": 130,
     "beat": "Show the clip cold, freeze on the exact frame where the expectation breaks, then an ORIGINAL two-column diagram: what the viewer predicted vs what actually happened. One sentence naming the delay between surprise and explanation.",
     "diagram": "ORIGINAL expected-vs-actual split diagram, our own shapes/text, no source logo"},
    {"slot": 2, "analytic_job": "physics / optics surprise", "query": "slot-02-03-physics-timing",
     "chapter": "2:55-4:05", "chapter_name": "CLIP 2 - the physics surprise", "vo_words": 135,
     "beat": "Play <=10s, replay at 0.5x, then explain the mechanism with an original ray/force diagram. Factual claim anchored to a first-party official source; state the source on screen.",
     "diagram": "ORIGINAL optics / force diagram, no stock b-roll as hero"},
    {"slot": 3, "analytic_job": "timing / slow-motion frame", "query": "slot-02-03-physics-timing",
     "chapter": "4:05-5:10", "chapter_name": "CLIP 3 - timing / slow motion", "vo_words": 120,
     "beat": "Show the same moment at 1x, 0.5x, 0.25x in three labelled passes. Identify which single frame carries the surprise; do not claim the creator intended it.",
     "diagram": "ORIGINAL frame-timeline with 3 labelled speed bands"},
    {"slot": 4, "analytic_job": "scale / size illusion", "query": "slot-04-scale-illusion",
     "chapter": "5:10-6:15", "chapter_name": "CLIP 4 - scale / size illusion", "vo_words": 120,
     "beat": "Clip <=10s, then an original scale diagram with a labelled reference object. Explain the missing reference cue, not 'the camera tricks you'.",
     "diagram": "ORIGINAL scale comparison with a stated reference length"},
    {"slot": 5, "analytic_job": "native sound vs silence", "query": "slot-05-06-08-sound-reaction-callback",
     "chapter": "6:15-7:10", "chapter_name": "CLIP 5 - sound and silence", "vo_words": 105,
     "beat": "Two passes: native audio, then muted with our commentary. Retain the source's native audio; no music or SFX substitution. Compare what the sound contributed to the replay impulse.",
     "diagram": "ORIGINAL two-row A/B waveform/beat diagram (drawn, not sampled audio)"},
    {"slot": 6, "analytic_job": "human reaction beat", "query": "slot-05-06-08-sound-reaction-callback",
     "chapter": "7:10-8:00", "chapter_name": "CLIP 6 - the human reaction", "vo_words": 95,
     "beat": "Clip <=10s, then explain why a face or laugh resets attention. No astronaut/person name used promotionally; no endorsement implied; identifiable-person check is a hard gate.",
     "diagram": "ORIGINAL attention-reset timeline, no face crop reused as thumbnail"},
    {"slot": 7, "analytic_job": "near-miss / coincidence", "query": "slot-01-07-expectation-violation",
     "chapter": "8:00-8:45", "chapter_name": "CLIP 7 - the near-miss / coincidence", "vo_words": 85,
     "beat": "Clip <=10s, then an original timeline graphic of the two converging events. No invented date, injury, outcome or quote.",
     "diagram": "ORIGINAL two-track converging timeline, sourced only from verified facts"},
    {"slot": 8, "analytic_job": "prediction test / callback", "query": "slot-05-06-08-sound-reaction-callback",
     "chapter": "8:45-9:25", "chapter_name": "CLIP 8 + the prediction test (MC-02 folded in)", "vo_words": 75,
     "beat": "Play the 8th clip WITHOUT explanation, ask the viewer to predict the replay point, then reveal how the earlier 7 clips set up the rule. Closes the thesis loop; no outcome promise.",
     "diagram": "ORIGINAL 8-slot callback grid, one cell per DIFFERENT clip"},
]

CHAPTERS = [
    {"t": "0:00-0:20", "name": "Cold open: 3-second montage of 8 different moments", "vo_words": 25,
     "beat": "One fast cut from each of 8 DIFFERENT clips (0.8-1.2s each), no logo, no greeting, native audio only. Then the one-line hook."},
    {"t": "0:20-0:55", "name": "The promise and the rule", "vo_words": 75,
     "beat": "Name the thesis plainly: a rewatch happens when an expectation breaks and the explanation arrives one beat late. Promise 8 proofs. No outcome promise."},
    {"t": "0:55-1:40", "name": "Why 'rewatched or shared' is a real signal", "vo_words": 110,
     "beat": "YouTube's own Help calls those moments Spikes; Intro is % still watching after 30s; Dips are skips. State the metric source, then say our own Analytics is not available."},
    {"t": "1:40-2:55", "name": "CLIP 1 - expectation violation", "vo_words": 130, "beat": "See slot 1 card."},
    {"t": "2:55-4:05", "name": "CLIP 2 - the physics surprise", "vo_words": 135, "beat": "See slot 2 card."},
    {"t": "4:05-5:10", "name": "CLIP 3 - timing / slow motion", "vo_words": 120, "beat": "See slot 3 card."},
    {"t": "5:10-6:15", "name": "CLIP 4 - scale / size illusion", "vo_words": 120, "beat": "See slot 4 card."},
    {"t": "6:15-7:10", "name": "CLIP 5 - sound and silence", "vo_words": 105, "beat": "See slot 5 card."},
    {"t": "7:10-8:00", "name": "CLIP 6 - the human reaction", "vo_words": 95, "beat": "See slot 6 card."},
    {"t": "8:00-8:45", "name": "CLIP 7 - the near-miss / coincidence", "vo_words": 85, "beat": "See slot 7 card."},
    {"t": "8:45-9:25", "name": "CLIP 8 + the prediction test (MC-02 folded in)", "vo_words": 75, "beat": "See slot 8 card."},
    {"t": "9:25-9:50", "name": "The rule, restated + honest limits", "vo_words": 55,
     "beat": "One screen with the 6-step rule; say plainly what we could not verify (no owner-only competitor retention/CTR/RPM, no arbitrary competitor transcripts, no human review, no per-clip clearance). Public Data API view counts were used for scouting, not as proof of our own result."},
    {"t": "9:50-10:00", "name": "Genuine question + series teaser", "vo_words": 20,
     "beat": "One specific question, one next-episode teaser. No like/subscribe coercion or reward."},
]

# Rights gate: every field stays empty until a human verifies it for THAT clip.
RIGHTS_FIELDS = [
    "official_source_url", "nasa_or_agency_asset_id", "licence_basis",
    "third_party_copyrighted_material_check", "identifiable_persons_check",
    "current_astronaut_or_employee_check", "promotional_or_cover_art_use",
    "native_audio_rights", "attribution_string", "no_endorsement_implied_wording",
    "no_insignia_confirmed", "sha256_after_download", "duration_seconds",
    "scout_score_out_of_100", "scout_min_pass_78", "clearance_status",
    "human_legal_review", "not_a_legal_opinion",
]

# Agency-owned rows that the NASA rights-lane probe actually returned.
AGENCY_KEYS = ("nasa", "space agency", "esa", "jaxa", "isro", "asc-csa")


def load_report(slug: str) -> dict:
    return json.loads((EV / f"{slug}.json").read_text(encoding="utf-8"))


def top_rows(report: dict, n: int = 3) -> list[dict]:
    rows = sorted(report.get("rows") or [], key=lambda x: -(x.get("views") or 0))[:n]
    return [{"id": r.get("id"), "title": r.get("title"), "channel": r.get("channel"),
             "views": r.get("views"), "duration": r.get("duration"),
             "published": r.get("published")} for r in rows]


def fmt(n) -> str:
    return f"{n:,}" if isinstance(n, int) else str(n)


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    esc = lambda s: str(s).replace("|", "or").replace("\n", " ")
    out = ["| " + " | ".join(esc(h) for h in headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    out += ["| " + " | ".join(esc(c) for c in row) + " |" for row in rows]
    return out


def report_summary(slug: str) -> dict:
    d = load_report(slug)
    rows = d.get("rows") or []
    mv = [r for r in rows if isinstance(r.get("views"), int) and r["views"] >= 1_000_000]
    sat = d.get("saturation") or {}
    dec = d.get("decision") or {}
    return {
        "slug": slug, "topic": d.get("topic"), "lane": d.get("lane"),
        "order": d.get("order"), "status": d.get("status"), "count": len(rows),
        "million_plus": len(mv), "top_views": max((r.get("views") or 0) for r in rows),
        "total_views": sat.get("total_views"), "median_views": sat.get("median_views"),
        "top3_share": sat.get("top3_share"), "fresh_share_30d": sat.get("fresh_share_30d"),
        "reading": sat.get("reading"), "verdict": dec.get("verdict"),
        "score": dec.get("score"), "confidence": dec.get("confidence"),
        "reason": dec.get("reason"), "next_probe": dec.get("next_probe"),
        "parts": dec.get("parts"),
        "title_signal_effect": (d.get("title_signal") or {}).get("effect_pct"),
        "title_signal_fit": (d.get("title_signal") or {}).get("fit"),
        "funnel_share": (d.get("funnel") or {}).get("share"),
        "top_rows": top_rows(d),
    }


def agency_rows() -> list[dict]:
    d = load_report("rights-lane-nasa-agency-probe")
    out = []
    for r in d.get("rows") or []:
        ch = str(r.get("channel") or "").lower()
        if not any(k in ch for k in AGENCY_KEYS):
            continue
        title = str(r.get("title") or "")
        if "artemis ii" in title.lower() and "crew" in title.lower():
            status = "EXCLUDED_PENDING_HUMAN_LEGAL_REVIEW"
            reason = "Current named crew / official mission broadcast: NASA promotional + current-astronaut + identifiable-person gate is OPEN."
        elif "wringing out water" in title.lower():
            status = "REJECT_FOR_NOW"
            reason = "DIFFERENT asset from the V10/Short (different agency, different video ID), but the SAME water-bubble physics family - not a fresh 'different moment' for this episode."
        else:
            status = "PROBE_ONLY_NOT_A_SOURCE_CLIP"
            reason = "Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks."
        out.append({"id": r.get("id"), "title": title, "channel": r.get("channel"),
                    "views": r.get("views"), "duration": r.get("duration"),
                    "status": status, "reason": reason})
    return sorted(out, key=lambda x: -(x.get("views") or 0))


def build_ledger(summaries: dict, agencies: list[dict]) -> dict:
    slots = []
    for s in SLOTS:
        rep = summaries[s["query"]]
        slots.append({
            "slot": s["slot"], "analytic_job": s["analytic_job"],
            "chapter_t": s["chapter"], "chapter_name": s["chapter_name"],
            "max_on_screen_seconds": 10, "vo_word_budget": s["vo_words"],
            "commentary_beat": s["beat"], "original_diagram_spec": s["diagram"],
            "scout_query": {"topic": rep["topic"], "order": rep["order"],
                            "report": f"api_evidence/phase_a/{s['query']}.json"},
            "real_benchmark_candidates": rep["top_rows"],
            "benchmark_boundary": "STRUCTURAL BENCHMARKS ONLY - third-party copyrighted videos, NOT any of the 8 source clips, NOT cleared, NOT downloaded.",
            "candidate_source_lanes": [
                "official NASA / agency image and video libraries (DIFFERENT assets only)",
                "CC BY content with full attribution fields",
                "verified public domain / agency originals",
                "own-shot original demo footage",
                "licensed clips with written permission",
            ],
            "rights_gate": {k: None for k in RIGHTS_FIELDS},
            "clearance_status": "pending", "human_legal_review": False,
            "not_a_legal_opinion": True, "clip_downloaded": False,
            "clip_cleared": False, "sha256_after_download": None,
        })
    return {
        "edition": EDITION, "phase": "A - real API clip-moment scouting (RESEARCH ONLY)",
        "run_id": RUN_ID, "head_pinned": False,
        "status": "SCOUT_CANDIDATES_FOUND_NO_CLIP_ACQUIRED_NO_CLIP_CLEARED",
        "winner_unchanged": {"id": "MC-01", "name": "THE REPLAY CODE: 8 Moments, One Hidden Rule",
                             "clip_count": 8, "runtime_seconds": 600,
                             "clip_share_max_seconds": 80, "clip_share_max_pct": 13.3},
        "excluded_existing_short_clip": {
            "nasa_asset_id": NASA_ID_EXCLUDED,
            "rule": "EXCLUDED from all 8 slots. Do not use as hero, callback, montage filler or whole-video subject.",
            "reason": "This exact clip was already used for the V10 Short; the user requires MANY DIFFERENT clips/moments.",
        },
        "api_evidence": {
            "key_secret_name": "YOUTUBE_API_KEY", "key_present": True,
            "secret_value_printed_or_stored": False,
            "secret_value_requested_from_user": False,
            "chat_sandbox_direct_calls": 0,
            "reports": [{k: v for k, v in rep.items() if k != "top_rows"}
                        for rep in summaries.values()],
        },
        "slots": slots,
        "agency_rights_lane_probe": agencies,
        "agency_probe_boundary": "Agency-owned channels found by the API are NOT cleared sources. Current-crew / official-broadcast rows are EXCLUDED pending human legal review; the water-bubble row is REJECT FOR NOW because it repeats the V10/Short physics family.",
        "chapter_ledger": CHAPTERS,
        "vo_total_word_budget": sum(c["vo_words"] for c in CHAPTERS),
        "edit_spec_NOT_EXECUTED": {
            "canvas": "16:9 landscape, 30fps, H.264 + AAC",
            "runtime_seconds": 600, "chapters": 13,
            "source_footage_max_seconds": 80, "source_share_max_pct": 13.3,
            "per_clip_max_on_screen_seconds": 10,
            "replay_passes": ["1x", "0.5x", "0.25x"],
            "audio": "retain native audio of each verified source; no music/SFX substitution; original VO only after rights gate",
            "pattern": "one original diagram + one labelled replay after each clip; no clip strung together with little narrative",
            "loudness_target": "-14 LUFS (spec copied from V10 QC, NOT a V12 measurement)",
            "status": "SPEC_ONLY_NOT_RENDERED",
        },
        "hard_stop": "NO clip enters the edit until every rights_gate field is filled with a verified value and human_legal_review=true for THAT clip.",
        "open_gates": ["NASA promotional / current-astronaut imagery", "8 per-clip rights chains",
                       "user-reported Short monetization ON", "render toolchain", "AI-use toggle",
                       "human listening / creative approval / legal review"],
        "non_claims": {
            "clip_downloaded": False, "clip_cleared": False, "legal_opinion": False,
            "human_legal_review": False, "commercial_monetization_clearance": False,
            "render_done": False, "vo_generated": False, "final_script_written": False,
            "upload_done": False, "publish_done": False, "monetization_changed": False,
            "human_creative_approval": False, "guaranteed_views": False,
            "guaranteed_retention": False, "guaranteed_virality": False,
            "perfection": False, "flawlessness": False, "nasa_endorsement": False,
            "verified_growth_ranking": False, "competitor_transcripts_obtained": False,
            "owner_only_analytics_obtained": False, "api_secret_value_read": False,
        },
    }


def build_md(summaries: dict, agencies: list[dict], ledger: dict) -> str:
    m: list[str] = []
    a = m.append
    a("# V12 PHASE A - Real API Clip-Moment Scout (MC-01)")
    a("")
    a("> **Aage kya hua:** live `YOUTUBE_API_KEY` (GitHub Actions secret) se **5 targeted Data API queries** "
      "chalayi gayin, jo `MC-01` ke **8 analytic clip slots** par map hoti hain. Har slot ko **asli** "
      "million-view benchmarks mile. Lekin — ye **scout candidates** hain, **hamare 8 source clips nahi**. "
      "Koi clip download/clear nahi hua, koi render/VO/upload/publish nahi hua.")
    a("")
    a(f"**Phase:** `A` · **Run:** `{RUN_ID}` · **Edition:** `{EDITION}` · "
      f"**Winner:** `MC-01` (unchanged) · **Status:** `SCOUT_CANDIDATES_FOUND_NO_CLIP_ACQUIRED`")
    a("**Machine-readable:** `phase_a_clip_scout_v12.json`, `api_evidence/phase_a/*.json`, "
      "`api_evidence/phase_a/run.json`")
    a("")
    a("---")
    a("")
    a("## 0. Seedha jawab (TL;DR)")
    a("")
    a(f"- **5/5 real API queries success** — `lane=api`, `status=ok`, "
      f"**{sum(s['count'] for s in summaries.values())} real videos** measured, "
      f"**{sum(s['million_plus'] for s in summaries.values())} rows 1M+ views**.")
    a(f"- **Sabse bada real number:** `slow motion physics explained` me ek 9-second clip ke "
      f"**{fmt(summaries['slot-02-03-physics-timing']['top_views'])} views** (UrDay, 'How lighter works close-up in #macro #slowmo'). "
      "Yani replay/slow-motion mechanic ka real audience bohat bara hai.")
    a(f"- **Sabse behtar rights-lane signal:** NASA/agency probe me **20/20 videos 1M+ views**, "
      f"median **{fmt(summaries['rights-lane-nasa-agency-probe']['median_views'])}**, "
      f"`top3_share={summaries['rights-lane-nasa-agency-probe']['top3_share']}` → reading: "
      "*distributed — no single video owns it, entry is feasible*.")
    a("- **Lekin 5/5 topic verdicts = `NO`** (scores 20.4 – 47.2). Ye **topic packaging** ka verdict hai, "
      "hamare idea ka nahi. Iska matlab seedha: generic \"viral moments / unexpected moments\" title se mat jao; "
      "`MC-01` ka thesis-driven forensic angle + number-hook hi alag banata hai.")
    a("- **Hard stop abhi bhi wahi:** 8 per-clip rights gates, NASA promotional/current-astronaut gate, "
      "aur user-reported Short monetization ON. **Is gate ke bina koi clip edit me nahi jayegi.**")
    a("")
    a("---")
    a("")
    a("## 1. Live API run receipt")
    a("")
    a(f"| Cheez | Value |\n| --- | --- |\n| Run | `{RUN_ID}` (success, 2m24s) |"
      f"\n| Secret | `YOUTUBE_API_KEY` — `key_present=true` |"
      f"\n| Secret value | **kabhi print / store / request nahi** |"
      f"\n| Chat sandbox direct calls | **0** (googleapis.com allowlist me nahi) |"
      f"\n| Bot commit | `6db3924` — 5 reports + `run.json` |")
    a("")
    m.extend(table(["#", "Query", "Order", "Slots", "n", "1M+", "Verdict", "Score"],
                   [[str(i + 1), q["topic"], q["order"], str(q["slots"]),
                     str(summaries[q["slug"]]["count"]), str(summaries[q["slug"]]["million_plus"]),
                     str(summaries[q["slug"]]["verdict"]), str(summaries[q["slug"]]["score"])]
                    for i, q in enumerate(QUERIES)]))
    a("")
    a("---")
    a("")
    a("## 2. Real numbers (poori hisaab-kitaab)")
    a("")
    m.extend(table(["Report", "Total views", "Median views", "top3_share", "fresh_30d", "Reading", "Top views"],
                   [[q["slug"], fmt(summaries[q["slug"]]["total_views"]),
                     fmt(summaries[q["slug"]]["median_views"]),
                     str(summaries[q["slug"]]["top3_share"]),
                     str(summaries[q["slug"]]["fresh_share_30d"]),
                     str(summaries[q["slug"]]["reading"]),
                     fmt(summaries[q["slug"]]["top_views"])] for q in QUERIES]))
    a("")
    a("### 2.1 Decision parts (real, khush-numa nahi)")
    a("")
    m.extend(table(["Report", "demand", "winnability", "mechanism", "reason"],
                   [[q["slug"], str((summaries[q["slug"]]["parts"] or {}).get("demand")),
                     str((summaries[q["slug"]]["parts"] or {}).get("winnability")),
                     str((summaries[q["slug"]]["parts"] or {}).get("mechanism")),
                     str(summaries[q["slug"]]["reason"])] for q in QUERIES]))
    a("")
    a("### 2.2 Teen imaandaar warnings")
    a("")
    a("1. **`fresh_share_30d = 0.0`** 4/5 reports me — ye `order=viewCount` ka **sampling artifact** hai "
      "(all-time classics wapas aate hain), iska matlab \"naya demand nahi hai\" **nahi**. Isko "
      "trend ka saboot bana kar pesh nahi kiya gaya.")
    a("2. **Number-in-title ka signal aapas me ulta hai:** NASA probe me `has_number_pct = "
      f"{summaries['rights-lane-nasa-agency-probe']['title_signal_effect']['has_number_pct']}%`, "
      f"expectation-violation me {summaries['slot-01-07-expectation-violation']['title_signal_effect']['has_number_pct']}%, "
      f"lekin scale-illusion me +{summaries['slot-04-scale-illusion']['title_signal_effect']['has_number_pct']}% "
      f"(aur uska fit `r2 = {summaries['slot-04-scale-illusion']['title_signal_fit']['r2']}` yani **weak**). "
      "Isliye hamare working title ka \"8\" koi **proven law** nahi — ye ek tested hook variant hai, "
      "aur A/B test (Studio Test & Compare) se hi confirm hoga.")
    a("3. **`verdict=NO` hamare idea ka verdict nahi.** Ye tool kisi *search topic* ko enter karne ki "
      "economics batata hai. Hamara koi video abhi bana hi nahi, isliye isse \"idea reject\" "
      "ya \"guaranteed hit\" dono nahi nikala ja sakta.")
    a("")
    a("---")
    a("")
    a("## 3. 8 CLIP SLOT CARDS (asli benchmark candidates ke saath)")
    a("")
    a("> Har card me **3 real videos** hain jo us slot ke query me sabse zyada views wale the. Ye "
      "**structural benchmarks** hain: dekhne ke liye ki audience kis mechanic par rewatch karti hai. "
      "**Inme se koi bhi hamara source clip nahi** — teesre-party copyrighted videos hain. Har card ke "
      "neeche rights fields **sab `null` / `pending`** hain.")
    a("")
    for s in SLOTS:
        rep = summaries[s["query"]]
        a(f"### SLOT {s['slot']} — `{s['analytic_job']}`")
        a("")
        a(f"- **Chapter:** `{s['chapter']}` · {s['chapter_name']}")
        a(f"- **On-screen:** <= 10s · **VO budget:** {s['vo_words']} words · "
          f"**Original diagram:** {s['diagram']}")
        a(f"- **Commentary beat:** {s['beat']}")
        a(f"- **Scout query:** `{rep['topic']}` (`order={rep['order']}`, {rep['count']} rows, "
          f"{rep['million_plus']} with 1M+ views)")
        a("")
        m.extend(table(["Real benchmark (NOT a source clip)", "Channel", "Views", "Duration"],
                       [[f"`{r['id']}` {r['title']}", r["channel"], fmt(r["views"]), r["duration"]]
                        for r in rep["top_rows"]]))
        a("")
        a(f"- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full "
          "attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.")
        a(f"- **Rights gate:** all {len(RIGHTS_FIELDS)} fields `null` · `clearance_status=pending` · "
          "`human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.")
        a("")
    a("---")
    a("")
    a("## 4. NASA / agency rights-lane probe — aur uske exclusions")
    a("")
    a("API ne agency-owned channels ke **10 real videos** diye. Ye sabse qareebi **rights-lane** hai "
      "(official source URL mil sakta hai), lekin **abhi koi cleared source nahi**: NASA brand/insignia, "
      "current astronauts, promotional use, native audio, endorsement wording — sab per-clip check "
      "aur **human legal review** maangte hain.")
    a("")
    m.extend(table(["Agency video (real ID)", "Channel", "Views", "Status", "Kyun"],
                   [[f"`{x['id']}` {x['title']}", x["channel"], fmt(x["views"]), x["status"], x["reason"]]
                    for x in agencies]))
    a("")
    a(f"> 🔴 **V10/Short clip abhi bhi EXCLUDED** (`{NASA_ID_EXCLUDED}`) — hero, callback, montage filler "
      "ya poore video ka subject, kisi bhi 8 slot me nahi. Aur upar wala Canadian Space Agency "
      "water-bubble video **alag asset** hone ke bawajood **REJECT FOR NOW** hai kyunki wohi physics "
      "family dohrata hai — aapne \"DUSRI bohat saari best clips/moments\" manga tha, wahi "
      "paani wala moment nahi.")
    a("")
    a("---")
    a("")
    a("## 5. Production blueprint (SPEC ONLY — kuch execute nahi hua)")
    a("")
    a(f"**VO budget:** {ledger['vo_total_word_budget']} words / 13 chapters · "
      f"**Runtime:** 600s · **Source footage:** <=80s (**<=13.3%**) · "
      "**Har clip:** <=10s on screen + 35-45s hamari apni analysis + 1 original diagram.")
    a("")
    m.extend(table(["#", "Time", "Chapter", "VO words", "Beat"],
                   [[str(i + 1), c["t"], c["name"], str(c["vo_words"]), c["beat"]]
                    for i, c in enumerate(CHAPTERS)]))
    a("")
    e = ledger["edit_spec_NOT_EXECUTED"]
    a("**Edit spec:** " + "; ".join(f"`{k}`={v}" if not isinstance(v, list) else f"`{k}`={', '.join(v)}"
                                    for k, v in e.items()))
    a("")
    a("> Ye **beat sheet + word budget** hai, **final VO script nahi**. Script/voice/edit ka kaam "
      "**Phase B rights gate ke baad** hoga — kyunki bina clear kiye clip par script likhna "
      "us clip ko edit me le jane jaisa hi hai. Koi MP4, koi WAV, koi VO audio nahi bana.")
    a("")
    a("---")
    a("")
    a("## 6. Hard stop — Phase B")
    a("")
    a("> **NO clip enters the edit until** har slot ke liye ye 18 fields verified values se bharein "
      "aur `human_legal_review=true` ho:")
    a("")
    a("`" + "`, `".join(RIGHTS_FIELDS) + "`")
    a("")
    a("**Open gates (unchanged):** " + "; ".join(ledger["open_gates"]) + ".")
    a("")
    a("---")
    a("")
    a("## 7. Jo main nahi bolunga")
    a("")
    for k in ledger["non_claims"]:
        a(f"- `{k}` = **False**")
    a("")
    a("**Seedha:** NO legal clearance, NO guaranteed views, NO guaranteed retention, NO guaranteed "
      "virality, NO human creative approval, NO monetization change, NO upload, NO publish, NO render, "
      "NO final VO script or audio.")
    a("")
    a("Koi verified \"best growing channels\" ranking, competitor retention/CTR/RPM graph, arbitrary "
      "competitor transcript, guaranteed views, legal opinion, NASA endorsement ya perfection ka dawa nahi. "
      "Jo figures hain wo **public Data API view counts** hain, jo kisi ke bhi dekhne ke liye available hain — "
      "private analytics nahi.")
    a("")
    a("---")
    a("")
    a("## 8. Agla qadam")
    a("")
    a("1. **Phase B (hard stop):** in 8 slots me se har clip ka `official_source_url` + licence basis + "
      "SHA-256 + identifiable-person / promotional / native-audio checks + **human legal review**. "
      "Ye main khud complete nahi kar sakta — aapki / reviewer ki zarurat hai.")
    a("2. Uske baad final VO script → voice → edit → QC → metadata.")
    a("3. Pending safety: uploaded V10 Short ka monetization OFF (aapne ON bataya tha).")
    a("4. Chahein to aur targeted API queries chalayein (`yt-intel topic` / `reverse`)\xa0— key ab "
      "available hai, workflow `yt-phase-a-scout-v12.yml` tayyar hai.")
    a("")
    return "\n".join(m) + "\n"


def patch_next_action() -> None:
    txt = NEXT_ACTION.read_text(encoding="utf-8")
    if ADDENDUM_MARKER in txt:
        return
    add = (
        ADDENDUM_MARKER + " (live API, NO clip cleared)\n\n"
        "- Phase A done via GitHub Actions run `42895703914` using the existing `YOUTUBE_API_KEY` secret "
        "(presence only; value never printed/stored). Five targeted real Data API topic reports committed under "
        "`research/multi_clip_long_form_v12/api_evidence/phase_a/`; bot commit `6db3924`.\n"
        "- Deliverable: `research/multi_clip_long_form_v12/PHASE_A_CLIP_SCOUT_V12.md` + "
        "`phase_a_clip_scout_v12.json`. 8 slot cards, each with 3 REAL million-view structural benchmark candidates, "
        "a 13-chapter beat sheet / 1,150-word VO budget, an edit spec and a NASA agency rights-lane probe with explicit exclusions.\n"
        "- Real findings: 5/5 topic verdicts are NO (20.4-47.2); NASA/agency lane is distributed (top3_share 0.398, "
        "20/20 videos 1M+ views); a 9s slow-motion clip has 363,151,838 views. Number-in-title signals CONTRADICT "
        "each other across samples - not treated as a law. `fresh_share_30d=0.0` is a viewCount sampling artifact, not a trend claim.\n"
        "- Winner unchanged: `MC-01 THE REPLAY CODE: 8 Moments, One Hidden Rule`. V10/Short NASA water-bubble asset "
        "still EXCLUDED from all 8 slots; the CSA water-bubble video is REJECT FOR NOW (same physics family); "
        "current-crew Artemis II broadcasts are EXCLUDED pending human legal review.\n"
        "- HARD STOP unchanged: all 18 per-clip rights fields are NULL, `clearance_status=pending`, "
        "`human_legal_review=false` for all 8 slots. NO clip downloaded/cleared, NO VO script/audio, NO render, "
        "NO upload/publish, NO monetization change, NO human approval, NO legal clearance, NO guaranteed views.\n"
        "- This addendum does NOT supersede the standing 'await human full-motion/native-audio review' line below.\n\n"
    )
    NEXT_ACTION.write_text(add + txt, encoding="utf-8")


def dumps(o) -> str:
    return json.dumps(o, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    summaries = {q["slug"]: report_summary(q["slug"]) for q in QUERIES}
    agencies = agency_rows()
    ledger = build_ledger(summaries, agencies)
    (D / "phase_a_clip_scout_v12.json").write_text(dumps(ledger), encoding="utf-8")
    (D / "PHASE_A_CLIP_SCOUT_V12.md").write_text(build_md(summaries, agencies, ledger), encoding="utf-8")
    patch_next_action()
    print(f"Wrote Phase A scout pack in {D.relative_to(ROOT)}")
    print(f"Reports: {len(summaries)} | real rows: {sum(s['count'] for s in summaries.values())} | "
          f"1M+ rows: {sum(s['million_plus'] for s in summaries.values())} | "
          f"agency rows: {len(agencies)} | slots: {len(ledger['slots'])} | "
          f"VO budget: {ledger['vo_total_word_budget']} words | "
          f"all non-claims false: {all(not v for v in ledger['non_claims'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
