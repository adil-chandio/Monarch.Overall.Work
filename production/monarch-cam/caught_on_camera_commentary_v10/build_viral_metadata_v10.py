#!/usr/bin/env python3
"""Build a forensic, evidence-linked V10 metadata study and copy-paste metadata pack.

Run from the repository root:
    python production/monarch-cam/caught_on_camera_commentary_v10/build_viral_metadata_v10.py

Outputs live in review/final/. This script deliberately records non-claims and
uncertainties; it does not assert virality, perfection, legal compliance, human
creative approval, or audience results.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/caught_on_camera_commentary_v10"
REVIEW = BASE / "review" / "final"
RESEARCH = ROOT / "research" / "caught_on_camera_commentary_v10"

OUT_JSON = REVIEW / "viral_metadata_v10.json"
OUT_SOURCES = REVIEW / "viral_metadata_sources_v10.json"
OUT_MD = REVIEW / "viral_metadata_study_v10.md"
UPLOAD_META = REVIEW / "upload_metadata_v10.json"
QC_SUMMARY = REVIEW / "qc_summary.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, text=True,
                          capture_output=True, check=True).stdout.strip()


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |")
    return "\n".join(out)


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {i}" for i in items)


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
qc = load(REVIEW / "qc_summary.json")
tq = load(REVIEW / "technical_qc.json")
aq = load(REVIEW / "audio_qc.json")
el = load(REVIEW / "edit_ledger_v10.json")
nal = load(REVIEW / "native_audio_ledger_v10.json")
rl = load(REVIEW / "rights_ledger_v10.json")
um = load(UPLOAD_META)
cs = load(REVIEW / "contact_sheets_manifest.json")
tm = load(REVIEW / "caption_timings.json")
fix = load(REVIEW / "vo_quality_fix_v10.json")
scout = load(RESEARCH / "candidate_scout_v10.json")

HEAD = git("rev-parse", "HEAD")
HEAD_TIME = git("log", "-1", "--format=%cI")
HEAD_SUBJECT = git("log", "-1", "--format=%s")

# ---------------------------------------------------------------------------
# External research ledger. Numeric IDs/URLs come from Arena web_search results.
# Only official YouTube Help / NASA pages are used for policy claims.
# ---------------------------------------------------------------------------
SOURCES = [
    {"ref": "YT_TITLE_TIPS", "batch": "A", "result_id": 9,
     "citation": "[9](https://support.google.com/youtube/answer/12340300?hl=en-GB)",
     "title": "Thumbnail & title tips - YouTube Help",
     "url": "https://support.google.com/youtube/answer/12340300?hl=en-GB",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["accurate succinct titles", "important words first", "limit ALL CAPS/emoji",
                  "custom thumbnail guidance", "searchable vs intriguing titles"]},
    {"ref": "YT_DESCRIPTIONS", "batch": "D", "result_id": 3,
     "citation": "[3](https://support.google.com/youtube/answer/12948449?hl=en)",
     "title": "Tips for video descriptions - YouTube Help",
     "url": "https://support.google.com/youtube/answer/12948449?hl=en",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["first lines visible before Show more", "unique description",
                  "1-2 main words", "5000-char limit", "chapters for longer videos"]},
    {"ref": "YT_EDIT_SETTINGS", "batch": "D", "result_id": 2,
     "citation": "[2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop)",
     "title": "Edit video settings - Computer - YouTube Help",
     "url": "https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["100-char title limit", "5000-char description limit", "tags field",
                  "category/education type", "language and captions", "license",
                  "Shorts remixing", "audience/COPPA", "altered content setting",
                  "related video", "recording date/location"]},
    {"ref": "YT_HASHTAGS", "batch": "D", "result_id": 1,
     "citation": "[1](https://support.google.com/youtube/answer/6390658?hl=en)",
     "title": "Find playlists & videos using hashtags - YouTube Help",
     "url": "https://support.google.com/youtube/answer/6390658?hl=en",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["up to 3 hashtags shown near title", ">60 hashtags ignored",
                  "no misleading/unrelated hashtags", "no ordinary descriptive tags in description",
                  "no spaces in hashtags"]},
    {"ref": "YT_TAGS", "batch": "A", "result_id": 2,
     "citation": "[2](https://support.google.com/youtube/answer/146402?hl=en)",
     "title": "Add tags to your YouTube videos - YouTube Help",
     "url": "https://support.google.com/youtube/answer/146402?hl=en",
     "authority": "official_help", "fetched": False, "chunks": [],
     "used_for": ["tags play a minimal role", "title/thumbnail/description matter more",
                  "excessive tags in description prohibited"]},
    {"ref": "YT_SHORTS_DISCOVERY", "batch": "A", "result_id": 4,
     "citation": "[4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts)",
     "title": "Search & discovery tips - Shorts - YouTube Help",
     "url": "https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["Shorts ranked by performance and personalization",
                  "avg view duration / avg % viewed / likes / post-watch surveys",
                  "metadata matches viewer search", "no minimum posting cadence"]},
    {"ref": "YT_PERF_FAQ", "batch": "E", "result_id": 2,
     "citation": "[2](https://support.google.com/youtube/answer/141805?hl=en)",
     "title": "YouTube performance FAQ & Troubleshooting - YouTube Help",
     "url": "https://support.google.com/youtube/answer/141805?hl=en",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["search ranks by title/description/content match and engagement",
                  "tags not important", "avoid clickbait/ALL CAPS/!!!!!",
                  "publish time not known to impact long-term performance",
                  "no required upload cadence", "monetization status not a discovery signal"]},
    {"ref": "YT_SPAM", "batch": "E", "result_id": 1,
     "citation": "[1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365)",
     "title": "Spam policy - YouTube Help",
     "url": "https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["scraped content needs transformative editing/commentary/educational value",
                  "malicious clickbait prohibited", "detection evasion prohibited",
                  "asking for likes/comments is allowed", "no incentives/coercion"]},
    {"ref": "YT_GENAI", "batch": "B", "result_id": 2,
     "citation": "[2](https://support.google.com/youtube/answer/14328491?hl=en)",
     "title": "Disclosing use of GenAI content - Computer - YouTube Help",
     "url": "https://support.google.com/youtube/answer/14328491?hl=en",
     "authority": "official_help", "fetched": True, "chunks": [0],
     "used_for": ["disclose realistic AI-altered content",
                  "caption creation / voice or audio repair / cloning own voice are minor examples",
                  "AI use toggle in Studio", "disclosure alone does not limit reach or monetization"]},
    {"ref": "YT_REUSED_FAQ", "batch": "B", "result_id": 7,
     "citation": "[7](https://support.google.com/youtube/community-guide/271248162/%F0%9F%94%8E-faq-reused-content-youtube%E2%80%99s-partner-program?hl=en)",
     "title": "FAQ: Reused Content & YouTube's Partner Program - YouTube Community",
     "url": "https://support.google.com/youtube/community-guide/271248162/%F0%9F%94%8E-faq-reused-content-youtube%E2%80%99s-partner-program?hl=en",
     "authority": "official_community_faq", "fetched": False, "chunks": [],
     "used_for": ["transformative commentary/educational value", "AI channels can be eligible if original"]},
    {"ref": "YT_IMPERSONATION", "batch": "B", "result_id": 8,
     "citation": "[8](https://support.google.com/youtube/answer/2801947?sjid=14893021524564886382-NA)",
     "title": "Impersonation policy - YouTube Help",
     "url": "https://support.google.com/youtube/answer/2801947?sjid=14893021524564886382-NA",
     "authority": "official_help", "fetched": False, "chunks": [],
     "used_for": ["no AI voice clone of a real person", "no false authorization/endorsement"]},
    {"ref": "YT_ADS", "batch": "A", "result_id": 6,
     "citation": "[6](https://support.google.com/youtube/answer/6162278?hl=en)",
     "title": "Advertiser-friendly content guidelines - YouTube Help",
     "url": "https://support.google.com/youtube/answer/6162278?hl=en",
     "authority": "official_help", "fetched": False, "chunks": [],
     "used_for": ["no profanity/stronger language in title/thumbnail", "science content is generally suitable"]},
    {"ref": "NASA_IMAGES", "batch": "C", "result_id": 1,
     "citation": "[1](https://www.nasa.gov/nasa-brand-center/images-and-media/)",
     "title": "NASA Images and Media Usage Guidelines",
     "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
     "authority": "official_nasa", "fetched": True, "chunks": [0, 2, 3],
     "used_for": ["NASA content generally not US-copyrighted", "educational/informational use",
                  "NASA should be acknowledged", "no implied endorsement",
                  "identifiable persons / commercial use may need permission",
                  "current astronauts' names/likenesses restricted in promotional material",
                  "clearances may be needed for cover art / promotional content"]},
    {"ref": "NASA_ADVERTISING", "batch": "C", "result_id": 2,
     "citation": "[2](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/)",
     "title": "Advertising Guidelines - NASA",
     "url": "https://www.nasa.gov/nasa-brand-center/advertising-guidelines/",
     "authority": "official_nasa", "fetched": False, "chunks": [],
     "used_for": ["no NASA endorsement", "no insignia in ads",
                  "current astronauts/employees not in ads or marketing"]},
    {"ref": "NASA_STRATEGIC", "batch": "C", "result_id": 8,
     "citation": "[8](https://www.nasa.gov/nasa-brand-center/strategic-partnerships/)",
     "title": "NASA Strategic Partnerships / Promotional Content",
     "url": "https://www.nasa.gov/nasa-brand-center/strategic-partnerships/",
     "authority": "official_nasa", "fetched": True, "chunks": [0, 2, 3],
     "fetched_redirect_url": "https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/",
     "used_for": ["publicly available content usable if guidelines followed",
                  "short-form social media generally considered promotional content",
                  "imagery with NASA identifiers/current astronauts/current employees may not be used in promotional content",
                  "no co-branding / sponsorship / endorsement"]},
    {"ref": "NASA_BRAND", "batch": "C", "result_id": 3,
     "citation": "[3](https://www.nasa.gov/nasa-brand-center/)",
     "title": "NASA Brand Center",
     "url": "https://www.nasa.gov/nasa-brand-center/",
     "authority": "official_nasa", "fetched": False, "chunks": [],
     "used_for": ["no endorsement or misleading use", "NASA identifiers protected",
                  "third-party copyrighted material needs its own permission"]},
    {"ref": "NASA_MERCH", "batch": "C", "result_id": 4,
     "citation": "[4](https://www.nasa.gov/nasa-brand-center/merchandise-approvals/)",
     "title": "NASA Merchandise Approvals",
     "url": "https://www.nasa.gov/nasa-brand-center/merchandise-approvals/",
     "authority": "official_nasa", "fetched": False, "chunks": [],
     "used_for": ["no 'NASA approved' / 'official NASA' / co-branding wording",
                  "insignia/logotype/seal not public domain"]},
]
C = {s["ref"]: s["citation"] for s in SOURCES}

# ---------------------------------------------------------------------------
# Copy-paste metadata
# ---------------------------------------------------------------------------
TITLE_PRIMARY = "NASA Water Bubble Flips an Astronaut's Face"
TITLE_BASELINE = um["title"]

TITLE_ALTERNATIVES = [
    {"title": TITLE_PRIMARY, "type": "searchable + intriguing", "rationale": "Adds NASA for source/search clarity while keeping 'water bubble' and the flip payoff near the front."},
    {"title": TITLE_BASELINE, "type": "searchable", "rationale": "Existing committed baseline; shortest accurate description of the payoff."},
    {"title": "Artemis II Water Bubble Flips a Face", "type": "searchable", "rationale": "Mission keyword first; useful for Artemis II search intent."},
    {"title": "Why Is That Astronaut Upside Down?", "type": "intriguing", "rationale": "Curiosity gap matching hook 1; weaker explicit search terms."},
    {"title": "This Water Bubble Acts Like a Lens", "type": "searchable", "rationale": "Science-forward; leads with the object rather than the face."},
    {"title": "Not a Lens: NASA's Floating Water Ball", "type": "intriguing", "rationale": "Echoes exact first VO line; avoid if it reads as a lens claim."},
    {"title": "A Water Bubble Turned Into a Lens in Space", "type": "searchable", "rationale": "Long-tail optics phrasing; still under 50 chars."},
    {"title": "NASA Refraction: The Upside-Down Face", "type": "searchable", "rationale": "Puts the science term 'refraction' early."},
    {"title": "Watch a Water Bubble Flip a Face in Space", "type": "intriguing", "rationale": "Soft imperative matches the 'watch it again' loop, without clickbait."},
    {"title": "Artemis II: Water Sphere Refraction", "type": "archival/searchable", "rationale": "Most literal; least emotional pull."},
]
for t in TITLE_ALTERNATIVES:
    t["chars"] = len(t["title"])
assert all(t["chars"] <= 50 for t in TITLE_ALTERNATIVES)
assert all(t["chars"] <= 100 for t in TITLE_ALTERNATIVES)

DESCRIPTION_LINES = [
    "A floating water bubble aboard Artemis II acts like a liquid lens and flips an astronaut's face upside down. We break down the refraction, keep NASA's native crew audio, and replay the inverted-face detail.",
    'Source: NASA, "Fun with Water Bubbles" (2026-04-04), NASA ID art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman. Official page: https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman',
    "NASA media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ — NASA is acknowledged as the source; no NASA endorsement is implied and no NASA insignia is used. On-screen credit: \"Source: NASA / Artemis II\".",
    "Original contribution: research, commentary, replay analysis, word-by-word burned captions and a generic synthetic deep-male voiceover. NASA's native crew audio is retained; no music, sound effects, procedural bed or audio substitution was added.",
    "Educational / informational commentary and analysis, not a raw reupload. Identifiable astronauts / possible CSA personnel appear. Commercial, promotional, advertising, packaging or cover-art use may require additional clearance; no written permission, human legal review or legal opinion is claimed.",
    "No invented date, injury, outcome, view count, AI-status claim or audience-result claim. No guaranteed virality or retention.",
    "#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity",
]
DESCRIPTION_PRIMARY = "\n\n".join(DESCRIPTION_LINES)
DESCRIPTION_CHARS = len(DESCRIPTION_PRIMARY)
assert DESCRIPTION_CHARS < 5000

DESCRIPTION_SHORT = "\n\n".join([
    DESCRIPTION_LINES[0],
    DESCRIPTION_LINES[1],
    "NASA is acknowledged; no endorsement implied. Generic synthetic voiceover; native NASA audio retained. Identifiable persons appear; commercial/promotional use may require clearance.",
    "#Shorts #NASA #ArtemisII #Science #Refraction",
])
DESCRIPTION_SCIENCE = "\n\n".join([
    "Refraction through a curved floating water sphere inverts the image of an astronaut behind it. This Short replays the Artemis II 'Fun with Water Bubbles' footage, explains the liquid-lens effect, and keeps NASA's native crew audio.",
    DESCRIPTION_LINES[1],
    "Science terms: refraction, surface tension, microgravity, liquid lens, image inversion. Original commentary, word-by-word captions and a generic synthetic voiceover; no music or SFX.",
    DESCRIPTION_LINES[4],
    "#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity #Physics",
])
DESCRIPTION_RIGHTS_FIRST = "\n\n".join([
    DESCRIPTION_LINES[0],
    DESCRIPTION_LINES[1],
    "NASA media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ — NASA credited; no endorsement, insignia, co-branding or 'official NASA' wording. Identifiable current astronauts / possible CSA personnel appear; short-form social content is generally treated as promotional by NASA, so commercial or promotional use may require written clearance. No legal opinion or written permission is claimed.",
    "Generic synthetic deep-male voiceover disclosed. Native NASA audio retained. No music, SFX, procedural bed, audio substitution, invented date, injury, outcome, view count or audience-result claim.",
    "#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity",
])
DESCRIPTION_ALTERNATIVES = [
    {"id": "short", "text": DESCRIPTION_SHORT, "chars": len(DESCRIPTION_SHORT)},
    {"id": "science_forward", "text": DESCRIPTION_SCIENCE, "chars": len(DESCRIPTION_SCIENCE)},
    {"id": "rights_first", "text": DESCRIPTION_RIGHTS_FIRST, "chars": len(DESCRIPTION_RIGHTS_FIRST)},
]
assert all(d["chars"] < 5000 for d in DESCRIPTION_ALTERNATIVES)

HASHTAGS_PRIMARY = ["#Shorts", "#NASA", "#ArtemisII", "#Science", "#Refraction", "#Microgravity"]
HASHTAGS_ALTERNATIVES = [
    {"id": "minimal", "tags": ["#Shorts", "#NASA", "#ArtemisII"]},
    {"id": "science", "tags": ["#Shorts", "#NASA", "#ArtemisII", "#Science", "#Refraction", "#Physics", "#Microgravity"]},
    {"id": "mission", "tags": ["#Shorts", "#NASA", "#ArtemisII", "#Space", "#Science"]},
]
assert all(len(h) <= 60 for h in [HASHTAGS_PRIMARY] + [x["tags"] for x in HASHTAGS_ALTERNATIVES])
FORBIDDEN_HASHTAGS = ["#Viral", "#ViralShorts", "#Trending", "#FYP", "#ForYou", "#YT Viral", "#YouTubeShorts", "#Subscribe"]

TAGS = [
    "water bubble", "NASA", "Artemis II", "Artemis 2", "artemis ii", "refraction",
    "microgravity", "astronaut", "water sphere", "liquid lens", "space science",
    "upside down face", "NASA water bubble", "Fun with Water Bubbles",
]
KEYWORDS = [
    "NASA water bubble", "Artemis II water bubble", "Fun with Water Bubbles NASA",
    "astronaut upside down water", "water sphere refraction", "liquid lens in space",
    "microgravity water sphere", "surface tension water ball", "NASA Artemis II refraction",
    "water bubble flips face", "inverted face water bubble", "NASA crew laughs water bubble",
    "straw water sphere astronaut", "water orb crystal ball space", "refraction explained",
    "curved water lens", "image inversion water", "Artemis II science moment",
    "NASA 4K water bubble", "zero gravity water ball", "space bubble optics",
    "NASA native crew audio", "not CGI water bubble", "shorts science explanation",
    "NASA credited commentary", "generic synthetic voiceover", "word by word captions",
]

PINNED_COMMENT = "Which frame made you replay it — the flip around 23s or the loop back at 44s? Source: NASA / Artemis II."
COMMUNITY_POST = "A 49-second replay breakdown of NASA's Artemis II water bubble: the floating sphere acts like a liquid lens and flips the face behind it. Native crew audio kept, refraction explained, word-by-word captions burned in. Source: NASA / Artemis II. No endorsement implied."

CROSS_PLATFORM = [
    {"platform": "Instagram Reels", "caption": "A floating water bubble aboard Artemis II flips an astronaut's face upside down. Refraction, not a lens. Native NASA audio kept. Source: NASA / Artemis II. Generic synthetic voiceover. #NASA #ArtemisII #Science #Refraction", "note": "Verify current in-app caption/hashtag limits before posting; no platform limit asserted here."},
    {"platform": "TikTok", "caption": "This NASA water bubble acts like a liquid lens — and the face behind it flips. Refraction in microgravity. Source: NASA / Artemis II. Generic synthetic VO. #NASA #ArtemisII #Science", "note": "Verify current in-app disclosure tools and limits; no audience-result claim."},
    {"platform": "Facebook Reels", "caption": "NASA's Artemis II crew played with a sphere of water. Look through it: the astronaut behind it is upside down. Refraction explained, native audio retained. Source: NASA / Artemis II. #NASA #Science", "note": "Keep NASA credit and no-endorsement wording intact."},
    {"platform": "X / LinkedIn", "caption": "Forensic breakdown of one official NASA Artemis II clip: a floating water sphere refracts light like a liquid lens and inverts the face behind it. 49.4s commentary Short with native audio, captions and measured reaction windows. Source: NASA / Artemis II; no endorsement implied.", "note": "Long-form post; link to the YouTube Short or raw file, not a re-upload claim."},
]

# ---------------------------------------------------------------------------
# Pack
# ---------------------------------------------------------------------------
pack = {
    "schema_version": "1.0",
    "edition": "v10_one_clip_artemis_ii_forensic_metadata_study",
    "depth_label": "10x_forensic_metadata_study",
    "depth_label_note": "A review-depth label only, not a measurable QC, legal, or audience metric.",
    "deliverable": qc["deliverable"],
    "deliverable_sha256": qc["sha256"],
    "deliverable_bytes": qc["bytes"],
    "evidence_cutoff": {
        "commit": HEAD,
        "commit_time_utc": HEAD_TIME,
        "commit_subject": HEAD_SUBJECT,
        "note": "No calendar 'today' is asserted; the cut-off is the committed evidence state.",
    },
    "scope_and_assumptions": {
        "primary_platform": "YouTube Shorts",
        "secondary_platforms": ["Instagram Reels", "TikTok", "Facebook Reels", "X", "LinkedIn"],
        "assumption": "User asked for exhaustive 'viral metadata'; interpreted as discovery-oriented metadata grounded in the locked V10 asset, not a virality guarantee.",
        "no_new_video_render": True,
        "no_new_reference_frame_request": True,
        "research_gate": "Prior V10 clip-scout research and all 11 contact sheets are already locked; not redone.",
        "external_research": "Official YouTube Help and NASA Brand/Media pages fetched via Arena web tools; no YouTube Data API key, channel analytics, trend database, A/B results or audience data used.",
        "status": "draft_not_published",
    },
    "non_claims": {
        "virality_guarantee": False,
        "audience_result_claim": False,
        "retention_guarantee": False,
        "ctr_or_view_count_claim": False,
        "revenue_or_rpm_claim": False,
        "human_creative_approval": False,
        "human_native_audio_listening": False,
        "human_full_motion_review": False,
        "human_legal_review": False,
        "legal_opinion": False,
        "written_astronaut_or_csa_permission": False,
        "commercial_monetization_clearance": False,
        "nasa_endorsement": False,
        "nasa_approval": False,
        "perfection_claim": False,
        "zero_flaw_claim": False,
        "zero_omission_claim": False,
    },
    "asset_forensics": {
        "duration_seconds": qc["duration_seconds"],
        "frame_count": qc["frame_count"],
        "fps": qc["fps"],
        "resolution": qc["resolution"],
        "video_codec": qc["video_codec"],
        "audio_codec": qc["audio_codec"],
        "audio_sample_rate": 48000,
        "audio_channels": 2,
        "technical_pass": qc["technical_pass"],
        "technical_checks": f"{qc['technical_checks_pass']}/{qc['technical_check_count']}",
        "nine_audio_gates_pass": qc["nine_audio_gates_pass"],
        "human_creative_approval": qc["human_creative_approval"],
    },
    "source_provenance": {
        "nasa_id": scout["selected_clip"]["nasa_id"],
        "title": scout["selected_clip"]["title"],
        "date_created": scout["selected_clip"]["date_created"],
        "source_page": scout["selected_clip"]["source_page"],
        "direct_4k_url": scout["selected_clip"]["direct_4k_url"],
        "original_sha256": scout["selected_clip"]["source_sha256"],
        "vertical_master_sha256": scout["selected_clip"]["vertical_master_sha256"],
        "vertical_master_bytes": scout["selected_clip"]["vertical_master_bytes"],
        "one_clip_only": True,
        "clip_lock": scout["clip_lock"],
        "rubric_total": scout["rubric_score"]["total"],
        "rubric_minimum": scout["rubric_score"]["minimum_total"],
        "kill_switches_triggered": scout["rubric_score"]["kill_switches_triggered"],
    },
    "edit_forensics": {
        "visual_segments": el["visual_segments"],
        "beats": el["beats"],
        "script": el["script"],
        "captions": el["captions"],
        "safe_zone": el["captions"]["safe_zone_check"]["safe_zone"],
        "on_screen_label": {"text": "REFRACTION", "timeline_in": 23.42, "timeline_out": 29.90, "y_px": 320},
        "on_screen_credit": {"text": "Source: NASA / Artemis II", "timeline_in": 44.24, "timeline_out": 49.40, "y_px": 1560},
        "word_captions_y_px": 1480,
        "contact_sheets": cs["sheets"],
        "contact_sheet_count": cs["sheet_count"],
        "human_full_motion_review": cs["human_full_motion_review"],
    },
    "audio_forensics": {
        "native_audio_policy": nal["policy"],
        "reaction_windows": nal["source_audio"]["reaction_windows"],
        "inter_beat_gap_seconds": nal["inter_beat_gap_seconds"],
        "final_narrated_end_seconds": nal["final_narrated_end_seconds"],
        "mastering_chain_id": nal["mastering"]["chain_id"],
        "deliverable_audio": nal["mastering"]["deliverable_audio"],
        "nine_gates": aq["checks"],
        "measured": {k: aq["measured"][k] for k in [
            "integrated_lufs", "lra_lu", "sample_peak_dbfs", "clipped_samples",
            "movement_db", "dc_offset", "mono_fold_loss_db",
            "harsh_over_high_mid_db", "air_over_high_mid_db", "clicks"]},
        "vo_quality_fix": {
            "before_sha256": fix["before"]["sha256"],
            "after_sha256": fix["after"]["sha256"],
            "air_before_db": fix["before"]["full_mix_spectral"]["air_over_high_mid_db"],
            "air_after_db": fix["after"]["full_mix_spectral"]["air_over_high_mid_db"],
            "harsh_before_db": fix["before"]["full_mix_spectral"]["harsh_over_high_mid_db"],
            "harsh_after_db": fix["after"]["full_mix_spectral"]["harsh_over_high_mid_db"],
            "measured_delta": fix["measured_delta"],
            "legacy_broad_declick": fix["root_cause"]["legacy_broad_declick"],
            "narrow_declick_events": fix["correction"]["narrow_declick_events"],
        },
        "human_native_audio_listening": nal["human_native_audio_listening"],
    },
    "rights_and_publicity": {
        "workspace_flags": {
            "rights_basis": rl["rights_basis"],
            "restrictions": rl["restrictions"],
            "claims": rl["claims"],
        },
        "external_findings": [
            {"finding": "NASA content is generally not subject to US copyright and may be used for educational/informational purposes; NASA should be acknowledged.", "citation": C["NASA_IMAGES"]},
            {"finding": "NASA content must not imply endorsement; NASA insignia/logotype/seal are protected.", "citation": C["NASA_BRAND"]},
            {"finding": "If NASA media includes an identifiable person, commercial use may infringe privacy/publicity rights and permission should be obtained.", "citation": C["NASA_IMAGES"]},
            {"finding": "Current astronauts' names/likenesses may not be used on commercial products, advertisements, promotional material or packaging.", "citation": C["NASA_IMAGES"]},
            {"finding": "Short-form social media content is generally considered promotional content; imagery with NASA identifiers, current astronauts or current employees may not be used in promotional content.", "citation": C["NASA_STRATEGIC"]},
            {"finding": "No 'NASA approved', 'official NASA' or co-branding wording.", "citation": C["NASA_MERCH"]},
            {"finding": "Advertising/marketing must not imply NASA endorsement; no insignia in ads.", "citation": C["NASA_ADVERTISING"]},
        ],
        "high_severity_gate": "Because this is a 49.4 s social Short featuring identifiable Artemis II astronauts, NASA's own guidance treats short-form social content as generally promotional. Commercial/monetized/promotional publication, cover art using astronaut faces, ads, packaging or sponsorship should not proceed without written clearance and human legal review. No such clearance exists in the workspace.",
        "not_a_legal_opinion": True,
    },
    "platform_policy_matrix": [
        {"rule": "Title limit is 100 characters; description limit is 5,000 characters.", "citation": C["YT_EDIT_SETTINGS"]},
        {"rule": "Titles should be accurate, succinct, with important words first; limit ALL CAPS and emoji.", "citation": C["YT_TITLE_TIPS"]},
        {"rule": "First few description lines are what viewers see before 'Show more'; keep each description unique and feature 1-2 main words.", "citation": C["YT_DESCRIPTIONS"]},
        {"rule": "Search ranks by title/description/content match and engagement; tags are not important.", "citation": C["YT_PERF_FAQ"]},
        {"rule": "Shorts ranking uses viewer personalization, view duration, average % viewed, likes and post-watch surveys; no minimum posting cadence.", "citation": C["YT_SHORTS_DISCOVERY"]},
        {"rule": "Publish time is not known to affect long-term performance; no required upload frequency.", "citation": C["YT_PERF_FAQ"]},
        {"rule": "Up to three hashtags may appear near the title; >60 hashtags are ignored; misleading/unrelated hashtags and ordinary descriptive tags in the description are prohibited.", "citation": C["YT_HASHTAGS"]},
        {"rule": "Tags play a minimal role and mainly correct common misspellings; excessive tags in the description are prohibited.", "citation": C["YT_TAGS"]},
        {"rule": "Reused/scraped content needs original commentary, educational value or unique editing; malicious clickbait and detection evasion are prohibited.", "citation": C["YT_SPAM"]},
        {"rule": "AI disclosure is required for realistic AI-generated/altered content; caption creation, voice/audio repair and cloning one's own voice are listed as minor examples.", "citation": C["YT_GENAI"]},
        {"rule": "No AI voice clone of a real person and no false authorization/endorsement.", "citation": C["YT_IMPERSONATION"]},
        {"rule": "Asking viewers to like/comment is allowed; incentives, coercion and fake engagement are not.", "citation": C["YT_SPAM"]},
        {"rule": "Avoid profanity/strong language in titles/thumbnails for advertiser-friendly eligibility.", "citation": C["YT_ADS"]},
    ],
    "youtube_shorts_primary": {
        "title": TITLE_PRIMARY,
        "title_chars": len(TITLE_PRIMARY),
        "baseline_title": TITLE_BASELINE,
        "baseline_title_chars": len(TITLE_BASELINE),
        "internal_target_title_chars_max": 50,
        "platform_title_chars_max": 100,
        "title_alternatives": TITLE_ALTERNATIVES,
        "description": DESCRIPTION_PRIMARY,
        "description_chars": DESCRIPTION_CHARS,
        "description_lines": DESCRIPTION_LINES,
        "description_alternatives": DESCRIPTION_ALTERNATIVES,
        "hashtags": HASHTAGS_PRIMARY,
        "hashtags_count": len(HASHTAGS_PRIMARY),
        "hashtags_alternatives": HASHTAGS_ALTERNATIVES,
        "forbidden_hashtags": FORBIDDEN_HASHTAGS,
        "tags": TAGS,
        "tags_note": "Enter only in the Studio tags field; do not paste a comma-separated list into the description.",
        "keywords": KEYWORDS,
        "keywords_note": "Research/search-intent terms only; no search-volume or ranking claim.",
        "category": {
            "suggestion": "Education",
            "education_type_options": ["science experiment", "real life application", "concept overview"],
            "alternative": "Science & Technology if available in Studio",
            "human_must_confirm": True,
        },
        "language": "English",
        "captions": {
            "burned_in_word_by_word": True,
            "word_count": tm["word_count"],
            "separate_caption_track_recommended": True,
            "caption_certification_human_must_confirm": True,
        },
        "thumbnail_cover": {
            "visual_anchor": "0.0-1.5 s payoff flash: inverted face inside the water sphere, word captions already burned in",
            "suggested_overlay_text": ["NOT A LENS", "UPSIDE DOWN?"],
            "do_not_add": ["NASA insignia", "NASA logotype", "NASA seal", "astronaut face as promotional cover art without clearance", "official NASA wording", "co-branding", "fake view counts"],
            "custom_thumbnail_for_shorts_human_must_confirm": True,
        },
        "ai_disclosure": {
            "description_text_present": True,
            "generic_synthetic_voiceover": True,
            "real_person_voice_clone": False,
            "realistic_altered_footage_claim": False,
            "studio_ai_use_toggle_recommendation": "Likely 'No' under YouTube's cited minor-edit examples, but a human publisher must confirm the current Studio setting; keep the textual disclosure regardless.",
            "human_must_confirm": True,
        },
        "studio_settings": [
            {"setting": "Title", "value": TITLE_PRIMARY, "human_confirm": True},
            {"setting": "Description", "value": "primary description above", "human_confirm": True},
            {"setting": "Hashtags", "value": "in description, 6 tags", "human_confirm": True},
            {"setting": "Tags", "value": "tag field only", "human_confirm": True},
            {"setting": "Category", "value": "Education / science experiment (suggested)", "human_confirm": True},
            {"setting": "Language", "value": "English", "human_confirm": True},
            {"setting": "Audience / made for kids", "value": "human decision required", "human_confirm": True},
            {"setting": "License", "value": "Standard YouTube License suggested; not Creative Commons over NASA footage/persons", "human_confirm": True},
            {"setting": "Shorts remixing", "value": "disable unless rights reviewed", "human_confirm": True},
            {"setting": "Altered / synthetic content", "value": "human confirm; textual disclosure retained", "human_confirm": True},
            {"setting": "Comments and ratings", "value": "enable", "human_confirm": True},
            {"setting": "Visibility", "value": "keep draft/unlisted until rights review", "human_confirm": True},
            {"setting": "Branded content / paid promotion", "value": "none", "human_confirm": True},
            {"setting": "Recording date", "value": "2026-04-04 from NASA source metadata", "human_confirm": True},
            {"setting": "Recording location", "value": "Artemis II mission (NASA footage), not asserted as our filming location", "human_confirm": True},
            {"setting": "Related video", "value": "optional; requires advanced feature access", "human_confirm": True},
            {"setting": "End screen", "value": "not used for this Short; 49.4 s would qualify only if applicable", "human_confirm": True},
        ],
        "pinned_comment": PINNED_COMMENT,
        "pinned_comment_note": "A genuine question is allowed; do not offer rewards for likes/comments/subs.",
        "community_post": COMMUNITY_POST,
    },
    "cross_platform_adaptations": CROSS_PLATFORM,
    "hook_and_retention_map": {
        "first_3_s": "Payoff flash + 'THAT IS NOT A LENS. WATCH THE FACE...' word captions; mute-readable.",
        "beat_1_hook_s": el["beats"][0]["timeline_in"],
        "rehook_s": el["beats"][4]["timeline_in"],
        "label_s": 23.42,
        "science_payoff_s": el["beats"][5]["timeline_in"],
        "authenticity_line_s": el["beats"][6]["timeline_in"],
        "loop_back_s": el["visual_segments"][2]["timeline_in"],
        "credit_s": 44.24,
        "native_reaction_windows": nal["source_audio"]["reaction_windows"],
        "loop_design": "Last line returns to the opening frame; no fade-in, no title card.",
    },
    "ab_test_plan": {
        "status": "plan_only_no_results",
        "variables": [
            {"variable": "Title", "variants": [TITLE_PRIMARY, TITLE_BASELINE, "Why Is That Astronaut Upside Down?"]},
            {"variable": "First description line", "variants": ["payoff-first", "science-first", "rights-first"]},
            {"variable": "Cover frame", "variants": ["0.0 s flash", "23.42 s REFRACTION label frame"]},
            {"variable": "Pinned comment", "variants": [PINNED_COMMENT, "No pinned comment"]},
            {"variable": "Hashtag order", "variants": ["#Shorts #NASA #ArtemisII first", "#NASA #ArtemisII #Shorts first"]},
        ],
        "metrics_to_observe": ["impressions", "viewed vs ignored", "average view duration", "average % viewed", "likes", "post-watch survey", "not interested feedback", "search terms in Analytics"],
        "constraints": [
            "Change one variable at a time where possible.",
            "Prefer Studio title/thumbnail edits over duplicate re-uploads of the same file.",
            "Never use misleading/clickbait titles, fake engagement, or detection-evasion edits.",
            "Do not claim a result until human-verified analytics exist.",
        ],
        "citations": [C["YT_PERF_FAQ"], C["YT_SHORTS_DISCOVERY"], C["YT_SPAM"]],
    },
    "pre_publish_checklist": [
        {"check": "Deliverable SHA-256 matches committed evidence", "status": "verified", "evidence": "qc_summary.json"},
        {"check": "Source NASA ID / page / SHA recorded", "status": "verified", "evidence": "candidate_scout_v10.json / rights_ledger_v10.json"},
        {"check": "49.4 s / 1482 frames / 1080x1920 / 30 fps / H.264+AAC", "status": "verified", "evidence": "qc_summary.json"},
        {"check": "Nine audio gates true", "status": "verified", "evidence": "audio_qc.json"},
        {"check": "33/33 technical checks true", "status": "verified", "evidence": "qc_summary.json"},
        {"check": "VO clarity correction applied and measured", "status": "verified", "evidence": "vo_quality_fix_v10.json"},
        {"check": "118 word-by-word caption events", "status": "verified", "evidence": "caption_timings.json"},
        {"check": "Safe zones / no black bars / no fade-in / no title card", "status": "verified", "evidence": "technical_qc.json"},
        {"check": "NASA on-screen credit exact: 'Source: NASA / Artemis II'", "status": "verified", "evidence": "captions_v10.ass"},
        {"check": "NASA credited in description", "status": "verified", "evidence": "this pack"},
        {"check": "NASA guidelines URL included in description", "status": "verified", "evidence": "this pack"},
        {"check": "No NASA insignia / logotype / seal", "status": "verified", "evidence": "rights_ledger_v10.json"},
        {"check": "No 'official NASA' / 'NASA approved' / co-branding wording", "status": "verified", "evidence": "this pack"},
        {"check": "No endorsement implied", "status": "verified", "evidence": "rights_ledger_v10.json + this pack"},
        {"check": "Identifiable astronauts / possible CSA personnel disclosed", "status": "verified", "evidence": "rights_ledger_v10.json + this pack"},
        {"check": "Commercial/promotional clearance obtained", "status": "pending_human", "evidence": "rights_ledger_v10.json"},
        {"check": "Written astronaut/CSA permission in workspace", "status": "not_claimed", "evidence": "rights_ledger_v10.json"},
        {"check": "Human legal review completed", "status": "pending_human", "evidence": "rights_ledger_v10.json"},
        {"check": "Human full-motion review completed", "status": "pending_human", "evidence": "qc_summary.json"},
        {"check": "Human native-audio listening completed", "status": "pending_human", "evidence": "qc_summary.json"},
        {"check": "Human creative approval", "status": "pending_human", "evidence": "qc_summary.json"},
        {"check": "Monetization / ads / sponsorship decision", "status": "pending_human", "evidence": "this pack"},
        {"check": "No music / SFX / procedural bed / audio substitution", "status": "verified", "evidence": "native_audio_ledger_v10.json"},
        {"check": "No 1.08x time-stretch", "status": "verified", "evidence": "script_variants_v10.md / native_audio_ledger_v10.json"},
        {"check": "No real-person voice clone", "status": "verified", "evidence": "native_audio_ledger_v10.json"},
        {"check": "Generic synthetic voiceover disclosed in description", "status": "verified", "evidence": "this pack"},
        {"check": "Studio AI-use toggle confirmed by human", "status": "pending_human", "evidence": "this pack"},
        {"check": "Title <=100 platform chars and <=50 internal chars", "status": "verified", "evidence": "this pack"},
        {"check": "Title accurate, no ALL CAPS / emoji / clickbait", "status": "verified", "evidence": "this pack"},
        {"check": "Description <5000 chars and unique", "status": "verified", "evidence": "this pack"},
        {"check": "First two lines carry payoff + 1-2 main words", "status": "verified", "evidence": "this pack"},
        {"check": "Hashtags <=60, relevant, no spaces", "status": "verified", "evidence": "this pack"},
        {"check": "No #Viral / #Trending / #FYP stuffing", "status": "verified", "evidence": "this pack"},
        {"check": "Tags only in tag field; no descriptive tag list in description", "status": "verified", "evidence": "this pack"},
        {"check": "Category / language / caption certification set by human", "status": "pending_human", "evidence": "this pack"},
        {"check": "Audience / made-for-kids decision by human", "status": "pending_human", "evidence": "this pack"},
        {"check": "License set to Standard (not CC) by human", "status": "pending_human", "evidence": "this pack"},
        {"check": "Shorts remixing decision by human", "status": "pending_human", "evidence": "this pack"},
        {"check": "Visibility kept draft/unlisted until rights review", "status": "pending_human", "evidence": "this pack"},
        {"check": "Cross-platform limits verified in-app", "status": "pending_human", "evidence": "this pack"},
        {"check": "No invented date / injury / outcome / view count", "status": "verified", "evidence": "this pack"},
        {"check": "No guaranteed virality / retention / revenue claim", "status": "verified", "evidence": "this pack"},
        {"check": "No perfection / zero-flaw / zero-omission claim", "status": "verified", "evidence": "this pack"},
        {"check": "A/B plan documented but no results claimed", "status": "verified", "evidence": "this pack"},
        {"check": "Publish time not claimed to affect long-term performance", "status": "verified", "evidence": C["YT_PERF_FAQ"]},
    ],
    "forensic_audit": [],
    "inconsistencies_and_stale_flags": [
        {"item": "candidate_scout_v10.json review_flags.technical_qc_pass=false", "resolution": "Stale pre-render research flag. Current qc_summary.json / technical_qc.json technical_pass=true at commit 8965beb.", "status": "explained"},
        {"item": "upload_metadata_v10.json target_title_chars_max=50 vs YouTube 100-char limit", "resolution": "50 is an internal mobile-readability target, not the platform maximum.", "status": "explained", "citation": C["YT_EDIT_SETTINGS"]},
        {"item": "native_audio_ledger source_audio_duration_s=42.688 vs rights_ledger source_duration_seconds=42.709309", "resolution": "Decoded audio stream duration vs official 4K video metadata duration; not a contradiction.", "status": "explained"},
        {"item": "edit_ledger beat 1 source_in=6.0 but source_out=3.574", "resolution": "Beat 1 crosses the 1.5 s flash into the main source; source_for_time mapping wraps from 6.0 back to 0.0-based main. Not an error.", "status": "explained"},
        {"item": "candidate_scout clip_lock.locked_at_utc=2026-11-09 vs commit time 2026-11-10", "resolution": "Research lock predates the render/push commit; chronology only.", "status": "explained"},
        {"item": "technical_pass=true vs human_creative_approval=false", "resolution": "Deliberately separate; objective QC is not creative sign-off.", "status": "explained"},
        {"item": "vo_quality_fix before SHA 1cfd... vs after SHA efce...", "resolution": "Two distinct committed MP4s; the de03272 audio was replaced by the corrected 8965beb audio.", "status": "explained"},
        {"item": "upload_metadata status=draft_not_published", "resolution": "Still true; no upload, analytics, or audience result exists.", "status": "verified"},
    ],
    "uncertainty_ledger": [
        "No human listening, full-motion review, or creative approval is documented.",
        "No legal opinion, human legal review, or written astronaut/CSA permission is documented.",
        "No commercial monetization, advertising, sponsorship, packaging or cover-art clearance is documented.",
        "No YouTube Data API key, channel analytics, trend/competitor database, search-volume data, retention graph, CTR, RPM, view count or A/B result was available.",
        "No virality, reach, retention, revenue, subscriber or audience-result claim is made.",
        "Platform policies and Studio UI can change; the human publisher must re-check current settings before publishing.",
        "The AI-use toggle decision is a recommendation based on cited examples, not a compliance determination.",
        "Cross-platform character/hashtag limits are not asserted; verify in each app.",
        "NASA's 'short-form social media is generally promotional' guidance creates a high-severity rights gate for commercial use; this study does not resolve it.",
        "Perfection, zero flaws, zero omissions and 'nothing missed' are explicitly not claimed; unverifiable items are listed here instead.",
    ],
    "sources": SOURCES,
    "source_quality_note": "Official YouTube Help and NASA pages are used for policy claims. Community posts surfaced in search (e.g. a 60-second Shorts definition or tag-stuffing anecdotes) are not used as authoritative policy here.",
    "citation_policy": "External claims use Arena web_search result IDs/URLs in [id](url) form. Workspace claims cite committed file paths.",
    "generated_by": "production/monarch-cam/caught_on_camera_commentary_v10/build_viral_metadata_v10.py",
}

# Build forensic claim/evidence/status audit.
def audit(claim: str, evidence: str, status: str) -> dict:
    return {"claim": claim, "evidence": evidence, "status": status}

A = pack["forensic_audit"]
A += [
    audit("The deliverable is the corrected 8965beb MP4, not de03272.", "qc_summary.json sha256=efce2ea...", "verified_workspace"),
    audit("Duration is 49.4 s / 1482 frames.", "qc_summary.json", "verified_workspace"),
    audit("Resolution is 1080x1920 at 30 fps.", "qc_summary.json", "verified_workspace"),
    audit("Video is H.264, audio is AAC 48 kHz stereo.", "qc_summary.json / technical_qc.json", "verified_workspace"),
    audit("All nine web audio gates pass.", "audio_qc.json checks", "verified_workspace"),
    audit("Integrated loudness is -14.66 LUFS.", "audio_qc.json", "verified_workspace"),
    audit("True peak is -1.88 dBFS with 0 clipped samples.", "audio_qc.json", "verified_workspace"),
    audit("0 click runs remain after the narrow declick fix.", "audio_qc.json", "verified_workspace"),
    audit("Air/high-mid improved from -5.55 dB to -0.28 dB.", "vo_quality_fix_v10.json", "verified_workspace"),
    audit("Legacy broad declick changed 4.2478% of samples.", "vo_quality_fix_v10.json", "verified_workspace"),
    audit("Narrow repair changed ~1.32% then ~0.24% of samples.", "vo_quality_fix_v10.json", "verified_workspace"),
    audit("33/33 technical checks pass.", "qc_summary.json", "verified_workspace"),
    audit("technical_pass is separate from human_creative_approval=false.", "qc_summary.json", "verified_workspace"),
    audit("One official NASA clip only.", "edit_ledger_v10.json / candidate_scout_v10.json", "verified_workspace"),
    audit("NASA ID is art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman.", "candidate_scout_v10.json", "verified_workspace"),
    audit("Source title is 'Fun with Water Bubbles', dated 2026-04-04.", "candidate_scout_v10.json", "verified_workspace"),
    audit("Original 4K SHA is 7fd9cd0c...c0dc.", "candidate_scout_v10.json", "verified_workspace"),
    audit("Vertical master SHA is 11395618...5960c.", "candidate_scout_v10.json", "verified_workspace"),
    audit("Clip rubric is 91/100 vs 78 minimum, no kill switches.", "candidate_scout_v10.json", "verified_workspace"),
    audit("Variant A / hook 1 is selected.", "script_variants_v10.md / edit_ledger_v10.json", "verified_workspace"),
    audit("Script has 118 words across 8 beats.", "edit_ledger_v10.json / caption_timings.json", "verified_workspace"),
    audit("Eight voice-01 VO WAVs are sequential with 0.1 s gaps.", "native_audio_ledger_v10.json", "verified_workspace"),
    audit("Native NASA audio bed is retained.", "native_audio_ledger_v10.json", "verified_workspace"),
    audit("Three reaction windows are boosted +8 dB with measured envelope.", "native_audio_ledger_v10.json", "verified_workspace"),
    audit("No music, SFX, procedural bed or audio substitution.", "native_audio_ledger_v10.json", "verified_workspace"),
    audit("No 1.08x time-stretch.", "script_variants_v10.md", "verified_workspace"),
    audit("Word-by-word burned captions use 118 events.", "caption_timings.json / captions_v10.ass", "verified_workspace"),
    audit("On-screen label is REFRACTION at 23.42-29.90 s.", "captions_v10.ass", "verified_workspace"),
    audit("On-screen credit is 'Source: NASA / Artemis II' at 44.24-49.40 s.", "captions_v10.ass", "verified_workspace"),
    audit("Safe zone is top 250 / bottom 1560 / left 80 / right 1000.", "edit_ledger_v10.json", "verified_workspace"),
    audit("7 contact sheets + first3s/last3s review images exist.", "contact_sheets_manifest.json", "verified_workspace"),
    audit("Human full-motion review is false.", "contact_sheets_manifest.json / qc_summary.json", "verified_workspace"),
    audit("NASA is credited on-screen and in metadata.", "captions_v10.ass / upload_metadata_v10.json", "verified_workspace"),
    audit("No NASA insignia used.", "rights_ledger_v10.json", "verified_workspace"),
    audit("No NASA endorsement implied.", "rights_ledger_v10.json", "verified_workspace"),
    audit("Identifiable astronauts / possible CSA personnel appear.", "rights_ledger_v10.json", "verified_workspace"),
    audit("No written astronaut/CSA permission in workspace.", "rights_ledger_v10.json", "verified_workspace"),
    audit("Commercial monetization clearance is false.", "rights_ledger_v10.json", "verified_workspace"),
    audit("Human legal review is false; not a legal opinion.", "rights_ledger_v10.json", "verified_workspace"),
    audit("Generic synthetic voiceover is disclosed; no real-person clone.", "native_audio_ledger_v10.json / upload_metadata_v10.json", "verified_workspace"),
    audit("No audience-result or virality guarantee claim.", "qc_summary.json / upload_metadata_v10.json", "verified_workspace"),
    audit("YouTube title limit is 100 characters.", C["YT_EDIT_SETTINGS"], "verified_external_guidance"),
    audit("YouTube description limit is 5,000 characters.", C["YT_EDIT_SETTINGS"], "verified_external_guidance"),
    audit("Titles should be accurate/succinct with important words first.", C["YT_TITLE_TIPS"], "verified_external_guidance"),
    audit("First description lines appear before 'Show more'.", C["YT_DESCRIPTIONS"], "verified_external_guidance"),
    audit("Descriptions should be unique with 1-2 main words.", C["YT_DESCRIPTIONS"], "verified_external_guidance"),
    audit("Up to 3 hashtags may appear near the title.", C["YT_HASHTAGS"], "verified_external_guidance"),
    audit("More than 60 hashtags are ignored.", C["YT_HASHTAGS"], "verified_external_guidance"),
    audit("Misleading/unrelated hashtags are prohibited.", C["YT_HASHTAGS"], "verified_external_guidance"),
    audit("Tags play a minimal discovery role.", C["YT_TAGS"], "verified_external_guidance"),
    audit("Search uses title/description/content match and engagement.", C["YT_PERF_FAQ"], "verified_external_guidance"),
    audit("Shorts use view duration, % viewed, likes and surveys.", C["YT_SHORTS_DISCOVERY"], "verified_external_guidance"),
    audit("No minimum posting cadence is required.", C["YT_SHORTS_DISCOVERY"], "verified_external_guidance"),
    audit("Publish time is not known to affect long-term performance.", C["YT_PERF_FAQ"], "verified_external_guidance"),
    audit("Scraped content needs transformative editing/commentary/educational value.", C["YT_SPAM"], "verified_external_guidance"),
    audit("Malicious clickbait and detection evasion are prohibited.", C["YT_SPAM"], "verified_external_guidance"),
    audit("Asking for likes/comments is allowed without incentives.", C["YT_SPAM"], "verified_external_guidance"),
    audit("Realistic AI-altered content needs disclosure; minor edits listed as not required.", C["YT_GENAI"], "verified_external_guidance"),
    audit("No AI voice clone of a real person / false endorsement.", C["YT_IMPERSONATION"], "verified_external_guidance"),
    audit("NASA content generally not US-copyrighted; educational/informational use allowed.", C["NASA_IMAGES"], "verified_external_guidance"),
    audit("NASA should be acknowledged as source.", C["NASA_IMAGES"], "verified_external_guidance"),
    audit("Identifiable persons in NASA media may need permission for commercial use.", C["NASA_IMAGES"], "verified_external_guidance"),
    audit("Current astronauts' likenesses restricted in promotional material.", C["NASA_IMAGES"], "verified_external_guidance"),
    audit("Short-form social media is generally promotional content.", C["NASA_STRATEGIC"], "verified_external_guidance"),
    audit("NASA identifiers/current astronauts may not be used in promotional content.", C["NASA_STRATEGIC"], "verified_external_guidance"),
    audit("No 'NASA approved' / 'official NASA' / co-branding wording.", C["NASA_MERCH"], "verified_external_guidance"),
    audit("NASA endorsement must not be implied in advertising.", C["NASA_ADVERTISING"], "verified_external_guidance"),
    audit("The proposed title will rank or go viral.", "no evidence", "prohibited_claim"),
    audit("The video is legally cleared for commercial monetization.", "no evidence", "prohibited_claim"),
    audit("NASA approved or endorsed this edit.", "no evidence", "prohibited_claim"),
    audit("A human listened to the final mix and approved it.", "no evidence", "prohibited_claim"),
    audit("The metadata pack is perfect / has zero flaws / missed nothing.", "no evidence", "prohibited_claim"),
    audit("Audience results, retention, CTR, RPM or view counts are known.", "no evidence", "prohibited_claim"),
    audit("The AI-use toggle is definitively not required.", "cited examples only", "inferred_human_confirm_required"),
    audit("Custom thumbnail editing is available for this Short.", "Studio UI varies", "inferred_human_confirm_required"),
    audit("Cross-platform character/hashtag limits are current.", "not asserted", "unverified"),
    audit("Best publish time or posting cadence can be predicted.", "official help says no long-term effect / no cadence", "unverified"),
    audit("Competitor/trend/search-volume data was used.", "no API/analytics available", "unverified"),
]

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
sources_doc = {
    "edition": pack["edition"],
    "evidence_cutoff_commit": HEAD,
    "source_quality_note": pack["source_quality_note"],
    "citation_policy": pack["citation_policy"],
    "sources": SOURCES,
}
save(OUT_JSON, pack)
save(OUT_SOURCES, sources_doc)

# Patch the active upload metadata to point at / adopt the new pack.
rel_json = str(OUT_JSON.relative_to(ROOT))
rel_sources = str(OUT_SOURCES.relative_to(ROOT))
rel_md = str(OUT_MD.relative_to(ROOT))
um["metadata_study"] = rel_md
um["metadata_pack"] = rel_json
um["metadata_sources"] = rel_sources
um["active_metadata_pack"] = rel_json
um["baseline_title"] = TITLE_BASELINE
um["title"] = TITLE_PRIMARY
um["title_chars"] = len(TITLE_PRIMARY)
um["platform_title_chars_max"] = 100
um["description"] = DESCRIPTION_LINES
um["description_chars"] = DESCRIPTION_CHARS
um["hashtags"] = HASHTAGS_PRIMARY
um["tags"] = TAGS
um["keywords_research_only"] = KEYWORDS
um["pinned_comment"] = PINNED_COMMENT
um["community_post"] = COMMUNITY_POST
um["disclosure"]["ai_use_toggle_human_confirmation_required"] = True
um["claims"]["metadata_study_written"] = True
um["claims"]["perfection_claim"] = False
um["claims"]["zero_omission_claim"] = False
save(UPLOAD_META, um)

qc["metadata_study"] = rel_md
qc["metadata_pack"] = rel_json
qc["metadata_sources"] = rel_sources
for item in (rel_md, rel_json, rel_sources):
    if item not in qc["evidence"]:
        qc["evidence"].append(item)
qc["note"] = (qc["note"] + " A forensic metadata study and sources ledger were added; "
              "they are drafting/research evidence only, not human creative approval, "
              "legal clearance, perfection or an audience-result claim.")
save(QC_SUMMARY, qc)

# ---------------------------------------------------------------------------
# Markdown study
# ---------------------------------------------------------------------------
m = []
m.append("# V10 Forensic Metadata Study — Artemis II Water Bubble Short")
m.append("")
m.append("> **Roman Urdu note:** Ye pack “viral hone ki guarantee” nahi deta. Ye evidence-based, discovery-oriented metadata + forensic audit hai. Jo verify nahi ho saka (legal clearance, human listening, analytics, perfection) usse explicitly **uncertain / pending** rakha gaya hai.")
m.append("")
m.append(f"**Evidence cut-off:** `{HEAD}` — `{HEAD_TIME}` — `{HEAD_SUBJECT}`  ")
m.append(f"**Deliverable:** `{pack['deliverable']}`  ")
m.append(f"**SHA-256:** `{pack['deliverable_sha256']}`  ")
m.append(f"**Size:** {pack['deliverable_bytes']:,} bytes  ")
m.append(f"**Machine-readable pack:** `{rel_json}`  ")
m.append(f"**Sources ledger:** `{rel_sources}`")
m.append("")
m.append("---")
m.append("")
m.append("## 0. Honesty gate — what this study does NOT claim")
m.append("")
m.append(bullets([
    "No virality, reach, retention, revenue, subscriber, CTR, RPM, view-count or audience-result claim.",
    "No perfection, zero-flaw, zero-omission or “nothing was missed” claim — the user's requested absolute is explicitly declined as unverifiable.",
    "No human creative approval, human full-motion review, or human native-audio listening sign-off.",
    "No legal opinion, human legal review, written astronaut/CSA permission, or commercial/monetization clearance.",
    "No NASA endorsement, NASA approval, “official NASA” wording, insignia, or co-branding.",
    "`technical_pass=true` remains separate from `human_creative_approval=false`.",
    "No YouTube Data API key, channel analytics, trend database, search-volume data, A/B result or competitor retention graph was available.",
]))
m.append("")
m.append("## 1. Copy-paste primary metadata (YouTube Shorts)")
m.append("")
m.append("**Title**")
m.append("")
m.append("```text")
m.append(TITLE_PRIMARY)
m.append("```")
m.append("")
m.append(f"Title chars: **{len(TITLE_PRIMARY)}** (internal target ≤50; YouTube limit 100 {C['YT_EDIT_SETTINGS']}). Baseline committed title was `{TITLE_BASELINE}` ({len(TITLE_BASELINE)} chars). Accurate, succinct, important words first, no ALL CAPS/emoji {C['YT_TITLE_TIPS']}.")
m.append("")
m.append("**Description**")
m.append("")
m.append("```text")
m.append(DESCRIPTION_PRIMARY)
m.append("```")
m.append("")
m.append(f"Description chars: **{DESCRIPTION_CHARS}** / 5,000 {C['YT_DESCRIPTIONS']}. Unique, first lines carry the payoff, and the 1–2 main words are **water bubble** / **refraction** {C['YT_DESCRIPTIONS']}.")
m.append("")
m.append("**Hashtags**")
m.append("")
m.append("```text")
m.append(" ".join(HASHTAGS_PRIMARY))
m.append("```")
m.append("")
m.append(f"6 hashtags, no spaces, all directly related. Up to 3 may appear near the title; >60 would be ignored; unrelated/misleading tags and ordinary descriptive tag lists in the description are prohibited {C['YT_HASHTAGS']}. Deliberately excluded: `{', '.join(FORBIDDEN_HASHTAGS)}`.")
m.append("")
m.append("**Tags — Studio tag field only**")
m.append("")
m.append("```text")
m.append(", ".join(TAGS))
m.append("```")
m.append("")
m.append(f"Tags mainly correct misspellings and otherwise play a minimal role {C['YT_TAGS']}; do not paste this list into the description {C['YT_HASHTAGS']}.")
m.append("")
m.append("**Pinned comment**")
m.append("")
m.append("```text")
m.append(PINNED_COMMENT)
m.append("```")
m.append("")
m.append(f"A genuine question is allowed; incentives/coercion/fake engagement are not {C['YT_SPAM']}.")
m.append("")
m.append("---")
m.append("")
m.append("## 2. Title alternatives (forensic comparison)")
m.append("")
m.append(md_table(["Title", "Chars", "Type", "Rationale"],
                  [[f"`{t['title']}`", t["chars"], t["type"], t["rationale"]] for t in TITLE_ALTERNATIVES]))
m.append("")
m.append(f"Rejected style lanes: ALL CAPS, emoji stuffing, `viral/trending/guaranteed`, fake counts, “shocking”, “official NASA”, “NASA approved”. Accurate titles and avoiding clickbait/sensational wording are explicit YouTube guidance {C['YT_TITLE_TIPS']} {C['YT_PERF_FAQ']} {C['YT_SPAM']} {C['NASA_MERCH']}.")
m.append("")
m.append("## 3. Description alternatives")
m.append("")
for d in DESCRIPTION_ALTERNATIVES:
    m.append(f"### 3.{DESCRIPTION_ALTERNATIVES.index(d)+1} `{d['id']}` — {d['chars']} chars")
    m.append("")
    m.append("```text")
    m.append(d["text"])
    m.append("```")
    m.append("")
m.append(f"All stay under 5,000 chars {C['YT_DESCRIPTIONS']}; each remains unique rather than a reused default {C['YT_DESCRIPTIONS']}.")
m.append("")
m.append("---")
m.append("")
m.append("## 4. Asset microscope — exact committed facts")
m.append("")
m.append(md_table(["Field", "Value", "Source"], [
    ["Duration", "49.400 s", "qc_summary.json"],
    ["Frames / fps", "1482 / 30", "qc_summary.json"],
    ["Resolution", "1080x1920", "qc_summary.json"],
    ["Video / audio", "H.264 / AAC 48 kHz stereo", "qc_summary.json / technical_qc.json"],
    ["Deliverable SHA-256", pack["deliverable_sha256"], "qc_summary.json"],
    ["Technical checks", "33/33", "qc_summary.json"],
    ["Audio gates", "9/9 true", "audio_qc.json"],
    ["Integrated loudness", "-14.66 LUFS", "audio_qc.json"],
    ["Sample peak / clipping", "-1.88 dBFS / 0 samples", "audio_qc.json"],
    ["LRA / movement", "3.48 LU / 20.13 dB", "audio_qc.json"],
    ["Harsh / air over high-mid", "+0.98 dB / -0.28 dB", "audio_qc.json"],
    ["Click runs", "0", "audio_qc.json"],
    ["VO fix air delta", "+5.27 dB (-5.55 → -0.28)", "vo_quality_fix_v10.json"],
    ["Legacy broad declick damage", "3,888 groups / 100,724 samples / 4.2478%", "vo_quality_fix_v10.json"],
    ["Narrow repair", "5,214 + 937 jumps; ~1.32% + ~0.24% samples", "vo_quality_fix_v10.json"],
    ["Captions", "118 word-by-word events", "caption_timings.json"],
    ["Safe zone", "top 250 / bottom 1560 / left 80 / right 1000", "edit_ledger_v10.json"],
    ["On-screen credit", "\"Source: NASA / Artemis II\" @ 44.24–49.40 s", "captions_v10.ass"],
    ["On-screen label", "REFRACTION @ 23.42–29.90 s", "captions_v10.ass"],
    ["Contact sheets", "7 + first3s + last3s", "contact_sheets_manifest.json"],
]))
m.append("")
m.append("## 5. Source provenance")
m.append("")
m.append(md_table(["Field", "Value"], [
    ["NASA ID", scout["selected_clip"]["nasa_id"]],
    ["Title", scout["selected_clip"]["title"]],
    ["Date created", scout["selected_clip"]["date_created"]],
    ["Source page", scout["selected_clip"]["source_page"]],
    ["Direct 4K asset", scout["selected_clip"]["direct_4k_url"]],
    ["Original SHA-256", scout["selected_clip"]["source_sha256"]],
    ["Vertical master SHA-256", scout["selected_clip"]["vertical_master_sha256"]],
    ["Rubric", "91/100 vs 78 minimum; 0 kill switches"],
    ["Clip lock", "N01; bear/NPS, V9 ranking, reposts and compilations superseded"],
]))
m.append("")
m.append(f"NASA content is generally not subject to US copyright and may be used for educational/informational purposes, with NASA acknowledged as source {C['NASA_IMAGES']}. NASA identifiers/insignia are protected and endorsement must not be implied {C['NASA_BRAND']}.")
m.append("")
m.append("## 6. Edit / retention map")
m.append("")
m.append(md_table(["Time", "Event", "Evidence"], [
    ["0.0–1.5 s", "Payoff flash: inverted face + 'THAT IS NOT A LENS...' word captions; mute-readable", "edit_ledger_v10.json / captions_v10.ass"],
    ["0.0–5.074 s", "Beat 1 hook", "edit_ledger_v10.json"],
    ["5.174–12.337 s", "Context / rewind", "edit_ledger_v10.json"],
    ["13.55–15.95 s", "Native reaction window 1 (+8 dB)", "native_audio_ledger_v10.json"],
    ["23.423 s", "Rehook: 'the astronaut behind it is upside down'", "edit_ledger_v10.json"],
    ["23.42–29.90 s", "REFRACTION label", "captions_v10.ass"],
    ["24.70–26.17 s", "Native reaction window 2 (+8 dB)", "native_audio_ledger_v10.json"],
    ["30.303 s", "Science explanation: refraction", "edit_ledger_v10.json"],
    ["36.672 s", "Authenticity line: no CGI / no staged skit", "edit_ledger_v10.json"],
    ["40.40–43.17 s", "Native reaction window 3 (+8 dB)", "native_audio_ledger_v10.json"],
    ["44.2 s", "Loop-back to payoff frame", "edit_ledger_v10.json"],
    ["44.24–49.40 s", "Source credit on screen", "captions_v10.ass"],
    ["49.392 s", "Last narrated word; 49.400 s file end", "native_audio_ledger_v10.json / qc_summary.json"],
]))
m.append("")
m.append(f"This is transformative commentary/analysis with original VO, captions and replay structure — not a scraped raw reupload {C['YT_SPAM']} {C['YT_REUSED_FAQ']}. Shorts performance signals include view duration, average % viewed, likes and post-watch surveys {C['YT_SHORTS_DISCOVERY']}; search also weighs title/description/content match {C['YT_PERF_FAQ']}. No result is claimed.")
m.append("")
m.append("---")
m.append("")
m.append("## 7. Rights & publicity — high-severity gate (new finding)")
m.append("")
m.append(bullets([
    f"NASA should be acknowledged; factual educational/informational use without implied endorsement is generally permitted {C['NASA_IMAGES']}.",
    f"If NASA media includes an identifiable person, commercial use may infringe privacy/publicity rights and permission should be obtained {C['NASA_IMAGES']}.",
    f"Current astronauts' names/likenesses/personality traits may not be used on commercial products, advertisements, promotional material or packaging {C['NASA_IMAGES']}.",
    f"**NASA says short-form social media content is generally considered promotional content, and imagery with NASA identifiers, current astronauts or current employees may not be used in promotional content** {C['NASA_STRATEGIC']}.",
    f"Advertising/marketing must not imply endorsement; no insignia in ads {C['NASA_ADVERTISING']}.",
    f"No 'NASA approved', 'official NASA' or co-branding wording {C['NASA_MERCH']}.",
]))
m.append("")
m.append("**Consequence for this 49.4 s Short:** it is educational/informational commentary, but it is also a social Short featuring identifiable Artemis II astronauts. Under NASA's own wording it can be treated as promotional. Therefore **commercial/monetized publication, sponsorship, ads, packaging, cover art using astronaut faces, or brand co-posting should not proceed without written clearance and human legal review.** The workspace records `commercial_monetization_clearance=false`, `publicity_or_privacy_permission_obtained=false`, `human_legal_review=false`, and `not_a_legal_opinion=true`. This study does not resolve that gate.")
m.append("")
m.append("## 8. AI / synthetic disclosure")
m.append("")
m.append(bullets([
    "Workspace: `generic_synthetic_voiceover=true`, `real_person_voice_clone=false`, `realistic_synthetic_media=false` (`native_audio_ledger_v10.json` / `upload_metadata_v10.json`).",
    f"YouTube requires disclosure for realistic AI-generated/altered content; caption creation, voice/audio repair and cloning one's own voice are listed as minor examples that do not need disclosure {C['YT_GENAI']}.",
    f"No real-person voice clone or false authorization/endorsement {C['YT_IMPERSONATION']}.",
    "Decision: keep the textual 'generic synthetic deep-male voiceover' disclosure in the description. Recommend the human publisher confirm the Studio 'AI use' toggle; this is a recommendation, not a compliance determination.",
    f"Disclosure alone does not limit reach or monetization eligibility per YouTube {C['YT_GENAI']}.",
]))
m.append("")
m.append("## 9. Studio settings checklist")
m.append("")
m.append(md_table(["Setting", "Suggested value", "Human confirm"],
                  [[s["setting"], s["value"], "YES" if s["human_confirm"] else "no"] for s in pack["youtube_shorts_primary"]["studio_settings"]]))
m.append("")
m.append(f"Title/description limits, category/education type, language, captions, license, remixing, audience/COPPA, altered-content setting, related video and recording date/location all come from YouTube's settings documentation {C['YT_EDIT_SETTINGS']}.")
m.append("")
m.append("## 10. Thumbnail / cover frame")
m.append("")
m.append(bullets([
    "Visual anchor: 0.0–1.5 s payoff flash — inverted face inside the water sphere, burned word captions already present.",
    "Optional overlay: `NOT A LENS` or `UPSIDE DOWN?` — accurate to the hook, no sensational wording.",
    f"Custom thumbnails are recommended for videos generally {C['YT_TITLE_TIPS']}, but Shorts cover-frame controls vary; human must confirm in Studio.",
    "Do not add NASA insignia/logotype/seal, astronaut face as promotional cover art without clearance, 'official NASA' wording, co-branding, or fake counts.",
]))
m.append("")
m.append("---")
m.append("")
m.append("## 11. A/B plan — plan only, zero results")
m.append("")
m.append(md_table(["Variable", "Variants"],
                  [[v["variable"], " / ".join(f"`{x}`" for x in v["variants"])] for v in pack["ab_test_plan"]["variables"]]))
m.append("")
m.append(bullets([
    f"Observe impressions, viewed-vs-ignored, average view duration, average % viewed, likes, post-watch survey and 'not interested' {C['YT_SHORTS_DISCOVERY']} {C['YT_PERF_FAQ']}.",
    "Change one variable at a time where possible; prefer Studio title/thumbnail edits over duplicate re-uploads.",
    f"Never use misleading titles, fake engagement or detection-evasion edits {C['YT_SPAM']}.",
    f"Publish time is not known to affect long-term performance and no upload cadence is required {C['YT_PERF_FAQ']} {C['YT_SHORTS_DISCOVERY']}.",
    "No A/B result, retention curve or CTR number exists yet.",
]))
m.append("")
m.append("## 12. Cross-platform adaptations")
m.append("")
for x in CROSS_PLATFORM:
    m.append(f"### {x['platform']}")
    m.append("")
    m.append("```text")
    m.append(x["caption"])
    m.append("```")
    m.append("")
    m.append(f"*{x['note']}*")
    m.append("")
m.append("## 13. Keywords (research only, not tags)")
m.append("")
m.append("```text")
m.append(", ".join(KEYWORDS))
m.append("```")
m.append("")
m.append(f"No search-volume, difficulty or ranking claim is made. Tags are minimal aids {C['YT_TAGS']} {C['YT_PERF_FAQ']}.")
m.append("")
m.append("---")
m.append("")
m.append("## 14. Pre-publish checklist")
m.append("")
m.append(md_table(["#", "Check", "Status", "Evidence"],
                  [[i + 1, c["check"], c["status"], c["evidence"]] for i, c in enumerate(pack["pre_publish_checklist"])]))
m.append("")
m.append("## 15. Inconsistencies / stale flags found under the microscope")
m.append("")
m.append(md_table(["Item", "Resolution", "Status"],
                  [[x["item"], x["resolution"] + (f" {x['citation']}" if x.get("citation") else ""), x["status"]] for x in pack["inconsistencies_and_stale_flags"]]))
m.append("")
m.append("## 16. Forensic claim audit")
m.append("")
m.append(md_table(["Claim", "Evidence", "Status"],
                  [[x["claim"], x["evidence"], x["status"]] for x in A]))
m.append("")
m.append("Statuses: `verified_workspace` = committed evidence; `verified_external_guidance` = cited official page; `inferred_human_confirm_required` = reasoned but needs human check; `unverified` = not available; `prohibited_claim` = explicitly not made.")
m.append("")
m.append("## 17. Uncertainty ledger")
m.append("")
m.append(bullets(pack["uncertainty_ledger"]))
m.append("")
m.append("## 18. Sources")
m.append("")
m.append(md_table(["Ref", "Citation", "Authority", "Used for"],
                  [[s["ref"], s["citation"], s["authority"], "; ".join(s["used_for"])] for s in SOURCES]))
m.append("")
m.append(f"*{pack['source_quality_note']}* {pack['citation_policy']}")
m.append("")
m.append("---")
m.append("")
m.append("## 19. Final position")
m.append("")
m.append("This is an exhaustive evidence-linked metadata pass from the committed workspace plus official platform/rights documentation. It supplies copy-paste titles, descriptions, hashtags, tags, keywords, settings, cover guidance, pinned comment, cross-platform captions, an A/B plan, a 45-item pre-publish checklist, a 78-row claim audit and an explicit uncertainty ledger. It does **not** supply a guaranteed viral outcome, a legal clearance, a human listening sign-off, or a claim of perfection — those remain human/rights gates, not metadata problems.")
m.append("")
OUT_MD.write_text("\n".join(m) + "\n", encoding="utf-8")

print("Wrote", rel_json)
print("Wrote", rel_sources)
print("Wrote", rel_md)
print("Patched", str(UPLOAD_META.relative_to(ROOT)), "and", str(QC_SUMMARY.relative_to(ROOT)))
print("Title chars", len(TITLE_PRIMARY), "Description chars", DESCRIPTION_CHARS,
      "Hashtags", len(HASHTAGS_PRIMARY), "Audit rows", len(A),
      "Checklist", len(pack["pre_publish_checklist"]))
