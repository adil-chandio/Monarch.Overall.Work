#!/usr/bin/env python3
"""V11 immediate-action card: user reported "Monetization on ha" on the uploaded Short.

Run from repo root:
    python research/long_form_viral_idea_v11/build_monetization_action_v11.py

Writes ONLY:
  MONETIZATION_ON_IMMEDIATE_ACTION_V11.md
  monetization_on_action_v11.json

This is a rights/policy evidence summary + an operational checklist. NOT legal advice,
NOT a clearance, NOT a verdict that a violation occurred, NOT a takedown prediction.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "long_form_viral_idea_v11"
MD = OUT / "MONETIZATION_ON_IMMEDIATE_ACTION_V11.md"
JS = OUT / "monetization_on_action_v11.json"

EDITION = "v11_monetization_on_action_2026-11-05"
HEAD = "990969474f79bcb8f6a96fe75c6061ee1ca0ef6d"
NASA_ID = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"

SOURCES = [
    {"n": 1, "id": "YT_TURN_OFF_ADS", "title": "Turn off ads for individual videos - YouTube Help",
     "url": "https://support.google.com/youtube/answer/6332943?hl=en", "authority": "official_youtube_help",
     "used_for": "Exact 5-step OFF procedure for an already-uploaded video."},
    {"n": 2, "id": "YT_MONETIZE", "title": "Choose how you want to monetize - YouTube Help",
     "url": "https://support.google.com/youtube/answer/94522?hl=en", "authority": "official_youtube_help",
     "used_for": "'By turning on ads for videos on YouTube, you confirm that you have all the necessary rights to the visual and audio elements of those videos.' Also: turning on ads doesn't auto-open ads; automated/human review happens; Shorts Feed ads require the Shorts Monetization Module in Earn."},
    {"n": 3, "id": "YT_SHORTS_POLICY", "title": "YouTube Shorts monetization policies - YouTube Help",
     "url": "https://support.google.com/youtube/answer/12504220?hl=en", "authority": "official_youtube_help",
     "used_for": "Shorts Feed ads are channel-level revenue sharing via the Shorts Monetization Module; 'Non-original Shorts ... or compilations with no original content added' are ineligible examples; content must follow advertiser-friendly guidelines; views before module acceptance are not eligible."},
    {"n": 4, "id": "YT_UPLOAD", "title": "Upload YouTube videos - YouTube Help",
     "url": "https://support.google.com/youtube/answer/57407?hl=en", "authority": "official_youtube_help",
     "used_for": "Monetization toggle exists inside upload/Details for YPP; Checks results aren't final; Likeness detection."},
    {"n": 5, "id": "NASA_IMAGES", "title": "NASA Images and Media Usage Guidelines",
     "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/", "authority": "official_nasa_guidance",
     "used_for": "Commercial-use section: identifiable persons, permission, current astronauts' likenesses, no endorsement, educational/informational general permission."},
    {"n": 6, "id": "NASA_ADS", "title": "NASA Advertising Guidelines",
     "url": "https://www.nasa.gov/nasa-brand-center/advertising-guidelines/", "authority": "official_nasa_guidance",
     "used_for": "Prohibited 'official NASA' / 'NASA approved' wording, identifiers in promotional material, and written advertising-request approval path."},
    {"n": 7, "id": "NASA_STRATEGIC", "title": "NASA Strategic Partnerships - Promotional Content",
     "url": "https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/", "authority": "official_nasa_guidance",
     "used_for": "Short-form social generally considered promotional content; imagery with current astronauts may not be used in promotional content."},
    {"n": 8, "id": "WORKSPACE_V10", "title": "V10 upload metadata + rights flags",
     "url": "workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/upload_metadata_v10.json",
     "authority": "workspace_evidence", "used_for": "rights.full_legal_review=false; description explicitly says 'no written permission, human legal review or legal opinion is claimed'; claims.human_creative_approval=false; status=draft_not_published."},
    {"n": 9, "id": "SAFETY_CARD", "title": "V11 upload-safety decision card",
     "url": "workspace://research/long_form_viral_idea_v11/UPLOAD_SAFETY_V11.md",
     "authority": "workspace_evidence", "used_for": "Prior verdict: monetized/promotional scenario = 'NAHI - abhi bilkel nahi' until written clearance + person permission + human legal review."},
    {"n": 10, "id": "DESC_AUDIT", "title": "V11 live-Short description audit",
     "url": "workspace://research/long_form_viral_idea_v11/LIVE_SHORT_DESCRIPTION_AUDIT_V11.md",
     "authority": "workspace_evidence", "used_for": "Screenshots matched committed description blocks 1-6; hashtag line unconfirmed; AI-use toggle and visibility unconfirmed."},
]


def cite(n: int) -> str:
    s = next(x for x in SOURCES if x["n"] == n)
    return f"[{s['n']}]({s['url']})"


FINDINGS = [
    {"id": "F1", "title": "Ads ON ka matlab rights ka izhaar",
     "text": ("YouTube official: *\"By turning on ads for videos on YouTube, you confirm that you have all the necessary "
              "rights to the visual and audio elements of those videos.\"* " + cite(2) +
              " Hamare committed ledger me `full_legal_review=false` aur likhit permission `false` hai " + cite(8) +
              ". Aapki apni description bhi kehti hai *\"no written permission, human legal review or legal opinion is "
              "claimed\"* " + cite(8) + ". Ye do baatein aapas me match nahi karti — isliye ye sabse pehle dekhne wali jagah hai.")},
    {"id": "F2", "title": "NASA ka commercial / identifiable-person gate seedha yahan lagta hai",
     "text": ("NASA: *\"If a NASA image, audio, video or media includes an identifiable person, using the media for "
              "commercial purposes may infringe that person's right of privacy or publicity, and permission should be "
              "obtained from the person.\"* aur *\"Astronauts or employees who are currently employed by NASA cannot "
              "have their names, likenesses or other personality traits displayed ... on any commercial products, "
              "advertisements, promotional material or commercial product packaging.\"* " + cite(5) +
              " Is clip me identifiable astronauts / possible CSA personnel hain " + cite(8) +
              ". NASA short-form social ko generally promotional kehta hai " + cite(7) + ".")},
    {"id": "F3", "title": "Shorts ki monetization do level ki hoti hai",
     "text": ("Shorts Feed ads **channel-level** revenue sharing hai: *\"Only monetizing partners who've accepted the "
              "Shorts Monetization Module can earn ad revenue from Shorts\"* " + cite(3) +
              ". Isliye 'channel YPP ON', 'is video ke ads ON' aur 'Shorts module accepted' teen alag baatein hain. "
              "Individual video ka monetization OFF kiya ja sakta hai " + cite(1) +
              ", lekin **Shorts Feed pool se is ek video ko alag se kaise hataya jaye, iski guarantee mujhe official "
              "docs me nahi mili** — `Earn` section human check karein. Main yahan koi certainty claim nahi karta.")},
    {"id": "F4", "title": "Ads ON ≠ ads chal gaye ≠ paisa mila",
     "text": ("YouTube: *\"Choosing to turn on ads doesn't mean that ads will automatically open on a video. Before any "
              "ads show up, the video will go through a standard process including automated or human reviews\"* " + cite(2) +
              ". Aur Shorts module accept karne se **pehle** wale views revenue-sharing ke liye eligible nahi " + cite(3) +
              ". Isliye main yahan koi ad-run, revenue, strike ya takedown ka dawa nahi karta — na hi koi violation ka faisla.")},
    {"id": "F5", "title": "Description achhi thi, par wo clearance nahi deti",
     "text": ("Credit + no-endorsement + synthetic VO disclosure + 'no legal opinion claimed' sab theek hain " + cite(10) +
              ". Lekin wo sab **risk kam** karte hain, **commercial-use ki ijazat** nahi dete. Pehle wala decision-card "
              "bhi yahi kehta tha: monetized/promotional = abhi nahi " + cite(9) + ".")},
]

STEPS_COMPUTER = [
    "YouTube Studio kholein → left menu **Content**.",
    "Is water-wale Short ke aage **Monetization** column par click karein.",
    "Dropdown me **Off** chunein.",
    "**Save** dabayein. " + cite(1),
]
STEPS_MOBILE = [
    "YouTube Studio app → bottom **Menu → Content**.",
    "Video select karein → **Edit** → **Monetization**.",
    "**OFF** chunein → **Back** → **Save**. " + cite(2),
]
STEPS_AFTER = [
    "**Earn** section me Shorts Monetization Module ka status human check karein (channel-level) " + cite(3) + ".",
    "**AI use** toggle (Attributes) abhi bhi unconfirmed hai — human confirm karein " + cite(10) + ".",
    "**Visibility** confirm karein; chahein to clearance tak **Unlisted / Private** rakhna ek ihtiyati option hai (aapka faisla, koi guarantee nahi) " + cite(4) + ".",
    "**Thumbnail** me astronaut ka chehra na ho " + cite(5) + ".",
    "**Description** waisa hi rakhein — mat badlein, mat hataayein; credit + no-endorsement + disclosure wahin rehne dein " + cite(10) + ".",
    "Video **delete** karne ka mashwara main nahi de raha; ye aapka faisla hai. Main koi bhi natija (safe / hataya jayega / strike) claim nahi karta.",
]

CLEARANCE_PATH = [
    "NASA Office of Communications ko **written request / approval** for the intended commercial use "
    "(public contact: `nasa-merchandise-&-brand-team@mail.nasa.gov`, specific-video questions 202-358-0309) " + cite(5) + " " + cite(6) + ".",
    "Identifiable astronauts / possible CSA personnel ki **apni likhit permission** — NASA unki taraf se nahi de sakta " + cite(5) + " " + cite(6) + ".",
    "Ek **insaan ka legal review** jo is clip, script, thumbnail, monetization plan aur region (PK) ko dekhe " + cite(8) + ".",
    "Tab jaakar monetization dobara ON karne ka faisla **aap** karein; main tab bhi 'guaranteed safe' nahi kahunga.",
]

NON_CLAIMS = {
    "legal_opinion": False,
    "legal_clearance": False,
    "human_legal_review": False,
    "commercial_monetization_clearance": False,
    "written_astronaut_or_csa_permission": False,
    "agent_turned_monetization_off": False,
    "agent_verified_studio_state": False,
    "violation_occurred_verdict": False,
    "takedown_or_strike_predicted": False,
    "ads_actually_shown": False,
    "revenue_earned": False,
    "shorts_pool_exclusion_guaranteed": False,
    "youtube_checks_pass_proves_safety": False,
    "human_creative_approval": False,
    "upload_or_publish_performed_by_agent": False,
    "safety_certified": False,
    "guaranteed_no_future_claim": False,
    "perfection_or_zero_risk": False,
}


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "or").replace("\n", " ") for x in r) + " |")
    return out


def build_md() -> str:
    m = []
    a = m.append
    a("# V11 — \"Monetization ON hai\" → abhi kya karein")
    a("")
    a("> **Seedha jawab:** ghabrane ki zarurat nahi, par **is Short ka monetization abhi OFF kar dein**. "
      "Ye wahi scenario hai jiske liye pehle kaha tha *\"monetized / promotional = abhi nahi\"* " + cite(9) + ". "
      "Ye koi violation ka faisla, legal notice ya takedown ki prediction **nahi** — bas sabse kam-risk wala agla qadam hai.")
    a("")
    a(f"**Edition:** `{EDITION}` · **HEAD:** `{HEAD}` · **Source clip:** `{NASA_ID}`")
    a("**Reported by user:** `Monetization on ha` · **Agent-verified on Studio:** ❌ nahi (main Studio/API access nahi rakhta)")
    a("")
    a("---")
    a("")
    a("## 1. Pehla kaam (2 minute) — monetization OFF")
    a("")
    a("**Computer / Studio web:**")
    for i, s in enumerate(STEPS_COMPUTER, 1):
        a(f"{i}. {s}")
    a("")
    a("**Mobile / Studio app:**")
    for i, s in enumerate(STEPS_MOBILE, 1):
        a(f"{i}. {s}")
    a("")
    a("> Official: *\"You can turn off monetization for any videos you've already uploaded.\"* " + cite(1))
    a("")
    a("## 2. Uske baad ye 6 cheezein")
    a("")
    for i, s in enumerate(STEPS_AFTER, 1):
        a(f"{i}. {s}")
    a("")
    a("---")
    a("")
    a("## 3. Kyun itni jaldi? (5 forensic findings)")
    a("")
    for f in FINDINGS:
        a(f"### {f['id']} — {f['title']}")
        a("")
        a(f["text"])
        a("")
    a("---")
    a("")
    a("## 4. Teen alag cheezein — confuse na hon")
    a("")
    m.extend(table(["Setting", "Kahan", "Iska matlab"], [
        ["Channel YPP / Earn modules", "Studio → Earn " + cite(2), "Channel-level; Shorts Feed ads ke liye Shorts Monetization Module chahiye " + cite(3)],
        ["Is **ek video** ka Monetization ON/OFF", "Studio → Content → video → Monetization " + cite(1), "Jise abhi OFF karna hai"],
        ["Ads sach me chalna", "Automated / human review ke baad " + cite(2), "ON ka matlab ads chal gaye **nahi**; koi revenue claim nahi"],
    ]))
    a("")
    a("---")
    a("")
    a("## 5. Monetization dobara ON kab?")
    a("")
    for s in CLEARANCE_PATH:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 6. Jo main claim NAHI karta (sab `false`)")
    a("")
    a(", ".join("`" + k + "`" for k in NON_CLAIMS))
    a("")
    a("---")
    a("")
    a("## 7. Sources")
    a("")
    m.extend(table(["Ref", "Source", "Authority", "Used for"],
                   [[f"[{s['n']}]({s['url']})", s["title"].replace("|", "or"), s["authority"],
                     s["used_for"].replace("|", "or")] for s in SOURCES]))
    a("")
    a("---")
    a("")
    a("## 8. Ek line")
    a("")
    a("**Description theek thi ✅ — monetization ON wala hissa abhi badal dein ❌→OFF.** Phir written clearance + "
      "identifiable-person permission + human legal review ke baad aap khud faisla karein. Main koi legal opinion, "
      "clearance, violation verdict, takedown prediction ya 'ab sab safe hai' ka certificate nahi de raha.")
    a("")
    return "\n".join(m) + "\n"


def build_json() -> dict:
    return {
        "schema_version": "1.0",
        "edition": EDITION,
        "head_at_writing": HEAD,
        "question": "Monetization on ha",
        "short_answer": "Turn this Short's monetization OFF now (Studio Content -> Monetization -> Off -> Save). Not a violation verdict; a risk-reduction step. Channel-level Shorts module needs separate human check.",
        "not_legal_advice": True,
        "user_reported_monetization": "on",
        "agent_verified_studio_state": False,
        "nasa_asset_id": NASA_ID,
        "findings": FINDINGS,
        "immediate_steps_computer": STEPS_COMPUTER,
        "immediate_steps_mobile": STEPS_MOBILE,
        "follow_up_steps": STEPS_AFTER,
        "clearance_path_before_re_enabling": CLEARANCE_PATH,
        "three_distinct_settings": [
            {"level": "channel_yPP_and_earn_modules", "where": "Studio > Earn", "citation": cite(2)},
            {"level": "per_video_monetization_toggle", "where": "Studio > Content > video > Monetization", "citation": cite(1)},
            {"level": "ads_actually_served", "where": "after automated or human review", "citation": cite(2)},
        ],
        "non_claims": NON_CLAIMS,
        "sources": SOURCES,
        "related_files": [
            "research/long_form_viral_idea_v11/UPLOAD_SAFETY_V11.md",
            "research/long_form_viral_idea_v11/LIVE_SHORT_DESCRIPTION_AUDIT_V11.md",
            "production/monarch-cam/caught_on_camera_commentary_v10/review/final/upload_metadata_v10.json",
        ],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    JS.write_text(json.dumps(build_json(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD.write_text(build_md(), encoding="utf-8")
    print("Wrote", MD.relative_to(ROOT))
    print("Wrote", JS.relative_to(ROOT))
    print("Findings:", len(FINDINGS), "| sources:", len(SOURCES),
          "| non-claims all false:", all(not v for v in NON_CLAIMS.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
