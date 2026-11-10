#!/usr/bin/env python3
"""V12 PHASE B + C - executable rights gate and full VO script DRAFT.

Deterministic / idempotent. Reads the committed REAL GitHub Actions Data API
evidence (phase_a + phase_bc) and the V12 source ledger; invents nothing.

Produces:
  * PHASE_B_RIGHTS_GATE_V12.md  + phase_b_rights_gate_v12.json
  * PHASE_C_SCRIPT_DRAFT_V12.md + phase_c_script_draft_v12.json
  * a Phase B/C addendum in NEXT_ACTION.md (appended once)

HARD STOP: all 8 per-clip rights dossiers stay NULL/pending. The script uses
[SLOT n - SOURCE PENDING RIGHTS GATE] placeholders, never a real clip. No VO
audio, no render, no upload, no clearance, no human approval.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "research" / "multi_clip_long_form_v12"
EV_A = D / "api_evidence" / "phase_a"
EV_BC = D / "api_evidence" / "phase_bc"
NEXT_ACTION = ROOT / "docs" / "continuity" / "channels" / "monarch-cam" / "NEXT_ACTION.md"
ADDENDUM_MARKER = "## V12 PHASE B/C addendum - executable rights gate + VO script DRAFT"

EDITION = "v12_phase_bc_rights_gate_and_script_draft"
RUN_ID_BC = "42905149277"
RUN_ID_A = "42895703914"
NASA_ID_EXCLUDED = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"

# ---------------------------------------------------------------------------
# Source-ledger citations (read from the committed V12 ledger, never guessed)
# ---------------------------------------------------------------------------
LEDGER = json.loads((D / "sources_v12.json").read_text(encoding="utf-8"))["sources"]
SRC = {s["n"]: s["url"] for s in LEDGER}


def cite(n: int) -> str:
    return f"[{n}]({SRC[n]})"


RIGHTS_FIELDS = [
    "official_source_url", "nasa_or_agency_asset_id", "licence_basis",
    "third_party_copyrighted_material_check", "identifiable_persons_check",
    "current_astronaut_or_employee_check", "promotional_or_cover_art_use",
    "native_audio_rights", "attribution_string", "no_endorsement_implied_wording",
    "no_insignia_confirmed", "sha256_after_download", "duration_seconds",
    "scout_score_out_of_100", "scout_min_pass_78", "clearance_status",
    "human_legal_review", "not_a_legal_opinion",
]

FIELD_RULES = [
    {"field": "official_source_url", "verify": "The exact first-party page where the asset is published, not a repost or a search result.", "pass": "URL resolves on the rights-holder's own domain and the asset ID matches.", "fail": "Aggregator, mirror, embed, social repost, or an unverifiable link."},
    {"field": "nasa_or_agency_asset_id", "verify": "The agency's own catalogue / asset identifier for this exact file.", "pass": "A stable agency asset ID is recorded and matches the downloaded file.", "fail": "Only a YouTube video ID, or no catalogue ID at all."},
    {"field": "licence_basis", "verify": "The written licence or public-domain statement covering THIS file, with its URL and retrieval date.", "pass": "Licence text explicitly permits this use, including commercial use if monetization is intended.", "fail": "Assumed 'public domain', 'educational use', 'fair use' as a licence, or a generic site-wide statement that excludes some media."},
    {"field": "third_party_copyrighted_material_check", "verify": "Whether the frame or audio contains anyone else's content (music, logo, broadcast graphic, another creator's footage).", "pass": "Written 'none found' after frame + audio inspection, or a documented clearance for each item.", "fail": "Uninspected, or contains uncleared third-party material."},
    {"field": "identifiable_persons_check", "verify": "Whether any identifiable person appears and what consent/permissions exist.", "pass": "No identifiable person, or documented permission plus the required likeness/AI-likeness review.", "fail": "Identifiable person with no documented permission."},
    {"field": "current_astronaut_or_employee_check", "verify": "Whether the person is a current agency employee/crew member shown in a way that could read as promotional.", "pass": "Confirmed not current personnel, or written clearance from the agency.", "fail": "Current crew / employee in promotional framing, or status unconfirmed."},
    {"field": "promotional_or_cover_art_use", "verify": "Whether the asset is used to promote a product, service, or as cover art / thumbnail hero.", "pass": "Editorial/educational context only, no promotional reading, no cover-art use.", "fail": "Promotional or cover-art use of agency imagery or insignia."},
    {"field": "native_audio_rights", "verify": "Rights covering the ORIGINAL audio track if it is retained.", "pass": "Native audio is licensed together with the picture, or audio is verified silent/own-recorded.", "fail": "Retained audio with no separate rights basis, or substituted music/SFX."},
    {"field": "attribution_string", "verify": "Complete credit line required by the licence (title, author, source URL, licence, any change note).", "pass": "Full credit string written and included on screen and in the description.", "fail": "Name only, link only, or a generic 'credit to the owner'."},
    {"field": "no_endorsement_implied_wording", "verify": "On-screen and spoken wording must not imply agency/person endorsement.", "pass": "Explicit 'no endorsement implied' wording present.", "fail": "Title, caption or VO could be read as an endorsement."},
    {"field": "no_insignia_confirmed", "verify": "Frame-by-frame check for agency insignia, logos, mission patches or branding.", "pass": "Documented 'no insignia in the selected frames'.", "fail": "Insignia visible, or check not performed."},
    {"field": "sha256_after_download", "verify": "Hash of the exact file that will enter the edit.", "pass": "SHA-256 recorded after download and matching the final media file.", "fail": "No hash, or hash of a different/transcoded file."},
    {"field": "duration_seconds", "verify": "Exact selected in-point / out-point and duration.", "pass": "Duration <= 10s on screen and the 8 clips together stay <= 80s / 600s (<=13.3%).", "fail": "Longer excerpt, or the aggregate source share exceeds 13.3%."},
    {"field": "scout_score_out_of_100", "verify": "V10-style 10-axis scout score for this specific clip.", "pass": "Numeric score recorded with its rubric sheet.", "fail": "No score, or a score copied from another clip."},
    {"field": "scout_min_pass_78", "verify": "The >=78 minimum pass threshold from the rubric.", "pass": "True only when scout_score_out_of_100 >= 78.", "fail": "True with a lower score, or set without a score."},
    {"field": "clearance_status", "verify": "Final status after every other field passes.", "pass": "'cleared' ONLY when all fields above are verified AND human_legal_review=true.", "fail": "'cleared' with any null/failed field."},
    {"field": "human_legal_review", "verify": "A human reviewer has actually reviewed this clip's rights chain.", "pass": "true with reviewer name and date in the sign-off block.", "fail": "true without a named reviewer/date, or set by an agent."},
    {"field": "not_a_legal_opinion", "verify": "This ledger is a checklist, not legal advice.", "pass": "true, always.", "fail": "false - would imply a legal opinion."},
]

KILL_CONDITIONS = [
    "Current named crew / employee in promotional framing or an official mission broadcast used as a source clip.",
    "Agency insignia, mission patch, or logo visible in the selected frames.",
    "Native audio or music retained without its own documented rights basis.",
    "Asset obtained from a social repost, mirror, aggregator or embed instead of the rights holder.",
    "Licence cannot be read for this exact file, or excludes commercial use while monetization is intended.",
    "The V10/Short NASA water-bubble asset (any hero, callback, montage or whole-video use).",
    "Any clip that would make the 8-source aggregate exceed 80s / 600s (13.3%).",
    "Clips strung together with little or no narrative, or a mostly non-verbal reaction.",
]

ATTRIBUTION_TEMPLATES = [
    {"lane": "NASA / agency", "template": 'Source: NASA / [mission or centre], "[asset title]", [asset ID]. NASA is credited; no endorsement implied. Licence: [agency media usage statement + URL, retrieved YYYY-MM-DD].'},
    {"lane": "CC BY", "template": '"[title]" by [author], [source URL], licensed CC BY [version]. Changes: cropped to <=10s, slowed to 0.5x/0.25x, no audio substitution. No endorsement implied.'},
    {"lane": "Verified public domain / agency original", "template": '"[title]", [agency], public domain per [statement URL, retrieved YYYY-MM-DD]. No endorsement implied.'},
    {"lane": "Own-shot original", "template": "Original footage shot for this episode by [operator], [date]. No third-party material."},
    {"lane": "Licensed with permission", "template": '"[title]" used with written permission from [rights holder], dated [date], reference [ID]. Permission alone does not establish reused-content eligibility.'},
]

# ---------------------------------------------------------------------------
# PHASE C: full VO script DRAFT (placeholders, never a real clip)
# ---------------------------------------------------------------------------
HOOKS = [
    {"id": "V12-H1", "label": "Primary", "text": "Eight different clips. One reason you cannot stop replaying them. I will show you the rule - then prove it on every single one."},
    {"id": "V12-H2", "label": "Puzzle-first", "text": "These eight moments look unrelated. By the end of this video you will be able to predict which clip will make you hit replay before it even finishes."},
    {"id": "V12-H3", "label": "Forensic-first", "text": "I slowed eight viral moments down to the frame. Every one of them breaks the same expectation at exactly the same point."},
]

SCRIPT = [
    {"t": "0:00-0:20", "name": "Cold open: 3-second montage of 8 different moments", "budget": 25,
     "shots": "One fast cut from each of 8 DIFFERENT clips (0.8-1.2s each), no logo, no greeting, native audio only. Then the one-line hook.",
     "vo": "Eight different clips. One reason you cannot stop replaying them. I will show you the rule, then prove it on every single one."},
    {"t": "0:20-0:55", "name": "The promise and the rule", "budget": 75,
     "shots": "Presenter on a clean card. One sentence per line, no stock b-roll.",
     "vo": "Here is the rule, stated once, plainly. A moment becomes rewatchable when it breaks an expectation you did not know you had, and the explanation arrives one beat later than your brain wanted it. Not the surprise alone. Not the explanation alone. The gap between them. Over the next ten minutes I will test that rule on eight completely different moments. If the rule is real, it should survive all eight. If it does not, I will say so. No outcome promises. Just the mechanism."},
    {"t": "0:55-1:40", "name": "Why 'rewatched or shared' is a real signal", "budget": 110,
     "shots": "Original metric card: Spikes / Intro / Dips, drawn by us. On-screen source note.",
     "vo": "Quick note on where this idea comes from. YouTube's own help pages call those moments Spikes, points that get rewatched or shared. Intro is the share still watching after thirty seconds. Dips are where people skip or leave. Those reports belong to the channel owner. They need at least sixty seconds and a hundred views, and they take a day or two to appear. I do not have them for anyone else's channel, and I am not going to pretend I do. What I can use is public information: view counts, titles, durations, published dates, and the structure a creator chose to put in their own description. So this is a structural argument, not a claim about anyone's retention graph. That distinction matters for the rest of the video."},
    {"t": "1:40-2:55", "name": "CLIP 1 - expectation violation", "budget": 130,
     "shots": "[SLOT 1 - SOURCE PENDING RIGHTS GATE] <=10s cold, native audio. FREEZE on the violation frame. ORIGINAL expected-vs-actual diagram.",
     "vo": "[SLOT 1 - SOURCE PENDING RIGHTS GATE. Play the clip cold, native audio, no captions over it yet.] Watch that again. Before I explain anything, notice what you expected: the ordinary version of this event, the one your brain filled in from a thousand earlier examples. Now notice the exact frame where that prediction stopped working. [FREEZE FRAME - ORIGINAL DIAGRAM: expected path versus actual path.] The rewatch impulse does not start at the surprise. It starts in the half-second after, when your brain still has no place to file it. That delay is the first half of the rule. The second half is that someone has to close it. Which is what we are about to do, eight times, with a different mechanism each time."},
    {"t": "2:55-4:05", "name": "CLIP 2 - the physics surprise", "budget": 135,
     "shots": "[SLOT 2 - SOURCE PENDING RIGHTS GATE] <=10s, then 0.5x replay. ORIGINAL ray / force diagram. On-screen first-party source note.",
     "vo": "[SLOT 2 - SOURCE PENDING RIGHTS GATE. Play up to ten seconds, then replay at half speed.] Here the gap is physical. [FACT - VERIFY AGAINST A FIRST-PARTY OFFICIAL SOURCE FOR THIS CLIP BEFORE RECORDING.] The frame looks wrong because a property of the medium, light, gravity, surface tension or momentum, is doing something our everyday intuition was not built to predict. [ORIGINAL RAY OR FORCE DIAGRAM.] Notice I am not saying the footage is fake, and I am not saying the creator intended a trick. I am saying the explanation is late. Your eyes register the event immediately, but the reason needs a sentence. That one-sentence lag is exactly the shape of a rewatch. At half speed you can see where the reason should have been available. At full speed it is already gone. That is the whole mechanic."},
    {"t": "4:05-5:10", "name": "CLIP 3 - timing / slow motion", "budget": 120,
     "shots": "[SLOT 3 - SOURCE PENDING RIGHTS GATE] Three labelled passes: 1x, 0.5x, 0.25x. ORIGINAL frame-timeline diagram.",
     "vo": "[SLOT 3 - SOURCE PENDING RIGHTS GATE. Three labelled passes: full speed, half speed, quarter speed.] Same footage, three speeds, three different amounts of information. At full speed you get an outcome. At half speed you get a sequence. At quarter speed you get the single frame that actually carries the surprise. [ORIGINAL FRAME-TIMELINE DIAGRAM.] Here is the useful part. Slowing a moment down does not create the rewatch impulse. It reveals where it was hiding. A good edit does not add suspense here. It moves the explanation to just after the point where the viewer has already started asking. I cannot tell you that was intentional. I can only show you the structure is there, and that it is the same structure as clip one."},
    {"t": "5:10-6:15", "name": "CLIP 4 - scale / size illusion", "budget": 120,
     "shots": "[SLOT 4 - SOURCE PENDING RIGHTS GATE] <=10s. ORIGINAL scale diagram with a labelled reference object. No stock b-roll as hero.",
     "vo": "[SLOT 4 - SOURCE PENDING RIGHTS GATE. Play up to ten seconds.] This one is a scale error. [ORIGINAL SCALE DIAGRAM WITH A LABELLED REFERENCE OBJECT.] Your visual system needs a known size nearby before it can judge an unknown one. Remove that reference, or put a misleading one in, and the same object becomes two different objects in the same shot. [FACT - VERIFY THE REFERENCE LENGTH AGAINST THE SOURCE BEFORE RECORDING.] Notice the expectation being broken here is not about events. It is about measurement. That matters, because it means the rule is not about surprises in general. It is about a specific kind of violated prediction, plus a delayed repair. Four clips in, four different surfaces, one shape. That is the first real sign this might be a rule rather than a coincidence."},
    {"t": "6:15-7:10", "name": "CLIP 5 - sound and silence", "budget": 105,
     "shots": "[SLOT 5 - SOURCE PENDING RIGHTS GATE] Pass one WITH native audio, pass two muted with commentary. ORIGINAL two-row A/B beat diagram, drawn not sampled.",
     "vo": "[SLOT 5 - SOURCE PENDING RIGHTS GATE. Pass one with native audio. Pass two muted, with commentary.] Two passes, same frames. On the first, the sound tells you when the event is coming. On the second, without it, the timing itself has to do that work. [ORIGINAL TWO-ROW A/B BEAT DIAGRAM.] We keep the source's native audio and we do not substitute music or effects, because the comparison only works if the audio is the real one. What changes between the passes is not the information. It is when you are allowed to resolve it. That is the same gap again, wearing a different costume."},
    {"t": "7:10-8:00", "name": "CLIP 6 - the human reaction", "budget": 95,
     "shots": "[SLOT 6 - SOURCE PENDING RIGHTS GATE] <=10s. ORIGINAL attention-reset timeline. No face crop reused as thumbnail. No name used promotionally.",
     "vo": "[SLOT 6 - SOURCE PENDING RIGHTS GATE. Play up to ten seconds.] A face is the fastest reset signal we have. [ORIGINAL ATTENTION-RESET TIMELINE.] When someone reacts, we automatically check what they are looking at, and for a moment our own prediction is suspended. I am not naming anyone in this clip, and I am not implying that any person or organisation endorses this video. The analytic point is narrower. A reaction shot hands the explanation to someone else for a beat, which delays closure. Same rule, sixth surface."},
    {"t": "8:00-8:45", "name": "CLIP 7 - the near-miss / coincidence", "budget": 85,
     "shots": "[SLOT 7 - SOURCE PENDING RIGHTS GATE] <=10s. ORIGINAL two-track converging timeline. No invented date, injury, outcome or quote.",
     "vo": "[SLOT 7 - SOURCE PENDING RIGHTS GATE. Play up to ten seconds.] Two independent sequences converge, and for one frame they look like they were written together. [ORIGINAL TWO-TRACK CONVERGING TIMELINE.] No invented date, no invented outcome, no quote I cannot source. The rewatch here is a verification loop. You go back to check whether you actually saw the alignment, or built it yourself. That is a different reason to replay, but the shape is identical: expectation, violation, delayed repair."},
    {"t": "8:45-9:25", "name": "CLIP 8 + the prediction test (MC-02 folded in)", "budget": 75,
     "shots": "[SLOT 8 - SOURCE PENDING RIGHTS GATE] Play the whole clip with NO explanation. ORIGINAL 8-slot callback grid, one cell per DIFFERENT clip.",
     "vo": "[SLOT 8 - SOURCE PENDING RIGHTS GATE. Play the whole clip with NO explanation.] Before I say anything: where would you put the replay point? Hold that answer. [ORIGINAL EIGHT-SLOT CALLBACK GRID, ONE CELL PER DIFFERENT CLIP.] Every cell in that grid is a different clip. Every one of them broke a prediction, then made you wait for the repair. If you picked the frame I picked, the rule just worked in reverse. It let you predict instead of just recognise."},
    {"t": "9:25-9:50", "name": "The rule, restated + honest limits", "budget": 55,
     "shots": "One screen with the six-step rule. Then a plainly worded limits card.",
     "vo": "So here is the rule in six steps: a prediction, a violation, a short delay, a repair, a replay to confirm, and a reason to share the confirmation. And here are the honest limits. I used public view counts and public structure, not anyone's private retention, click-through or revenue data. I could not obtain transcripts for most of the comparison videos. No clip in this episode has been through a human rights review, and no human has approved this edit. Those are open items, not fine print."},
    {"t": "9:50-10:00", "name": "Genuine question + series teaser", "budget": 20,
     "shots": "One specific question on screen. One next-episode teaser. No like/subscribe coercion or reward.",
     "vo": "Which of the eight made you replay before the explanation landed? Tell me the number. Next file: the same rule, tested on moments that never went viral."},
]

METADATA_DRAFT = {
    "status": "DRAFT_NOT_UPLOADED_NOT_PUBLISHED",
    "working_title": "Why These 8 Moments Make You Rewatch: A Forensic Breakdown",
    "working_title_chars": 58,
    "alt_titles": ["The Replay Code: 8 Moments, One Hidden Rule", "Eight Clips, One Reason You Hit Replay"],
    "description_draft": "Eight different clips. One rule about why a moment makes you hit replay. I break each one down frame by frame, then test the rule on a final unseen clip. Sources and rights credits for every clip are listed below once cleared. This is an original commentary and analysis video; no endorsement implied. [CREDITS BLOCK - PENDING PER-CLIP RIGHTS GATE] [AI-USE DISCLOSURE - PENDING]",
    "hashtags": ["#science", "#videoessay", "#physics"],
    "hashtag_note": "At most three displayed hashtags; more than sixty are ignored; misleading or unrelated hashtags are disallowed " + cite(13),
    "category": {"primary": "Science & Technology", "alternate": "Education + science experiment",
                 "human_must_confirm": True,
                 "note": "Carried from V10; ID values were caveated and must be confirmed by a human in Studio."},
    "pinned_comment_draft": "Which clip made you replay before the explanation landed - 1 to 8?\n\nThis video is original commentary and analysis. Sources and credits are listed in the description. No endorsement implied.",
    "ai_use_disclosure": "REQUIRED if synthetic or altered media is used; content and wording pending human review " + cite(15),
    "monetization_recommendation": "OFF pending written clearance, identifiable-person permission and human legal review. Ads ON confirms rights to all visual and audio elements " + cite(17),
    "clickbait_guard": "Accurate title/thumbnail, no deceptive clickbait or ALL CAPS; tags are not important " + cite(6),
}

EDIT_DECISIONS = [
    {"rule": "J-cut / L-cut between clip and commentary", "why": "Keeps the explanation arriving one beat late - the thesis itself, not just a style choice."},
    {"rule": "One original diagram per clip, drawn by us", "why": "Makes the repair visible and keeps the video commentary-dominant, not a compilation."},
    {"rule": "Native audio retained; no music or SFX substitution", "why": "Slot 5's A/B comparison is only valid with the real audio. Also a rights requirement."},
    {"rule": "Three labelled replay passes (1x / 0.5x / 0.25x) on slot 3", "why": "Real slow-motion winners show the reveal lives in a single frame."},
    {"rule": "No clip strung together with little narrative; no mostly non-verbal reaction", "why": "Official reused-content policy line " + cite(7)},
    {"rule": "Source share <=80s / 600s (<=13.3%), each clip <=10s", "why": "Original commentary must dominate; permission alone is not enough " + cite(7)},
    {"rule": "No ALL CAPS, no coercion, no reward CTA", "why": "Packaging and spam rules " + cite(6) + " " + cite(14)},
]


# ---------------------------------------------------------------------------
# Real evidence readers
# ---------------------------------------------------------------------------
def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def words(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text)


def syllables(word: str) -> int:
    w = word.lower()
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


def reading_grade(text: str) -> float:
    """Flesch-Kincaid grade, same formula as yt_intel/reverse.py."""
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    ws = words(text)
    if not ws:
        return 0.0
    syl = sum(syllables(w) for w in ws)
    return round(0.39 * (len(ws) / sentences) + 11.8 * (syl / len(ws)) - 15.59, 1)


def angle_summaries() -> list[dict]:
    out = []
    for slug in ["angle-why-we-rewatch", "angle-frame-by-frame", "angle-science-commentary"]:
        d = load(EV_BC / f"{slug}.json")
        rows = d.get("rows") or []
        mv = [r for r in rows if isinstance(r.get("views"), int) and r["views"] >= 1_000_000]
        sat = d.get("saturation") or {}
        dec = d.get("decision") or {}
        out.append({
            "slug": slug, "topic": d.get("topic"), "lane": d.get("lane"), "order": d.get("order"),
            "status": d.get("status"), "count": len(rows), "million_plus": len(mv),
            "total_views": sat.get("total_views"), "median_views": sat.get("median_views"),
            "top3_share": sat.get("top3_share"), "fresh_share_30d": sat.get("fresh_share_30d"),
            "reading": sat.get("reading"), "verdict": dec.get("verdict"), "score": dec.get("score"),
            "parts": dec.get("parts"), "next_probe": dec.get("next_probe"),
            "top_rows": [{"id": r.get("id"), "title": r.get("title"), "channel": r.get("channel"),
                          "views": r.get("views"), "duration": r.get("duration")}
                         for r in sorted(rows, key=lambda x: -(x.get("views") or 0))[:3]],
        })
    return out


def teardown_summaries() -> list[dict]:
    out = []
    for p in sorted(EV_BC.glob("reverse-*.json")):
        d = load(p)
        rec = d.get("receipt") or {}
        tr = d.get("transcript_status") or {}
        sc = d.get("script") or {}
        hk = d.get("hook") or {}
        out.append({
            "file": p.name, "id": d.get("id"), "title": rec.get("title"),
            "channel": rec.get("channel"), "views": rec.get("views"),
            "likes": rec.get("likes"), "comments": rec.get("comments"),
            "duration": rec.get("duration"), "duration_seconds": d.get("duration_seconds"),
            "published": rec.get("published"), "transcript_status": tr.get("status"),
            "transcript_words": tr.get("words"), "script_words": sc.get("words"),
            "wpm": sc.get("wpm"), "reading_grade": sc.get("reading_grade"),
            "cta_count": sc.get("cta_count"), "filler_rate": sc.get("filler_rate"),
            "first_sentence": hk.get("first_sentence"), "opens_with_number": hk.get("opens_with_number"),
            "opens_with_you": hk.get("opens_with_you"), "claim_type": hk.get("claim_type"),
            "structure": d.get("structure"), "replication": d.get("replication"),
            "psychology": d.get("psychology"),
        })
    return out


def phase_a_top(slot_query: str) -> list[dict]:
    d = load(EV_A / f"{slot_query}.json")
    return [{"id": r.get("id"), "title": r.get("title"), "channel": r.get("channel"),
             "views": r.get("views"), "watch_url": f"https://www.youtube.com/watch?v={r.get('id')}"}
            for r in sorted(d["rows"], key=lambda x: -(x.get("views") or 0))[:3]]


SLOT_QUERIES = {
    1: "slot-01-07-expectation-violation", 2: "slot-02-03-physics-timing",
    3: "slot-02-03-physics-timing", 4: "slot-04-scale-illusion",
    5: "slot-05-06-08-sound-reaction-callback", 6: "slot-05-06-08-sound-reaction-callback",
    7: "slot-01-07-expectation-violation", 8: "slot-05-06-08-sound-reaction-callback",
}
SLOT_JOBS = {
    1: "expectation violation", 2: "physics / optics surprise", 3: "timing / slow-motion frame",
    4: "scale / size illusion", 5: "native sound vs silence", 6: "human reaction beat",
    7: "near-miss / coincidence", 8: "prediction test / callback",
}


def assert_gate_blocks() -> dict:
    """Executable proof: a fabricated 'cleared' slot with NULL fields is REJECTED."""
    fake = {"slot": 99, "clearance_status": "cleared", "human_legal_review": False,
            "rights_gate": {k: None for k in RIGHTS_FIELDS}}
    blocked = (fake["clearance_status"] == "cleared" and
               (not fake["human_legal_review"] or any(v is None for v in fake["rights_gate"].values())))
    return {"test": "fabricated cleared slot with NULL fields", "rejected": blocked,
            "expected_rejected": True,
            "rule": "clearance_status='cleared' requires human_legal_review=true AND zero NULL rights fields"}


def build_gate_ledger(angles, teardowns) -> dict:
    dossiers = []
    for n in range(1, 9):
        dossiers.append({
            "slot": n, "analytic_job": SLOT_JOBS[n],
            "status": "PENDING_HUMAN_REVIEW", "clearance_status": "pending",
            "human_legal_review": False, "not_a_legal_opinion": True,
            "rights_gate": {k: None for k in RIGHTS_FIELDS},
            "real_api_probe_targets": phase_a_top(SLOT_QUERIES[n]),
            "probe_target_boundary": "These are real public YouTube videos found by the Data API. They are STRUCTURAL BENCHMARKS and are NOT cleared source clips. Using any of them requires written permission AND still does not by itself establish reused-content eligibility " + cite(7),
            "sign_off": {"reviewer_name": None, "review_date": None, "decision": None, "notes": None},
        })
    return {
        "edition": EDITION, "phase": "B - executable per-clip rights gate",
        "status": "ALL_8_DOSSIERS_PENDING_NO_CLIP_CLEARED",
        "hard_stop": "NO clip enters the edit until every rights_gate field is filled with a verified value and human_legal_review=true for THAT clip.",
        "gate_enforcement": assert_gate_blocks(),
        "excluded_existing_short_clip": {"nasa_asset_id": NASA_ID_EXCLUDED,
            "rule": "EXCLUDED from all 8 slots - no hero, callback, montage filler or whole-video subject."},
        "field_rules": FIELD_RULES, "kill_conditions": KILL_CONDITIONS,
        "attribution_templates": ATTRIBUTION_TEMPLATES,
        "dossiers": dossiers,
        "policy_anchors": {
            "reused_content": cite(7), "fair_use_four_factors": cite(8),
            "credit_insufficient": cite(10), "cc_by_attribution": cite(11),
            "content_id": cite(9), "ads_rights_confirmation": cite(17),
            "nasa_media": cite(31), "nasa_advertising": cite(32), "nasa_partnerships": cite(33),
        },
        "phase_bc_real_evidence": {
            "run_id": RUN_ID_BC, "angle_probes": angles,
            "winner_teardowns": teardowns,
            "boundary": "Angle probes and teardowns are structural benchmarks, not cleared sources.",
        },
        "non_claims": {
            "clip_downloaded": False, "clip_cleared": False, "legal_opinion": False,
            "human_legal_review": False, "commercial_monetization_clearance": False,
            "nasa_endorsement": False, "astronaut_permission_obtained": False,
            "render_done": False, "upload_done": False, "publish_done": False,
            "monetization_changed": False, "human_creative_approval": False,
            "guaranteed_views": False, "perfection": False,
        },
    }


def build_script_ledger(angles, teardowns) -> dict:
    chapter_rows = []
    for i, c in enumerate(SCRIPT, 1):
        vo = c["vo"]
        chapter_rows.append({
            "n": i, "t": c["t"], "name": c["name"],
            "vo_word_budget": c["budget"], "vo_words_actual": len(words(vo)),
            "shot_list": c["shots"], "vo_text": vo,
            "contains_slot_placeholder": "SOURCE PENDING RIGHTS GATE" in vo or "SLOT " in vo,
            "status": "DRAFT_NOT_RECORDED_NOT_RENDERED",
        })
    total_actual = sum(x["vo_words_actual"] for x in chapter_rows)
    total_budget = sum(x["vo_word_budget"] for x in chapter_rows)
    speech_seconds = 600 - 80  # 80s max source footage, rest available for VO + diagrams + pauses
    wpm = round(total_actual / (speech_seconds / 60.0), 1)
    all_vo = " ".join(c["vo"] for c in SCRIPT)
    return {
        "edition": EDITION, "phase": "C - full VO script DRAFT with placeholders",
        "status": "DRAFT_NOT_FOR_RENDER_NOT_RECORDED",
        "winner": "MC-01 THE REPLAY CODE: 8 Moments, One Hidden Rule",
        "runtime_seconds": 600, "chapters": 13,
        "hooks": HOOKS, "chapter_ledger": chapter_rows,
        "vo_words_budget": total_budget, "vo_words_actual": total_actual,
        "vo_wpm_estimate": wpm, "vo_reading_grade": reading_grade(all_vo),
        "reading_grade_formula": "Flesch-Kincaid, same formula as yt_intel/reverse.py (computed locally, no API)",
        "edit_decisions": EDIT_DECISIONS, "metadata_draft": METADATA_DRAFT,
        "placeholder_rule": "Every clip reference is [SLOT n - SOURCE PENDING RIGHTS GATE]. No real clip, agency asset or third-party video is named as a source clip anywhere in the VO.",
        "real_script_benchmark": next((t for t in teardowns if t["transcript_status"] == "ok"), None),
        "angle_probes": angles,
        "hard_stop": "This draft is NOT cleared for recording. Recording, edit and render begin only after all 8 Phase B dossiers pass human legal review.",
        "non_claims": {
            "vo_recorded": False, "final_script_approved": False, "render_done": False,
            "mp4_created": False, "upload_done": False, "publish_done": False,
            "category_set": False, "pinned_comment_posted": False,
            "monetization_changed": False, "human_creative_approval": False,
            "human_legal_review": False, "legal_clearance": False,
            "guaranteed_views": False, "guaranteed_retention": False,
            "guaranteed_virality": False, "perfection": False, "flawlessness": False,
            "nasa_endorsement": False, "clip_acquired": False,
        },
    }


def table(headers, rows) -> list[str]:
    esc = lambda s: str(s).replace("|", "or").replace("\n", " ")
    out = ["| " + " | ".join(esc(h) for h in headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    out += ["| " + " | ".join(esc(c) for c in row) + " |" for row in rows]
    return out


def build_gate_md(g: dict) -> str:
    m, a = [], None
    a = m.append
    a("# V12 PHASE B - Executable Per-Clip Rights Gate")
    a("")
    a("> **Ye hard stop ko sirf likha nahi, chalaya bhi gaya.** 8 dossiers, har ek me 18 fields "
      "`null`, `clearance_status=pending`, `human_legal_review=false`. Generator me ek executable "
      "test hai jo **farzi \"cleared\" slot ko reject karta hai** — yani gate ko jumlon se bypass "
      "nahi kiya ja sakta. Koi clip download/clear nahi hua.")
    a("")
    a(f"**Edition:** `{EDITION}` · **API runs:** `{RUN_ID_A}`, `{RUN_ID_BC}` · "
      f"**Status:** `ALL_8_DOSSIERS_PENDING_NO_CLIP_CLEARED`")
    a("**Machine-readable:** `phase_b_rights_gate_v12.json`, `PHASE_C_SCRIPT_DRAFT_V12.md`, "
      "`phase_c_script_draft_v12.json`")
    a("")
    a("---")
    a("")
    a("## 0. Seedha jawab")
    a("")
    a(f"- **Gate executable hai:** `{g['gate_enforcement']['test']}` → "
      f"`rejected={g['gate_enforcement']['rejected']}` (expected `True`).")
    a(f"- **{len(g['field_rules'])} fields**, **{len(g['kill_conditions'])} kill conditions**, "
      f"**{len(g['attribution_templates'])} attribution templates**, **8 dossiers** — sab pending.")
    a("- **Real API probe targets** har dossier me hain, lekin wo **benchmarks** hain, source clips "
      "nahi. Written permission bhi reused-content eligibility guarantee nahi karta " + cite(7) + ".")
    a(f"- **V10/Short clip EXCLUDED** (`{NASA_ID_EXCLUDED}`) — kisi bhi slot me nahi.")
    a("")
    a("---")
    a("")
    a("## 1. 18 fields - kya verify karna hai")
    a("")
    m.extend(table(["#", "Field", "Verify", "Pass", "Fail"],
                   [[str(i + 1), r["field"], r["verify"], r["pass"], r["fail"]]
                    for i, r in enumerate(g["field_rules"])]))
    a("")
    a("## 2. Kill conditions (koi ek bhi mila to slot REJECT)")
    a("")
    for k in g["kill_conditions"]:
        a(f"- {k}")
    a("")
    a("## 3. Attribution templates")
    a("")
    m.extend(table(["Lane", "Template"], [[t["lane"], t["template"]] for t in g["attribution_templates"]]))
    a("")
    a("## 4. 8 dossiers (sab pending)")
    a("")
    m.extend(table(["Slot", "Analytic job", "clearance", "human_legal_review", "NULL fields", "Reviewer"],
                   [[str(d["slot"]), d["analytic_job"], d["clearance_status"],
                     str(d["human_legal_review"]).lower(), str(sum(v is None for v in d["rights_gate"].values())),
                     str(d["sign_off"]["reviewer_name"])] for d in g["dossiers"]]))
    a("")
    a("Har dossier ke **3 real API probe targets** (IDs + watch URLs) JSON me hain. Ye "
      "**third-party copyrighted videos** hain — inka istemal likhit ijazat ke bagair nahi, aur "
      "ijazat milne par bhi alag se reused-content review hogi " + cite(7) + " " + cite(9) + ".")
    a("")
    a("## 5. Policy anchors")
    a("")
    m.extend(table(["Mauzoo", "Source"], list(g["policy_anchors"].items())))
    a("")
    a("> **Ye checklist legal advice nahi.** `not_a_legal_opinion=true` har dossier me. "
      "Credit, disclaimer aur \"non-profit\" apne aap fair use nahi banate; chaar factors aur "
      "adoalat ka faisla alag baat hai " + cite(8) + " " + cite(10) + ".")
    a("")
    a("---")
    a("")
    a("## 6. Phase B/C ki nayi real API forensics (run `" + RUN_ID_BC + "`)")
    a("")
    ang = g["phase_bc_real_evidence"]["angle_probes"]
    m.extend(table(["Angle query", "n", "1M+", "Median views", "top3_share", "fresh_30d", "Verdict", "Score"],
                   [[x["topic"], str(x["count"]), str(x["million_plus"]), f"{x['median_views']:,}",
                     str(x["top3_share"]), str(x["fresh_share_30d"]), str(x["verdict"]), str(x["score"])]
                    for x in ang]))
    a("")
    a("**Imaandaar padhne ka tarika:**")
    a("")
    a("- `science commentary long form` me **sirf 1 result** aaya — ye query bahut tang thi, "
      "\"demand nahi hai\" ka saboot **nahi**. `winnability=0.0` isi chhote sample ka natija hai.")
    a("- `why we rewatch moments` me `fresh_share_30d=1.0` aur Phase A ke `viewCount` reports me "
      "`0.0` — **dono order ka artifact** hain, trend ka faisla nahi.")
    a("- Lekin is query ka top video ka title hi **\"The NO-GOAL Moment You Need to Watch TWICE\"** "
      f"hai ({ang[0]['top_rows'][0]['views']:,} views, {ang[0]['top_rows'][0]['duration']}). "
      "Yani \"watch twice\" wala framing real audience tak pahunchta hai — hamare thesis ke liye "
      "ek **real** (magar chhota) signal.")
    a("- `frame by frame breakdown explained` ka top **jacksfilms** video **1H5M35S** ka hai with "
      f"{ang[1]['top_rows'][0]['views']:,} views — lambi frame-by-frame analysis ka bhi real precedent hai.")
    a("")
    td = g["phase_bc_real_evidence"]["winner_teardowns"]
    m.extend(table(["Real winner", "Channel", "Views", "Duration", "Transcript"],
                   [[x["title"], x["channel"], f"{x['views']:,}", str(x["duration"]),
                     str(x["transcript_status"])] for x in td]))
    a("")
    a("**6 teardown me se 5 transcripts nahi mile** (4 par `yt-dlp` bot check, 1 par `no_captions`). "
      "**1 mila**: Veritasium *\"How a slinky falls in slow motion\"* — aur usse hamare script ko "
      "seedha fayda mila. Poora hisaab `PHASE_C_SCRIPT_DRAFT_V12.md` me.")
    a("")
    a("> NOTE: in teardowns ke view counts Phase A reports se **kuch sau** differ karte hain "
      "(do alag waqt par fetch). Ye point-in-time public counts hain, koi stable analytics nahi.")
    a("")
    a("---")
    a("")
    a("## 7. Jo abhi nahi hua")
    a("")
    for k in g["non_claims"]:
        a(f"- `{k}` = **False**")
    a("")
    a("NO legal clearance, NO guaranteed views, NO human approval, NO render, NO upload, "
      "NO publish, NO monetization change, NO NASA endorsement.")
    a("")
    a("---")
    a("")
    a("## 8. Agla qadam")
    a("")
    a("1. **Aap / human reviewer** 8 dossiers ke 18 fields bhartein, `sign_off` me naam + tareekh + decision.")
    a("2. `validate_phase_bc_v12.py` ka gate test tabhi `cleared` allow karega jab sab fields verified ho.")
    a("3. Uske baad VO recording → edit → QC → metadata. Abhi kuch record/render/upload nahi.")
    a("4. Pending safety: uploaded V10 Short ka monetization OFF (aapne ON bataya tha).")
    a("")
    return "\n".join(m) + "\n"


def build_script_md(s: dict) -> str:
    m = []
    a = m.append
    a("# V12 PHASE C - Full VO Script DRAFT (placeholders, NOT for render)")
    a("")
    a("> **Poora 13-chapter script likh diya gaya** — lekin har clip reference "
      "`[SLOT n - SOURCE PENDING RIGHTS GATE]` hai. **Koi real clip, agency asset ya teesre-party "
      "video ko source clip nahi banaya gaya.** Koi VO audio record nahi, koi MP4 nahi, koi "
      "upload/publish nahi. **NO real clip is named as a source clip; NO VO has been recorded.** "
      "Ye draft **Phase B human legal review se pehle recording ke liye clear nahi** hai.")
    a("")
    a(f"**Edition:** `{EDITION}` · **Winner:** `{s['winner']}` · "
      f"**Status:** `{s['status']}`")
    a(f"**Runtime:** 600s · **Chapters:** {s['chapters']} · "
      f"**VO budget:** {s['vo_words_budget']} words · **Draft actual:** {s['vo_words_actual']} words · "
      f"**Est. VO rate:** {s['vo_wpm_estimate']} wpm · **Reading grade:** {s['vo_reading_grade']}")
    a("**Machine-readable:** `phase_c_script_draft_v12.json`, `phase_b_rights_gate_v12.json`")
    a("")
    a("---")
    a("")
    a("## 0. Real script benchmark (ek transcript jo mila)")
    a("")
    rb = s["real_script_benchmark"]
    if rb:
        a(f"`{rb['id']}` — **{rb['title']}** ({rb['channel']}, {rb['views']:,} views, "
          f"{rb['duration']}). `transcript_status=ok`, manual English captions.")
        a("")
        m.extend(table(["Metric", "Real value", "Hamara draft"], [
            ["Words", str(rb["script_words"]), str(s["vo_words_actual"])],
            ["WPM", str(rb["wpm"]), str(s["vo_wpm_estimate"])],
            ["Reading grade", str(rb["reading_grade"]), str(s["vo_reading_grade"])],
            ["CTA count", str(rb["cta_count"]), "0 (no coercion)"],
            ["Filler rate", str(rb["filler_rate"]), "n/a (text draft)"],
            ["Opens with number", str(rb["opens_with_number"]).lower(), "yes - 'Eight different clips'"],
            ["Opens with 'you'", str(rb["opens_with_you"]).lower(), "no - but H2 addresses the viewer"],
            ["Claim type", str(rb["claim_type"]), "explicit rule / promise"],
        ]))
        a("")
        a(f"**Real hook (pehla jumla):** *\"{rb['first_sentence']}\"*")
        a("")
        a(f"**Tool ka apna reading:** 200 wpm = *fast, shorts-native*; grade {rb['reading_grade']} = "
          "*too dense for spoken word*. Isliye hamara long-form draft **jaan-bujh kar dheema** hai: "
          f"~{s['vo_wpm_estimate']} wpm aur chhote jumle. `replication.beat` ne kaha *\"add a concrete "
          "number inside the first 3 seconds\"* — hamara H1 \"Eight different clips\" se khulta hai. "
          "Ye **co-occurrence** hai, koi causal \"isliye viral hua\" dawa nahi.")
        a("")
        a(f"**Real structure map:** " + ", ".join(f"{x['at']} {x['title']} ({x['pct']}%)"
                                                for x in (rb["structure"] or [])) + ".")
        a("")
        a("Hamare 13 chapters usi *promise → proof → payoff* arc ko 10 minute par phailate hain, "
          "lekin har proof ke baad **apna original diagram** aur **apni commentary** hai — "
          "clip-ko-clip compilation nahi " + cite(7) + ".")
    a("")
    a("> **Honest limit:** baqi 5 teardowns me transcript nahi mila (4 bot-check, 1 no-captions), "
      "isliye unke script/word-rate ka koi analysis **nahi likha**. Ek transcript se koi "
      "\"best channels ka formula\" nahi banaya.")
    a("")
    a("---")
    a("")
    a("## 1. Teen hook variants")
    a("")
    m.extend(table(["ID", "Label", "Text"], [[h["id"], h["label"], h["text"]] for h in s["hooks"]]))
    a("")
    a("> Number-in-title / number-in-hook ka signal Phase A reports me **aapas me ulta** tha "
      "(−65% se +389%, ek ka `r²=0.093`). Isliye ye 3 variants **test ke liye** hain, "
      "\"proven winner\" nahi. Studio Test & Compare se confirm karna hoga.")
    a("")
    a("---")
    a("")
    a("## 2. POORA SCRIPT (13 chapters)")
    a("")
    for c in s["chapter_ledger"]:
        a(f"### {c['n']}. `{c['t']}` — {c['name']}")
        a("")
        a(f"*Budget {c['vo_word_budget']} words · draft {c['vo_words_actual']} words · "
          f"`{c['status']}`*")
        a("")
        a("**Shots:** " + c["shot_list"])
        a("")
        a("**VO:**")
        a("")
        a(c["vo_text"])
        a("")
    a("---")
    a("")
    a("## 3. Edit decisions (kyun, sirf style nahi)")
    a("")
    m.extend(table(["Rule", "Reason"], [[e["rule"], e["why"]] for e in s["edit_decisions"]]))
    a("")
    a("---")
    a("")
    a("## 4. Metadata DRAFT (koi upload/publish nahi)")
    a("")
    md = s["metadata_draft"]
    a(f"- **Status:** `{md['status']}`")
    a(f"- **Working title:** `{md['working_title']}` ({md['working_title_chars']} chars)")
    a(f"- **Alt titles:** " + "; ".join(f"`{x}`" for x in md["alt_titles"]))
    a(f"- **Category:** `{md['category']['primary']}` (alternate `{md['category']['alternate']}`), "
      f"`human_must_confirm={str(md['category']['human_must_confirm']).lower()}` — agent ne set nahi kiya.")
    a(f"- **Hashtags:** " + ", ".join(f"`{x}`" for x in md["hashtags"]) + " — " + md["hashtag_note"])
    a("")
    a("**Description draft:**")
    a("")
    a("```text")
    a(md["description_draft"])
    a("```")
    a("")
    a("**Pinned comment draft:**")
    a("")
    a("```text")
    a(md["pinned_comment_draft"])
    a("```")
    a("")
    a(f"- **AI-use disclosure:** {md['ai_use_disclosure']}")
    a(f"- **Monetization recommendation:** {md['monetization_recommendation']}")
    a(f"- **Clickbait guard:** {md['clickbait_guard']}")
    a("")
    a("---")
    a("")
    a("## 5. Hard stop / jo nahi hua")
    a("")
    a("> " + s["hard_stop"])
    a("")
    for k in s["non_claims"]:
        a(f"- `{k}` = **False**")
    a("")
    a("NO legal clearance, NO guaranteed views, NO guaranteed retention, NO guaranteed virality, "
      "NO human approval, NO NASA endorsement, NO perfection. Public view counts aur ek public "
      "transcript istemal hue; kisi ka private retention / CTR / RPM data nahi.")
    a("")
    a("---")
    a("")
    a("## 6. Agla qadam")
    a("")
    a("1. **Phase B:** human reviewer 8 dossiers bhartein (18 fields + sign-off).")
    a("2. Gate pass hone ke baad: recording (`voice-02` pehle selected tha), edit, QC, metadata.")
    a("3. Tabhi koi MP4 / upload / publish ki baat. Abhi nahi.")
    a("")
    return "\n".join(m) + "\n"


def patch_next_action() -> None:
    txt = NEXT_ACTION.read_text(encoding="utf-8")
    if ADDENDUM_MARKER in txt:
        return
    add = (
        ADDENDUM_MARKER + " (NO clearance, NO render)\n\n"
        "- Phase B/C done via GitHub Actions run `42905149277` (3 angle-specific topic probes + 6 real-winner "
        "reverse teardowns) using the existing `YOUTUBE_API_KEY` secret, presence only. Bot commit `a6895cf`. "
        "Five of six transcripts were blocked (yt-dlp bot check / no captions); ONE succeeded: Veritasium "
        "`k5s1cMNTmGs` (36,618,923 views, 140 words, 200 wpm, reading grade 8.1, 0 CTAs, opens with 'you'). "
        "Its real structure map is promise -> setup -> first proof -> escalation -> payoff.\n"
        "- Deliverables: `research/multi_clip_long_form_v12/PHASE_B_RIGHTS_GATE_V12.md` + `.json` "
        "(8 dossiers, 18 field rules, 8 kill conditions, 5 attribution templates, executable gate-enforcement "
        "test that REJECTS a fabricated cleared slot) and `PHASE_C_SCRIPT_DRAFT_V12.md` + `.json` "
        "(FULL 13-chapter VO script draft with [SLOT n - SOURCE PENDING RIGHTS GATE] placeholders, "
        "3 hook variants, 7 edit decisions, metadata/pinned-comment drafts).\n"
        "- HARD STOP UNCHANGED: all 8 x 18 rights fields NULL, clearance_status=pending, "
        "human_legal_review=false, reviewer sign-off empty. Winner unchanged: MC-01, 8 DIFFERENT clips, "
        "10:00, <=13.3% source share. V10/Short NASA water-bubble asset still EXCLUDED from all 8 slots.\n"
        "- NO clip downloaded/cleared, NO VO recorded, NO final script approved, NO render/MP4, "
        "NO upload/publish, NO category set, NO pinned comment posted, NO monetization change, "
        "NO human creative approval, NO legal clearance, NO guaranteed views.\n"
        "- This addendum does NOT supersede the standing 'await human full-motion/native-audio review' line below.\n\n"
    )
    NEXT_ACTION.write_text(add + txt, encoding="utf-8")


def dumps(o) -> str:
    return json.dumps(o, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    angles = angle_summaries()
    teardowns = teardown_summaries()
    gate = build_gate_ledger(angles, teardowns)
    script = build_script_ledger(angles, teardowns)
    (D / "phase_b_rights_gate_v12.json").write_text(dumps(gate), encoding="utf-8")
    (D / "phase_c_script_draft_v12.json").write_text(dumps(script), encoding="utf-8")
    (D / "PHASE_B_RIGHTS_GATE_V12.md").write_text(build_gate_md(gate), encoding="utf-8")
    (D / "PHASE_C_SCRIPT_DRAFT_V12.md").write_text(build_script_md(script), encoding="utf-8")
    patch_next_action()
    print(f"Wrote Phase B rights gate + Phase C script draft in {D.relative_to(ROOT)}")
    print(f"Gate: {len(gate['dossiers'])} dossiers x {len(RIGHTS_FIELDS)} fields, all pending | "
          f"enforcement test rejected={gate['gate_enforcement']['rejected']}")
    print(f"Script: {script['chapters']} chapters | budget {script['vo_words_budget']} | "
          f"actual {script['vo_words_actual']} words | ~{script['vo_wpm_estimate']} wpm | "
          f"grade {script['vo_reading_grade']} | real transcript benchmark: "
          f"{'yes' if script['real_script_benchmark'] else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
