#!/usr/bin/env python3
"""Build the V11 upload-safety decision card (question: "kya safely upload kar sakte hain?").

Run from repo root:
    python research/long_form_viral_idea_v11/build_upload_safety_v11.py

Writes ONLY these two files (does not touch the idea study or any other evidence):
  UPLOAD_SAFETY_V11.md
  upload_safety_v11.json

Applies to BOTH the existing V10 Short and the proposed V11 long-form idea,
because both use the same locked NASA Artemis II water-bubble clip.

This is a rights/policy evidence summary, NOT legal advice and NOT a clearance.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "long_form_viral_idea_v11"
MD = OUT / "UPLOAD_SAFETY_V11.md"
JS = OUT / "upload_safety_v11.json"

EDITION = "v11_upload_safety_decision_2026-11-05"
HEAD_EXPECTED = "50e20f8396549b9ebae8e929df858dc5eca280d4"
NASA_ID = "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"

SOURCES = [
    {"n": 1, "id": "YT_UPLOAD", "title": "Upload YouTube videos - YouTube Help",
     "url": "https://support.google.com/youtube/answer/57407?hl=en", "authority": "official_youtube_help",
     "used_for": "Upload = file imported; Publish = made available for anyone to watch. Private / Unlisted / Public visibility. Checks are not final. Likeness detection. Monetization toggle for YPP."},
    {"n": 2, "id": "YT_CHECKS", "title": "Upload YouTube videos - Checks section - YouTube Help",
     "url": "https://support.google.com/youtube/answer/57407?hl=en", "authority": "official_youtube_help",
     "used_for": "Exact: 'Copyright check results aren't final'; future manual claims, strikes and settings edits may impact the video. Likeness detection scans for enrolled creators' faces; video may be removed later if it violates policies."},
    {"n": 3, "id": "NASA_IMAGES", "title": "NASA Images and Media Usage Guidelines",
     "url": "https://www.nasa.gov/nasa-brand-center/images-and-media/", "authority": "official_nasa_guidance",
     "used_for": "Educational/informational use generally permitted; factual manner + no endorsement + acknowledge NASA = no explicit permission needed. Commercial use and identifiable persons need clearance. SI/AI attribution rules."},
    {"n": 4, "id": "NASA_ADS", "title": "NASA Advertising Guidelines",
     "url": "https://www.nasa.gov/nasa-brand-center/advertising-guidelines/", "authority": "official_nasa_guidance",
     "used_for": "'official NASA', 'NASA approved' and similar wording prohibited; NASA identifiers prohibited in promotional materials; current astronauts' likenesses cannot be displayed in advertisements or marketing material; NASA may not grant likeness rights on their behalf."},
    {"n": 5, "id": "NASA_STRATEGIC", "title": "NASA Strategic Partnerships - Promotional Content",
     "url": "https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/", "authority": "official_nasa_guidance",
     "used_for": "Publicly available content usable if Media Usage Guidelines followed; promotional content with NASA identifiers / current astronauts may not be used; short-form social generally considered promotional; no endorsement or co-branding."},
    {"n": 6, "id": "NASA_ASSET", "title": "NASA image detail - Fun with Water Bubbles (Artemis II)",
     "url": f"https://images.nasa.gov/details/{NASA_ID}", "authority": "official_nasa_asset",
     "used_for": "The single locked source clip used by both V10 and the V11 idea."},
    {"n": 7, "id": "WORKSPACE_V10", "title": "V10 rights ledger and QC evidence",
     "url": "workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json",
     "authority": "workspace_evidence", "used_for": "Recorded flags: no written astronaut/CSA permission, no human legal review, no commercial monetization clearance, not a legal opinion."},
    {"n": 8, "id": "V11_STUDY", "title": "V11 long-form idea selection study",
     "url": "workspace://research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md",
     "authority": "workspace_evidence", "used_for": "The idea whose upload safety is being asked about; idea selected, video not built."},
]


def cite(n: int) -> str:
    s = next(x for x in SOURCES if x["n"] == n)
    return f"[{s['n']}]({s['url']})"


VERDICTS = [
    {
        "id": "private_unlisted_review_upload",
        "scenario": "Studio me file daalna, **Private / Unlisted**, sirf khud review ke liye",
        "verdict": "HAAN (technically) - lekin clearance ka matlab NAHI",
        "why": ("YouTube khud kehta hai: *upload* = file import, *publish* = sabke liye available " + cite(1) +
                ". Private/Unlisted ka matlab koi public audience nahi, koi monetization nahi. "
                "Phir bhi ye koi legal clearance ya approval nahi hai."),
        "monetization": False, "public_audience": False, "clearance_needed": False,
    },
    {
        "id": "public_non_monetized_educational",
        "scenario": "**Public**, lekin non-monetized, factual / educational commentary, credit ke saath, bina endorsement",
        "verdict": "KAM RISK - par main \"pakka safely\" ka certificate NAHI de sakta",
        "why": ("NASA: educational/informational use generally allowed; 'factual manner that does not imply endorsement "
                "may be used without needing explicit permission' + NASA ko source acknowledge karo " + cite(3) +
                ". **LEKIN** is clip me identifiable current astronauts / possible CSA personnel hain; NASA kehta hai "
                "identifiable person ke commercial use me privacy/publicity rights aur permission " + cite(3) +
                ", aur short-form social generally promotional mana jata hai " + cite(5) +
                ". Long-form bhi agar channel/brand growth ke liye hai to promotional mana ja sakta hai. "
                "Isliye lower-risk lane hai, certified-safe nahi."),
        "monetization": False, "public_audience": True, "clearance_needed": "recommended_human_legal_review",
    },
    {
        "id": "monetized_promotional",
        "scenario": "**Monetized / ad / sponsor / brand post / thumbnail me astronaut ka chehra / 'official NASA' / logo**",
        "verdict": "NAHI - abhi bilkel nahi",
        "why": ("NASA: current astronauts ke naam, likeness ya personality traits 'commercial products, advertisements, "
                "promotional material' me display nahi kiye ja sakte " + cite(3) + " " + cite(4) +
                "; NASA khud unki taraf se likeness permission nahi de sakta " + cite(4) +
                ". 'official NASA', 'NASA approved' aur identifiers promotional material me prohibited hain " + cite(4) +
                ". Written clearance + identifiable persons ki permission + human legal review zaroori hai. "
                "Workspace flags bhi `false` hain " + cite(7) + "."),
        "monetization": True, "public_audience": True, "clearance_needed": True,
    },
]

NASA_QUOTES = [
    {"quote": "NASA content ... generally are not subject to copyright in the United States. You may use this material for educational or informational purposes.", "src": cite(3)},
    {"quote": "NASA content used in a factual manner that does not imply endorsement may be used without needing explicit permission. NASA should be acknowledged as the source of the material.", "src": cite(3)},
    {"quote": "If a NASA image, audio, video or media includes an identifiable person, using the media for commercial purposes may infringe that person's right of privacy or publicity, and permission should be obtained from the person.", "src": cite(3)},
    {"quote": "Astronauts or employees who are currently employed by NASA cannot have their names, likenesses or other personality traits displayed ... on any commercial products, advertisements, promotional material or commercial product packaging.", "src": cite(3)},
    {"quote": "Imagery with NASA identifiers ..., current astronauts, or current employees may not be used in promotional content. Short-form social media content generally is considered promotional content.", "src": cite(5)},
    {"quote": "Use of terms like 'NASA approved,' 'NASA collection,' 'official NASA,' ... is prohibited. Use of NASA identifiers in promotional materials ... is prohibited.", "src": cite(4)},
    {"quote": "As a statement of fact, you can acknowledge your SI tool includes NASA source material, but do not imply any review or permission was granted by NASA for its specific use. ... References like 'according to NASA' or similar are prohibited in SI products.", "src": cite(3)},
    {"quote": "Copyright check results aren't final. ... Likeness detection ... may be removed later if it violates our policies.", "src": cite(2)},
]

WHY_NOT_CERTIFIED = [
    "Identifiable current astronauts / possible CSA personnel is clip me hain; koi likhit permission record nahi " + cite(3) + " " + cite(7) + ".",
    "NASA short-form social ko generally promotional kehta hai; long-form bhi promotional mana ja sakta hai agar brand/channel growth ke liye ho " + cite(5) + ".",
    "Workspace me `human_legal_review=false`, `commercial_monetization_clearance=false`, `publicity_or_privacy_permission_obtained=false`, `not_a_legal_opinion=true` " + cite(7) + ".",
    "YouTube ke Checks pass hona bhi proof nahi: 'Copyright check results aren't final', aur Likeness detection ke baad bhi policy violation par video hat sakta hai " + cite(2) + ".",
    "AI/synthetic VO ke saath NASA SI guidance bhi lagu ho sakti hai: 'according to NASA' jaisa attribution SI products me prohibited, insignia SI-generated imagery ke saath nahi, aur 'NASA ne review/permission diya' ka matlab nahi nikalna " + cite(3) + ". Hamara on-screen credit `Source: NASA / Artemis II` ek factual source disclosure hai - ye theek hai, lekin script me 'NASA ke mutabiq...' se bachna hoga.",
    "YouTube par reused-content / altered-or-synthetic disclosure / audience (COPPA) / misleading metadata jaise alag settings bhi hain; inka human decision abhi pending hai " + cite(1) + " " + cite(8) + ".",
    "Main legal advisor nahi hoon aur ye legal opinion nahi hai.",
]

MIN_CHECKLIST = [
    "Visibility pehle **Private** ya **Unlisted** rakhein; public tabhi jab niche wale steps ho jayein " + cite(1) + ".",
    "Monetization **OFF** rakhein jab tak written clearance na ho " + cite(1) + " " + cite(3) + ".",
    "Sirf factual, educational/informational commentary; koi invented date, injury, 'No CGI', '100% real' ya view-count claim nahi " + cite(3) + ".",
    "On-screen + description me `Source: NASA / Artemis II` aur `no endorsement implied` " + cite(3) + " " + cite(6) + ".",
    "Koi 'official NASA', 'NASA approved', insignia, logotype, mission patch, co-branding ya sponsor mention nahi " + cite(4) + ".",
    "Astronauts ke naam / chehre ko promotional ya thumbnail/cover art ke taur par istemal na karein " + cite(3) + " " + cite(4) + ".",
    "Agar script/VO AI-assisted hai: 'according to NASA' na likhein; sirf factual source disclosure; koi implied review/permission na ho " + cite(3) + ".",
    "Altered / synthetic content disclosure, Language, Audience / made-for-kids, License aur Shorts-remixing settings human confirm karein " + cite(1) + ".",
    "Title/description/tags/hashtags me koi unrelated ya misleading metadata nahi " + cite(1) + ".",
    "YouTube Checks ke result ko final clearance na samjhein " + cite(2) + ".",
]

CONDITIONS_FOR_YES = [
    "NASA Office of Communications se **written clearance / approval** for the intended use (questions: nasa-merchandise-&-brand-team@mail.nasa.gov) " + cite(3) + " " + cite(4) + ".",
    "Identifiable astronauts / possible CSA personnel ki **apni likhit permission** (NASA unki taraf se nahi de sakta) " + cite(3) + " " + cite(4) + ".",
    "Ek **insaan ka legal review** jo is specific clip, script, thumbnail, monetization plan aur region (PK) ko dekhe " + cite(7) + ".",
    "Ya alternative: aisa footage use karein jisme koi identifiable current astronaut na ho / chehra na pehchana jaye " + cite(3) + ".",
    "Tab bhi: no endorsement wording, no insignia, credit + no-endorsement-implied, correct disclosures, no guaranteed outcome.",
]

NON_CLAIMS = {
    "legal_opinion": False,
    "legal_clearance": False,
    "human_legal_review": False,
    "commercial_monetization_clearance": False,
    "written_astronaut_or_csa_permission": False,
    "publicity_or_privacy_permission_obtained": False,
    "youtube_checks_pass_proves_safety": False,
    "upload_or_publish_performed": False,
    "video_rendered_for_v11": False,
    "human_creative_approval": False,
    "nasa_endorsement": False,
    "official_nasa_status": False,
    "guaranteed_no_takedown": False,
    "guaranteed_monetization": False,
    "perfection_or_zero_risk": False,
}

WORKSPACE_FLAGS = {
    "head": HEAD_EXPECTED,
    "branch": "arena/2b012328-monarch-overall-work",
    "applies_to": ["deliverables/MONARCH_CAM_Artemis_II_Upside_Down_Face_V10_Short.mp4 (V10 Short, exists)",
                   "REPLAY LAB Ep.1 long-form idea (V11, video NOT built yet)"],
    "same_nasa_clip": True,
    "nasa_id": NASA_ID,
    "v10_deliverable_sha256": "608aa065cd3c53894b96df1ebb6fa74dd3ce1e846366e40a940426b4823586a7",
}


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "or").replace("\n", " ") for x in r) + " |")
    return out


def build_md() -> str:
    m = []
    a = m.append
    a("# V11 - Kya isse safely upload kar sakte hain? (Decision card)")
    a("")
    a("> **Seedha jawab:** *File Studio me daalna (Private/Unlisted) ho sakta hai. **Public + monetized / promotional** "
      "abhi \"safely\" NAHI keh sakta.* Ye V10 Short aur V11 long-form idea **dono** par lagu hai, kyunki dono ek hi "
      f"NASA clip `{NASA_ID}` use karte hain " + cite(6) + ".")
    a("")
    a(f"**Edition:** `{EDITION}` · **HEAD:** `{HEAD_EXPECTED}` · **Status:** evidence summary, NOT legal advice")
    a("")
    a("---")
    a("")
    a("## 0. Teen sawalon ka table")
    a("")
    m.extend(table(["Kya karna chahte hain", "Jawab", "Kyun"],
                   [[v["scenario"], v["verdict"], v["why"]] for v in VERDICTS]))
    a("")
    a("---")
    a("")
    a("## 1. Pehle 'upload' aur 'publish' alag karein")
    a("")
    a("YouTube official: *\"When you **upload** a video, the video file is imported to YouTube. When you **publish** a "
      "video, the video is made available for anyone to watch.\"* " + cite(1))
    a("")
    a("Isliye **Private / Unlisted** upload technically possible hai - lekin iska matlab ye **nahi** ke rights clear "
      "ho gaye. Visibility `Public` karte hi asli sawal shuru hota hai. Monetization toggle bhi alag se hai (sirf YPP "
      "members ke liye) " + cite(1) + ".")
    a("")
    a("---")
    a("")
    a("## 2. NASA ne khud kya likha hai (exact quotes)")
    a("")
    for q in NASA_QUOTES:
        a(f"> {q['quote']} — {q['src']}")
        a("")
    a("---")
    a("")
    a("## 3. \"Pakka safe\" kyun nahi keh sakta")
    a("")
    for s in WHY_NOT_CERTIFIED:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 4. Agar phir bhi **public, non-monetized, educational** karna hai - minimum checklist")
    a("")
    for i, s in enumerate(MIN_CHECKLIST, 1):
        a(f"{i}. {s}")
    a("")
    a("> Ye checklist risk **kam** karti hai, **khatam** nahi karti. Isko bhi human legal review se guzarana chahiye.")
    a("")
    a("---")
    a("")
    a("## 5. \"Haan, safely\" kab bolega")
    a("")
    for s in CONDITIONS_FOR_YES:
        a(f"- {s}")
    a("")
    a("---")
    a("")
    a("## 6. Jo main claim NAHI karta")
    a("")
    a("**Non-claim register (sab `false`):** " + ", ".join("`" + k + "`" for k in NON_CLAIMS))
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
    a("## 8. Ek line ka nateeja")
    a("")
    a("**Private review upload = haan (sirf file daalna). Public educational = kam risk par certified-safe nahi. "
      "Monetized / ad / sponsor / 'official NASA' / astronaut chehra thumbnail par = abhi NAHI.** Pehle written "
      "clearance + identifiable-person permission + human legal review, tab aage. Main legal opinion nahi de raha.")
    a("")
    return "\n".join(m) + "\n"


def build_json() -> dict:
    return {
        "schema_version": "1.0",
        "edition": EDITION,
        "question": "Han to pooch rha hun usko ham upload karsakte hena safely",
        "short_answer": "Private/Unlisted file upload technically yes (no clearance). Public non-monetized educational = lower risk but NOT certified safe. Monetized/promotional = NO without written clearance + person permission + human legal review.",
        "not_legal_advice": True,
        "workspace": WORKSPACE_FLAGS,
        "verdict_by_scenario": VERDICTS,
        "youtube_upload_vs_publish": {
            "upload": "video file imported to YouTube",
            "publish": "made available for anyone to watch",
            "visibility_options": ["Private", "Unlisted", "Public"],
            "cite": cite(1),
        },
        "nasa_exact_quotes": NASA_QUOTES,
        "why_not_certified_safe": WHY_NOT_CERTIFIED,
        "minimum_checklist_if_public_non_monetized": MIN_CHECKLIST,
        "conditions_for_yes": CONDITIONS_FOR_YES,
        "non_claims": NON_CLAIMS,
        "sources": SOURCES,
        "files": {"study": "research/long_form_viral_idea_v11/UPLOAD_SAFETY_V11.md",
                  "pack": "research/long_form_viral_idea_v11/upload_safety_v11.json",
                  "idea_study": "research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md",
                  "v10_rights_ledger": "production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json"},
    }


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    save(JS, build_json())
    MD.write_text(build_md(), encoding="utf-8")
    print("Wrote", MD.relative_to(ROOT))
    print("Wrote", JS.relative_to(ROOT))
    print("Verdicts:", [(v["id"], v["verdict"]) for v in VERDICTS])
    print("NASA quotes:", len(NASA_QUOTES), "| sources:", len(SOURCES), "| non-claims all false:", all(not v for v in NON_CLAIMS.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
