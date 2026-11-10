#!/usr/bin/env python3
"""Build the V10 YouTube category + pinned comment copy-paste pack.

Run from the repository root:
    python production/monarch-cam/caught_on_camera_commentary_v10/build_category_pinned_comment_v10.py

This is the LAST-MILE pack: it writes the two dedicated deliverables and patches the
existing upload metadata pack, forensic metadata pack, study and QC evidence index.
It is deliberately evidence-linked (official YouTube Help / Data API / NASA guidance)
and deliberately makes no reach, retention, engagement, legal-clearance, human
listening, perfection or human creative-approval claim.

Re-run this AFTER build_viral_metadata_v10.py if that study is ever regenerated.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/caught_on_camera_commentary_v10"
REVIEW = BASE / "review" / "final"

OUT_MD = REVIEW / "category_and_pinned_comment_v10.md"
OUT_JSON = REVIEW / "category_and_pinned_comment_v10.json"
UPLOAD_META = REVIEW / "upload_metadata_v10.json"
VIRAL_JSON = REVIEW / "viral_metadata_v10.json"
VIRAL_MD = REVIEW / "viral_metadata_study_v10.md"
SOURCES_LEDGER = REVIEW / "viral_metadata_sources_v10.json"
QC_SUMMARY = REVIEW / "qc_summary.json"

DELIVERABLE = "deliverables/MONARCH_CAM_Artemis_II_Upside_Down_Face_V10_Short.mp4"
DELIVERABLE_SHA = "608aa065cd3c53894b96df1ebb6fa74dd3ce1e846366e40a940426b4823586a7"
DELIVERABLE_BYTES = 34495086
NASA_ID = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"
NASA_PAGE = f"https://images.nasa.gov/details/{NASA_ID}"

SOURCES = [
    {"ref": 1, "id": "YT_EDIT_SETTINGS", "title": "Edit video settings - YouTube Help",
     "url": "https://support.google.com/youtube/answer/57404?hl=en", "authority": "official_help",
     "used_for": "Category under SHOW MORE; Education sub-fields; tags' minimal discovery role; comments and ratings setting"},
    {"ref": 2, "id": "YT_UPLOAD", "title": "Upload YouTube videos - YouTube Help",
     "url": "https://support.google.com/youtube/answer/57407?hl=en", "authority": "official_help",
     "used_for": "Category field, advanced settings, vertical/Shorts upload details"},
    {"ref": 3, "id": "YT_COMMENTS", "title": "Post & interact with comments - YouTube Help",
     "url": "https://support.google.com/youtube/answer/6000964?hl=en", "authority": "official_help",
     "used_for": "Pin mechanics, advanced-features requirement, mobile expansion, comment preview not guaranteed, links become hyperlinks"},
    {"ref": 4, "id": "YT_STUDIO_COMMENTS", "title": "Review & reply to comments - YouTube Help",
     "url": "https://support.google.com/youtube/answer/9482367?hl=en", "authority": "official_help",
     "used_for": "Studio > Community > Pin; Shorts content-type filter; unpin"},
    {"ref": 5, "id": "YT_SPAM", "title": "Spam Policy - YouTube Help",
     "url": "https://support.google.com/youtube/answer/2801973?hl=en", "authority": "official_policy",
     "used_for": "Asking for comments is allowed; coercion, rewards, fake engagement, comment spam and malicious clickbait are not"},
    {"ref": 6, "id": "YT_HASHTAGS", "title": "Find playlists & videos using hashtags - YouTube Help",
     "url": "https://support.google.com/youtube/answer/6390658?hl=en", "authority": "official_help",
     "used_for": "Up to 3 hashtags above title; >60 ignored; unrelated/descriptive-tag stuffing prohibited"},
    {"ref": 7, "id": "YT_TAGS", "title": "Add tags to your videos - YouTube Help",
     "url": "https://support.google.com/youtube/answer/146402?hl=en", "authority": "official_help",
     "used_for": "Tags mainly correct common misspellings and otherwise play a minimal role in discovery"},
    {"ref": 8, "id": "YT_CATEGORIES_API", "title": "VideoCategories: list — YouTube Data API",
     "url": "https://developers.google.com/youtube/v3/docs/videoCategories/list", "authority": "official_developer_docs",
     "used_for": "Category list is region-specific (regionCode); category IDs come from the API"},
    {"ref": 9, "id": "NASA_IMAGES", "title": "NASA Brand Center - Images and Media",
     "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/", "authority": "official_nasa_guidance",
     "used_for": "Acknowledge NASA; no implied endorsement; insignia and identifiable-person restrictions"},
    {"ref": 10, "id": "NASA_STRATEGIC", "title": "NASA Strategic Partnerships (brand guidance)",
     "url": "https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/", "authority": "official_nasa_guidance",
     "used_for": ("Exact wording: 'Short-form social media content generally is considered promotional content' and "
                  "'Imagery with ... current astronauts ... may not be used in promotional content'; no endorsement/co-branding. "
                  "The sources ledger's /nasa-brand-center/strategic-partnerships/ URL redirects here.")},
]


def cite(n: int) -> str:
    s = next(x for x in SOURCES if x["ref"] == n)
    return f"[{s['ref']}]({s['url']})"


PINNED_PRIMARY = (
    "Which moment made you replay — the face flipping upside down, or the loop back at the end?\n\n"
    "Curved water bends light (refraction), so the sphere acts like a tiny liquid lens.\n\n"
    'Source: NASA / Artemis II, "Fun with Water Bubbles". NASA is credited; no endorsement implied.'
)

PINNED_ALTERNATIVES = [
    {
        "id": "B", "label": "Science-first / value",
        "text": (
            "Curved water acts like a liquid lens: light bends through the sphere and the face behind it flips.\n\n"
            "What caught your eye first — the upside-down face around 23s, or the crew's reaction?\n\n"
            'Source: NASA / Artemis II ("Fun with Water Bubbles"). NASA credited; no endorsement implied.'
        ),
        "use_case": "Agar aap comment ko chhota 'science note' banana chahte hain, discussion ke saath.",
        "why": "Pehli line mein video ka asli explanation; sawal doosri line mein; credit aakhir mein.",
    },
    {
        "id": "C", "label": "Source-first / rights-heavy",
        "text": (
            f'Source: NASA, "Fun with Water Bubbles" (Artemis II) — {NASA_PAGE}\n\n'
            "Independent commentary and replay analysis; NASA's native crew audio is retained. "
            "NASA is credited, no endorsement implied.\n\n"
            "What do you think bends the light here?"
        ),
        "use_case": "Jab source attribution sabse upar chahiye (promotional / monetized context mein sabse cautious).",
        "why": "Official source link pehle; URLs comments mein hyperlink ban jate hain " + cite(3) + ". "
               "NASA endorsement ka koi claim nahi " + cite(9) + ".",
    },
    {
        "id": "D", "label": "One-line / Shorts mobile",
        "text": (
            "Refraction: curved water flips the face. Which frame made you replay? "
            "Source: NASA / Artemis II — NASA credited, no endorsement implied."
        ),
        "use_case": "Mobile par jahan comment preview chhota dikhta hai; ek line mein hook + credit.",
        "why": "Pinned comment preview ki jagah guaranteed nahi hai, isliye pehli line hi sab kuch keh de " + cite(3) + ".",
    },
]

CATEGORY = {
    "primary": {
        "studio_label": "Science & Technology",
        "commonly_documented_api_id": 28,
        "api_id_caveat": ("28 is a widely documented third-party mapping, not re-verified here via "
                          "videoCategories.list (no API key). Studio shows the label, not the ID — "
                          "you do not need the ID to set it. " + cite(8)),
        "prior_study_suggestion": "Education / science experiment (viral_metadata_v10.json, before this pack)",
    },
    "alternate": {
        "studio_label": "Education",
        "commonly_documented_api_id": 27,
        "api_id_caveat": "27 is a widely documented third-party mapping; see the same caveat " + cite(8) + ".",
        "education_type": "science experiment",
        "education_type_other_option": "real life application",
        "extra_fields_studio_may_ask": ["Type", "Problems", "Academic system", "Level",
                                        "Exam, course, or standard"],
        "extra_fields_note": ("Education khud 'science experiment' aur 'real life application' Type deta hai "
                              + cite(1) + " " + cite(2) + " — dono is clip par fit baithte hain. "
                              "Academic system / Level / Exam fields bhi dikhte hain, lekin inhe khali "
                              "chhod sakte hain; ye 49.4 s general-audience Short kisi exam ya grade se "
                              "bound nahi hai."),
    },
    "where_to_set": [
        "YouTube Studio (desktop) -> Content -> click the video -> Details -> SHOW MORE -> Category " + cite(1) + " " + cite(2),
        "Upload ke time bhi: Studio -> CREATE -> Upload videos -> Edit -> SHOW MORE -> Category " + cite(2),
        "Baad me badalna ho to: Studio -> Content -> video -> settings -> Save " + cite(1),
    ],
    "why_primary": [
        "Video ek science / physics explainer hai: curved water sphere refraction se image flip karta hai; "
        "NASA Artemis II ka official clip + replay analysis. Isliye topical bucket Science & Technology hai.",
        "Ye 49.4 s vertical Short hai — 8 beats, word-by-word captions aur loop-back ke saath commentary — "
        "koi structured lesson, how-to ya exam-aligned lecture nahi. Isliye main isse broad science bucket "
        "me rakhta hoon.",
        "Pichhli forensic study ne `Education / science experiment` suggest kiya tha aur wo **bhi bilkul "
        "sahih hai**: YouTube khud Education ke liye `science experiment` Type deta hai " + cite(1) + " " + cite(2) +
        ". Ye pack us purane suggestion ko 'galat' qarar nahi deta; sirf do valid options me se aik final "
        "pick lock karta hai. Dono se reach / retention ka koi guaranteed farq claim nahi kiya ja sakta.",
    ],
    "decision_note": ("Mera final pick Science & Technology hai; Education + Type `science experiment` "
                      "equally valid alternate hai. Ye aik categorization judgment hai, koi official "
                      "ranking, discovery ya engagement rule nahi. Aapko Studio me khud confirm karna hai."),
    "why_not_education_as_primary": ("Agar aap channel ko explicitly educational series ke taur par classify "
                                     "karna chahte hain, ya aapke Studio / region me `Science & Technology` "
                                     "na dikhe, to Education chunlein — Type = `science experiment` (ya "
                                     "`real life application`) aur academic fields khali. Ye koi galat "
                                     "jawab nahi hai."),
    "region_note": ("Category list region-specific hoti hai (regionCode) " + cite(8) + ". Agar aapke Studio "
                    "mein 'Science & Technology' na dikhe, to 'Education' chunlein — dono hi galat nahi hain."),
    "no_ranking_claim": ("Official wording sirf ye hai: 'Select a category so viewers can find your video "
                         "more easily' " + cite(1) + " " + cite(2) + "; tags bhi 'minimal role' play karte "
                         "hain " + cite(1) + " " + cite(7) + ". Category se Shorts feed reach, retention, "
                         "views ya comments badhne ka koi guaranteed asar claim nahi kiya ja sakta."),
    "operational_advice": ("Channel ki baqi science/refraction clips par bhi yahi category rakhein taake "
                           "classification consistent rahe — ye meri operational salah hai, koi official "
                           "ranking rule nahi."),
    "human_must_confirm": True,
}

PINNED_MECHANICS = [
    "Comments on rakhein: Settings -> Comments and ratings " + cite(1) + "; comments off/limited hone par pin kaam nahi karega " + cite(3) + ".",
    "Channel par 'Advanced features' enable karein — pin karne ke liye zaroori hai, aur poore channel par dikhne me 24 ghante tak lag sakte hain " + cite(3) + ".",
    "Apna comment post karein, phir uske three-dot menu -> Pin -> PIN " + cite(3) + "; ya Studio -> Community -> Published -> More -> Pin " + cite(4) + ".",
    "Shorts ke comments bhi Studio ke 'Content type' filter mein hain, to pin wahan se bhi kiya ja sakta hai " + cite(4) + ".",
    "Mobile par viewer ko comment section expand karna padta hai; pinned comment 'view all' kholne par sabse pehle dikhta hai. Comment preview mein dikhna guaranteed nahi hai " + cite(3) + ".",
    "Isliye pehli line chhoti aur sabse important rakhi hai — sawal — taake truncated preview me bhi kaam kare.",
    "Ek hi templated comment ko kai videos par repeat na karein; naya comment pin karne par purana apne aap unpin ho jata hai " + cite(3) + " " + cite(4) + ".",
]

PINNED_WHY = [
    "Pehli line ek specific, asani se jawab dene wala sawal hai jo video ke do sachche moments se juda hai: "
    "~23.42 s par REFRACTION / ulta chehra aur ~44.24 s par loop-back + on-screen credit.",
    "Genuine sawal poochna allowed hai; lekin incentive, coercion, 'sub-for-sub', repetitive engagement bait ya fake engagement mana hai " + cite(5) + ". Is comment me koi reward / 'like karo' / 'subscribe karo' nahi hai.",
    "Doosri line comment ko khud me value deti hai (refraction) aur video ki asli explanation se match karti hai — malicious clickbait nahi " + cite(5) + ".",
    "Teesri line on-screen credit 'Source: NASA / Artemis II' aur description ke attribution ko mirror karti hai; 'NASA credited; no endorsement implied' likha hai " + cite(9) + ".",
    "Comment me koi hashtag nahi: hashtag rules title/description par hain, up to 3 title ke paas, >60 ignore, aur unrelated/descriptive stuffing prohibited " + cite(6) + ".",
    "Koi unverified claim nahi: na 'No CGI', na astronaut ke naam, na 'official NASA', na invented date, view count ya audience result.",
]

PINNED_AVOID = [
    "Like/comment/subscribe ke badle inaam, giveaway, coercion, 'sub-for-sub' ya forced engagement " + cite(5) + ".",
    "'Comment YES', 'tag a friend', 'click the heart' jaisa low-effort repetitive engagement bait " + cite(5) + ".",
    "Aisa hook jo video deliver na kare (malicious clickbait), ya comments me traffic lane ke liye repetitive/deceptive messages " + cite(5) + ".",
    "'Official NASA', 'NASA approved', NASA endorsement, insignia/logo, ya current astronauts ke naam/likeness ka promotional istemal " + cite(9) + " " + cite(10) + ".",
    "Hashtag stuffing, unrelated tags, ALL CAPS, emoji-spam ya description wale descriptive tags ko comment me chipkana " + cite(6) + ".",
    "'No CGI' / '100% real' jaise unverified authenticity claims — workspace me human_full_motion_review=false hai.",
    "Guaranteed viral / retention / views / RPM ya audience-result ka koi claim.",
]

CAVEATS = [
    "Ye drafting recommendations hain; koi upload, publish, category set ya comment pin actually kiya nahi gaya (status draft_not_published).",
    "human_creative_approval=false, human_legal_review=false, commercial_monetization_clearance=false, publicity_or_privacy_permission_obtained=false — sab workspace evidence me waise hi hain.",
    "High-severity unresolved gate: NASA ke exact wording ke mutabiq 'Short-form social media content generally is considered promotional content' aur 'Imagery with ... current astronauts ... may not be used in promotional content'. Is Short me identifiable current astronauts / possible CSA personnel hain; isliye commercial/monetized ya kisi bhi promotional publication se pehle written clearance aur human legal review zaroori hai. Ye pinned comment us gate ko theek nahi karta " + cite(10) + ".",
    "Official platform/NASA documentation legal opinion nahi hai.",
    "Category ya pinned comment se reach, retention, comments, CTR, RPM ya virality ka koi guaranteed natija claim nahi kiya jata.",
]


def code(text: str) -> list[str]:
    return ["```text", *text.splitlines(), "```"]


def build_md() -> str:
    m: list[str] = []
    a = m.append
    a("# V10 — Category & Pinned Comment (copy-paste pack)")
    a("")
    a("> **Roman Urdu note:** Category ka aik clear final jawab aur pin comment ke 4 tayyar versions neeche hain. "
      "Ye evidence-linked drafting hai — \"viral\", reach ya engagement ki guarantee nahi, aur na hi legal/human sign-off.")
    a("")
    a(f"**Status:** `draft_not_published` — koi upload/publish/category-set/pin nahi kiya gaya  ")
    a(f"**Applies to:** `{DELIVERABLE}`  ")
    a(f"**SHA-256:** `{DELIVERABLE_SHA}` · **Size:** {DELIVERABLE_BYTES:,} bytes · 49.40 s vertical Short  ")
    a("**Machine-readable pack:** `production/monarch-cam/caught_on_camera_commentary_v10/review/final/category_and_pinned_comment_v10.json`")
    a("")
    a("---")
    a("")
    a("## 0. TL;DR — exactly kya set karein")
    a("")
    a("**Category:** `Science & Technology`  ")
    a("*(Alternate, equally valid: `Education` + Type `science experiment` — agar Studio me ye label na mile ya aap educational series chahte hain — §1.4)*")
    a("")
    a("**Pinned comment — seedha copy/paste karein:**")
    a("")
    m.extend(code(PINNED_PRIMARY))
    a("")
    a(f"*({len(PINNED_PRIMARY)} characters, {len(PINNED_PRIMARY.splitlines())} lines)*")
    a("")
    a("---")
    a("")
    a("## 1. Category decision")
    a("")
    a("### 1.1 Primary")
    a("")
    a(f"| Field | Value |\n| --- | --- |\n| Studio label | **{CATEGORY['primary']['studio_label']}** |")
    a(f"| Commonly documented API ID | `{CATEGORY['primary']['commonly_documented_api_id']}` (API-only, Studio me ID ki zarurat nahi) |")
    a(f"| Pichhli study ka suggestion | `{CATEGORY['primary']['prior_study_suggestion']}` |")
    a(f"| Human confirm | `YES` — aapko Studio me khud select karna hai |")
    a("")
    a(f"**ID caveat:** {CATEGORY['primary']['api_id_caveat']}")
    a("")
    a("### 1.2 Studio me kahan milta hai")
    a("")
    for s in CATEGORY["where_to_set"]:
        a(f"- {s}")
    a("")
    a("### 1.3 Primary kyun")
    a("")
    for s in CATEGORY["why_primary"]:
        a(f"- {s}")
    a("")
    a("### 1.4 Alternate — `Education`")
    a("")
    a(f"| Field | Value |\n| --- | --- |\n| Studio label | `{CATEGORY['alternate']['studio_label']}` |")
    a(f"| Commonly documented API ID | `{CATEGORY['alternate']['commonly_documented_api_id']}` (same caveat) |")
    a(f"| Education Type | `{CATEGORY['alternate']['education_type']}` (ya `{CATEGORY['alternate']['education_type_other_option']}`) |")
    a(f"| Extra fields Studio mang sakta hai | {', '.join('`'+x+'`' for x in CATEGORY['alternate']['extra_fields_studio_may_ask'])} |")
    a("")
    a(f"{CATEGORY['alternate']['extra_fields_note']}")
    a("")
    a(f"> {CATEGORY['why_not_education_as_primary']}")
    a("")
    a(f"> **Region note:** {CATEGORY['region_note']}")
    a("")
    a("### 1.5 Jo claim NAHI kiya ja raha")
    a("")
    a(f"> **Decision note:** {CATEGORY['decision_note']}")
    a("")
    a(f"- {CATEGORY['no_ranking_claim']}")
    a(f"- {CATEGORY['operational_advice']}")
    a("")
    a("---")
    a("")
    a("## 2. Pinned comment — primary version")
    a("")
    a(f"**Label:** `A — Replay question (recommended)` · **{len(PINNED_PRIMARY)} characters**")
    a("")
    m.extend(code(PINNED_PRIMARY))
    a("")
    a("### 2.1 Is version ko aise banaya gaya hai")
    a("")
    for s in PINNED_WHY:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 3. Teen alternate versions")
    a("")
    a("| Ver | Label | Characters | Kab use karein |")
    a("| --- | --- | --- | --- |")
    for v in PINNED_ALTERNATIVES:
        a(f"| `{v['id']}` | {v['label']} | {len(v['text'])} | {v['use_case']} |")
    a("")
    for v in PINNED_ALTERNATIVES:
        a(f"### 3.{['B','C','D'].index(v['id'])+1} `{v['id']}` — {v['label']} ({len(v['text'])} chars)")
        a("")
        m.extend(code(v["text"]))
        a("")
        a(f"*Kyun:* {v['why']}")
        a("")
    a("---")
    a("")
    a("## 4. Pin kaise karein (practical steps)")
    a("")
    for i, s in enumerate(PINNED_MECHANICS, 1):
        a(f"{i}. {s}")
    a("")
    a("---")
    a("")
    a("## 5. In cheezon se bachein")
    a("")
    for s in PINNED_AVOID:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 6. Caveats / unresolved gates")
    a("")
    for s in CAVEATS:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 7. Sources")
    a("")
    a("| Ref | Source | Authority | Used for |")
    a("| --- | --- | --- | --- |")
    for s in SOURCES:
        a(f"| [{s['ref']}]({s['url']}) | {s['title']} | `{s['authority']}` | {s['used_for']} |")
    a("")
    a("**Workspace evidence:** `upload_metadata_v10.json`, `viral_metadata_v10.json`, "
      "`viral_metadata_study_v10.md`, `rights_ledger_v10.json`, `edit_ledger_v10.json`, "
      "`caption_timings.json`, `qc_summary.json`.")
    a("")
    a("---")
    a("")
    a("## 8. Final position")
    a("")
    a("Category ka aik hi final pick: **Science & Technology** (agar aapke Studio / region me na mile, "
      "ya aap channel ko educational series banana chahte hain, to `Education` + Type `science experiment` "
      "— dono valid hain, koi galat jawab nahi). Pinned comment ka primary: §0 wala replay-question "
      "version. Baqi 3 versions A/B test ke liye hain — koi natija, reach, retention, comments ya "
      "virality guarantee nahi. NASA credit aur 'no endorsement implied' har version me hai, lekin "
      "promotional/commercial clearance ka gate abhi bhi human legal review ke liye khula hai.")
    a("")
    return "\n".join(m) + "\n"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_json() -> dict:
    return {
        "schema_version": "1.0",
        "edition": "v10_category_and_pinned_comment_pack",
        "status": "draft_not_published",
        "deliverable": DELIVERABLE,
        "deliverable_sha256": DELIVERABLE_SHA,
        "deliverable_bytes": DELIVERABLE_BYTES,
        "video_facts_used": {
            "duration_seconds": 49.4,
            "format": "1080x1920 vertical Short, 30 fps",
            "refraction_label_timeline": "23.42-29.90 s",
            "loop_back_and_credit_timeline": "44.24-49.40 s",
            "on_screen_credit": "Source: NASA / Artemis II",
            "nasa_id": NASA_ID,
            "nasa_page": NASA_PAGE,
            "beats": 8, "vo_words": 118, "caption_events": 118,
        },
        "category": CATEGORY,
        "pinned_comment": {
            "primary": {
                "id": "A", "label": "Replay question (recommended)",
                "text": PINNED_PRIMARY, "characters": len(PINNED_PRIMARY),
                "lines": len(PINNED_PRIMARY.splitlines()),
            },
            "alternatives": [
                {"id": v["id"], "label": v["label"], "text": v["text"],
                 "characters": len(v["text"]), "use_case": v["use_case"], "why": v["why"]}
                for v in PINNED_ALTERNATIVES
            ],
            "why_primary": PINNED_WHY,
            "mechanics": PINNED_MECHANICS,
            "avoid": PINNED_AVOID,
        },
        "caveats": CAVEATS,
        "claims": {
            "human_creative_approval": False,
            "human_native_audio_listening": False,
            "human_legal_review": False,
            "commercial_monetization_clearance": False,
            "legal_opinion": False,
            "upload_or_publish_performed": False,
            "reach_or_engagement_guaranteed": False,
            "virality_guaranteed": False,
            "perfection_claim": False,
            "technical_qc_pass": True,
            "technical_qc_reference": "review/final/qc_summary.json",
        },
        "sources": SOURCES,
        "workspace_evidence": [
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/upload_metadata_v10.json",
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/viral_metadata_v10.json",
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/viral_metadata_study_v10.md",
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json",
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/edit_ledger_v10.json",
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/qc_summary.json",
        ],
        "generated_by": "build_category_pinned_comment_v10.py",
        "note": ("Last-mile pack: run AFTER build_viral_metadata_v10.py if the forensic study is "
                 "regenerated, so the category / pinned-comment patches are re-applied."),
    }


def patch_existing(pack: dict) -> None:
    md_rel = str(OUT_MD.relative_to(ROOT))
    json_rel = str(OUT_JSON.relative_to(ROOT))

    # 1) Copy-paste upload metadata pack: keep its editorial content, refresh the two fields.
    um = load(UPLOAD_META)
    um["category"] = {
        "primary": CATEGORY["primary"]["studio_label"],
        "alternate": CATEGORY["alternate"]["studio_label"],
        "alternate_education_type": CATEGORY["alternate"]["education_type"],
        "where_to_set": CATEGORY["where_to_set"],
        "region_note": CATEGORY["region_note"],
        "no_ranking_claim": CATEGORY["no_ranking_claim"],
        "human_must_confirm": True,
        "evidence": json_rel,
    }
    um["pinned_comment"] = PINNED_PRIMARY
    um["pinned_comment_alternatives"] = [
        {"id": v["id"], "label": v["label"], "text": v["text"], "characters": len(v["text"])}
        for v in PINNED_ALTERNATIVES
    ]
    um["category_and_pinned_comment_pack"] = json_rel
    um["category_and_pinned_comment_study"] = md_rel
    um["claims"]["human_creative_approval"] = False
    save(UPLOAD_META, um)

    # 2) Forensic metadata pack: supersede the earlier Education suggestion and old pinned text.
    vm = load(VIRAL_JSON)
    vm["youtube_shorts_primary"]["category"] = {
        "primary": CATEGORY["primary"]["studio_label"],
        "previously_suggested": "Education",
        "superseded_by": json_rel,
        "alternate": CATEGORY["alternate"]["studio_label"],
        "alternate_education_type": CATEGORY["alternate"]["education_type"],
        "why_primary": CATEGORY["why_primary"],
        "no_ranking_claim": CATEGORY["no_ranking_claim"],
        "human_must_confirm": True,
    }
    vm["youtube_shorts_primary"]["pinned_comment"] = PINNED_PRIMARY
    vm["youtube_shorts_primary"]["pinned_comment_alternatives"] = [
        {"id": v["id"], "label": v["label"], "text": v["text"], "characters": len(v["text"])}
        for v in PINNED_ALTERNATIVES
    ]
    for row in vm["youtube_shorts_primary"]["studio_settings"]:
        if row.get("setting") == "Category":
            row["value"] = ("Science & Technology (primary); Education only if needed "
                            "(see category_and_pinned_comment_v10.json)")
    vm["category_and_pinned_comment_pack"] = json_rel
    vm["category_and_pinned_comment_study"] = md_rel
    save(VIRAL_JSON, vm)

    # 3) Study: keep it readable — refresh the copy-paste pinned block, category row and A/B row.
    study = VIRAL_MD.read_text(encoding="utf-8")
    old_pinned = ("Which frame made you replay it — the flip around 23s or the loop back at 44s? "
                  "Source: NASA / Artemis II.")
    pointer = (f"> **Updated recommendation:** category aur pinned comment ka final, evidence-linked "
               f"pack `{md_rel}` me hai. Neeche wali category/pinned values usi se sync ki gayi hain.")
    if pointer not in study:
        anchor = ("**Sources ledger:** `production/monarch-cam/caught_on_camera_commentary_v10/"
                  "review/final/viral_metadata_sources_v10.json`\n")
        study = study.replace(anchor, anchor + "\n" + pointer + "\n", 1)
    # Do the single-line A/B table row FIRST, then the fenced copy-paste block with
    # exact fence context. A blind global replace would inject newlines into the table.
    ab_old = "| Pinned comment | `" + old_pinned + "` / `No pinned comment` |"
    ab_new = ("| Pinned comment | `A — replay question (recommended)` / "
              "`D — one-line Shorts` / `No pinned comment` |")
    study = study.replace(ab_old, ab_new)
    fence_old = "```text\n" + old_pinned + "\n```"
    fence_new = "```text\n" + PINNED_PRIMARY.replace("\n\n", "\n") + "\n```"
    study = study.replace(fence_old, fence_new)
    study = study.replace(
        "| Category | Education / science experiment (suggested) | YES |",
        "| Category | Science & Technology (primary); Education only if needed | YES |")
    VIRAL_MD.write_text(study, encoding="utf-8")

    # 4) Sources ledger: register the last-mile pack's official URLs as an addendum.
    #    Do not rewrite the original `sources` array (its refs are web_search result IDs).
    sl = load(SOURCES_LEDGER)
    sl["category_and_pinned_comment_pack"] = json_rel
    sl["category_and_pinned_comment_study"] = md_rel
    sl["category_and_pinned_comment_sources"] = [
        {"ref": s["ref"], "id": s["id"], "title": s["title"], "url": s["url"],
         "authority": s["authority"], "used_for": s["used_for"],
         "fetched": True, "citation": f"[{s['ref']}]({s['url']})"}
        for s in SOURCES
    ]
    save(SOURCES_LEDGER, sl)

    # 5) QC evidence index: add the two new deliverables.
    qc = load(QC_SUMMARY)
    for item in (json_rel, md_rel):
        if item not in qc["evidence"]:
            qc["evidence"].append(item)
    save(QC_SUMMARY, qc)


def main() -> int:
    REVIEW.mkdir(parents=True, exist_ok=True)
    pack = build_json()
    save(OUT_JSON, pack)
    OUT_MD.write_text(build_md(), encoding="utf-8")
    patch_existing(pack)
    print("Wrote", OUT_MD.relative_to(ROOT))
    print("Wrote", OUT_JSON.relative_to(ROOT))
    print("Patched", UPLOAD_META.relative_to(ROOT), VIRAL_JSON.relative_to(ROOT),
          VIRAL_MD.relative_to(ROOT), SOURCES_LEDGER.relative_to(ROOT),
          QC_SUMMARY.relative_to(ROOT))
    print("Category primary:", CATEGORY["primary"]["studio_label"])
    print("Pinned primary chars:", len(PINNED_PRIMARY))
    for v in PINNED_ALTERNATIVES:
        print("  alt", v["id"], v["label"], len(v["text"]), "chars")
    print("Sources:", len(SOURCES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
