# V11 - Kya isse safely upload kar sakte hain? (Decision card)

> **Seedha jawab:** *File Studio me daalna (Private/Unlisted) ho sakta hai. **Public + monetized / promotional** abhi "safely" NAHI keh sakta.* Ye V10 Short aur V11 long-form idea **dono** par lagu hai, kyunki dono ek hi NASA clip `art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman` use karte hain [6](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman).

**Edition:** `v11_upload_safety_decision_2026-11-05` · **HEAD:** `50e20f8396549b9ebae8e929df858dc5eca280d4` · **Status:** evidence summary, NOT legal advice

---

## 0. Teen sawalon ka table

| Kya karna chahte hain | Jawab | Kyun |
| --- | --- | --- |
| Studio me file daalna, **Private / Unlisted**, sirf khud review ke liye | HAAN (technically) - lekin clearance ka matlab NAHI | YouTube khud kehta hai: *upload* = file import, *publish* = sabke liye available [1](https://support.google.com/youtube/answer/57407?hl=en). Private/Unlisted ka matlab koi public audience nahi, koi monetization nahi. Phir bhi ye koi legal clearance ya approval nahi hai. |
| **Public**, lekin non-monetized, factual / educational commentary, credit ke saath, bina endorsement | KAM RISK - par main "pakka safely" ka certificate NAHI de sakta | NASA: educational/informational use generally allowed; 'factual manner that does not imply endorsement may be used without needing explicit permission' + NASA ko source acknowledge karo [3](https://www.nasa.gov/nasa-brand-center/images-and-media/). **LEKIN** is clip me identifiable current astronauts / possible CSA personnel hain; NASA kehta hai identifiable person ke commercial use me privacy/publicity rights aur permission [3](https://www.nasa.gov/nasa-brand-center/images-and-media/), aur short-form social generally promotional mana jata hai [5](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/). Long-form bhi agar channel/brand growth ke liye hai to promotional mana ja sakta hai. Isliye lower-risk lane hai, certified-safe nahi. |
| **Monetized / ad / sponsor / brand post / thumbnail me astronaut ka chehra / 'official NASA' / logo** | NAHI - abhi bilkel nahi | NASA: current astronauts ke naam, likeness ya personality traits 'commercial products, advertisements, promotional material' me display nahi kiye ja sakte [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/); NASA khud unki taraf se likeness permission nahi de sakta [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/). 'official NASA', 'NASA approved' aur identifiers promotional material me prohibited hain [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/). Written clearance + identifiable persons ki permission + human legal review zaroori hai. Workspace flags bhi `false` hain [7](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json). |

---

## 1. Pehle 'upload' aur 'publish' alag karein

YouTube official: *"When you **upload** a video, the video file is imported to YouTube. When you **publish** a video, the video is made available for anyone to watch."* [1](https://support.google.com/youtube/answer/57407?hl=en)

Isliye **Private / Unlisted** upload technically possible hai - lekin iska matlab ye **nahi** ke rights clear ho gaye. Visibility `Public` karte hi asli sawal shuru hota hai. Monetization toggle bhi alag se hai (sirf YPP members ke liye) [1](https://support.google.com/youtube/answer/57407?hl=en).

---

## 2. NASA ne khud kya likha hai (exact quotes)

> NASA content ... generally are not subject to copyright in the United States. You may use this material for educational or informational purposes. — [3](https://www.nasa.gov/nasa-brand-center/images-and-media/)

> NASA content used in a factual manner that does not imply endorsement may be used without needing explicit permission. NASA should be acknowledged as the source of the material. — [3](https://www.nasa.gov/nasa-brand-center/images-and-media/)

> If a NASA image, audio, video or media includes an identifiable person, using the media for commercial purposes may infringe that person's right of privacy or publicity, and permission should be obtained from the person. — [3](https://www.nasa.gov/nasa-brand-center/images-and-media/)

> Astronauts or employees who are currently employed by NASA cannot have their names, likenesses or other personality traits displayed ... on any commercial products, advertisements, promotional material or commercial product packaging. — [3](https://www.nasa.gov/nasa-brand-center/images-and-media/)

> Imagery with NASA identifiers ..., current astronauts, or current employees may not be used in promotional content. Short-form social media content generally is considered promotional content. — [5](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/)

> Use of terms like 'NASA approved,' 'NASA collection,' 'official NASA,' ... is prohibited. Use of NASA identifiers in promotional materials ... is prohibited. — [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/)

> As a statement of fact, you can acknowledge your SI tool includes NASA source material, but do not imply any review or permission was granted by NASA for its specific use. ... References like 'according to NASA' or similar are prohibited in SI products. — [3](https://www.nasa.gov/nasa-brand-center/images-and-media/)

> Copyright check results aren't final. ... Likeness detection ... may be removed later if it violates our policies. — [2](https://support.google.com/youtube/answer/57407?hl=en)

---

## 3. "Pakka safe" kyun nahi keh sakta

- Identifiable current astronauts / possible CSA personnel is clip me hain; koi likhit permission record nahi [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) [7](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json).
- NASA short-form social ko generally promotional kehta hai; long-form bhi promotional mana ja sakta hai agar brand/channel growth ke liye ho [5](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/).
- Workspace me `human_legal_review=false`, `commercial_monetization_clearance=false`, `publicity_or_privacy_permission_obtained=false`, `not_a_legal_opinion=true` [7](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json).
- YouTube ke Checks pass hona bhi proof nahi: 'Copyright check results aren't final', aur Likeness detection ke baad bhi policy violation par video hat sakta hai [2](https://support.google.com/youtube/answer/57407?hl=en).
- AI/synthetic VO ke saath NASA SI guidance bhi lagu ho sakti hai: 'according to NASA' jaisa attribution SI products me prohibited, insignia SI-generated imagery ke saath nahi, aur 'NASA ne review/permission diya' ka matlab nahi nikalna [3](https://www.nasa.gov/nasa-brand-center/images-and-media/). Hamara on-screen credit `Source: NASA / Artemis II` ek factual source disclosure hai - ye theek hai, lekin script me 'NASA ke mutabiq...' se bachna hoga.
- YouTube par reused-content / altered-or-synthetic disclosure / audience (COPPA) / misleading metadata jaise alag settings bhi hain; inka human decision abhi pending hai [1](https://support.google.com/youtube/answer/57407?hl=en) [8](workspace://research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md).
- Main legal advisor nahi hoon aur ye legal opinion nahi hai.

---

## 4. Agar phir bhi **public, non-monetized, educational** karna hai - minimum checklist

1. Visibility pehle **Private** ya **Unlisted** rakhein; public tabhi jab niche wale steps ho jayein [1](https://support.google.com/youtube/answer/57407?hl=en).
2. Monetization **OFF** rakhein jab tak written clearance na ho [1](https://support.google.com/youtube/answer/57407?hl=en) [3](https://www.nasa.gov/nasa-brand-center/images-and-media/).
3. Sirf factual, educational/informational commentary; koi invented date, injury, 'No CGI', '100% real' ya view-count claim nahi [3](https://www.nasa.gov/nasa-brand-center/images-and-media/).
4. On-screen + description me `Source: NASA / Artemis II` aur `no endorsement implied` [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) [6](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman).
5. Koi 'official NASA', 'NASA approved', insignia, logotype, mission patch, co-branding ya sponsor mention nahi [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
6. Astronauts ke naam / chehre ko promotional ya thumbnail/cover art ke taur par istemal na karein [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
7. Agar script/VO AI-assisted hai: 'according to NASA' na likhein; sirf factual source disclosure; koi implied review/permission na ho [3](https://www.nasa.gov/nasa-brand-center/images-and-media/).
8. Altered / synthetic content disclosure, Language, Audience / made-for-kids, License aur Shorts-remixing settings human confirm karein [1](https://support.google.com/youtube/answer/57407?hl=en).
9. Title/description/tags/hashtags me koi unrelated ya misleading metadata nahi [1](https://support.google.com/youtube/answer/57407?hl=en).
10. YouTube Checks ke result ko final clearance na samjhein [2](https://support.google.com/youtube/answer/57407?hl=en).

> Ye checklist risk **kam** karti hai, **khatam** nahi karti. Isko bhi human legal review se guzarana chahiye.

---

## 5. "Haan, safely" kab bolega

- NASA Office of Communications se **written clearance / approval** for the intended use (questions: nasa-merchandise-&-brand-team@mail.nasa.gov) [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
- Identifiable astronauts / possible CSA personnel ki **apni likhit permission** (NASA unki taraf se nahi de sakta) [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
- Ek **insaan ka legal review** jo is specific clip, script, thumbnail, monetization plan aur region (PK) ko dekhe [7](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json).
- Ya alternative: aisa footage use karein jisme koi identifiable current astronaut na ho / chehra na pehchana jaye [3](https://www.nasa.gov/nasa-brand-center/images-and-media/).
- Tab bhi: no endorsement wording, no insignia, credit + no-endorsement-implied, correct disclosures, no guaranteed outcome.

---

## 6. Jo main claim NAHI karta

**Non-claim register (sab `false`):** `legal_opinion`, `legal_clearance`, `human_legal_review`, `commercial_monetization_clearance`, `written_astronaut_or_csa_permission`, `publicity_or_privacy_permission_obtained`, `youtube_checks_pass_proves_safety`, `upload_or_publish_performed`, `video_rendered_for_v11`, `human_creative_approval`, `nasa_endorsement`, `official_nasa_status`, `guaranteed_no_takedown`, `guaranteed_monetization`, `perfection_or_zero_risk`

---

## 7. Sources

| Ref | Source | Authority | Used for |
| --- | --- | --- | --- |
| [1](https://support.google.com/youtube/answer/57407?hl=en) | Upload YouTube videos - YouTube Help | official_youtube_help | Upload = file imported; Publish = made available for anyone to watch. Private / Unlisted / Public visibility. Checks are not final. Likeness detection. Monetization toggle for YPP. |
| [2](https://support.google.com/youtube/answer/57407?hl=en) | Upload YouTube videos - Checks section - YouTube Help | official_youtube_help | Exact: 'Copyright check results aren't final'; future manual claims, strikes and settings edits may impact the video. Likeness detection scans for enrolled creators' faces; video may be removed later if it violates policies. |
| [3](https://www.nasa.gov/nasa-brand-center/images-and-media/) | NASA Images and Media Usage Guidelines | official_nasa_guidance | Educational/informational use generally permitted; factual manner + no endorsement + acknowledge NASA = no explicit permission needed. Commercial use and identifiable persons need clearance. SI/AI attribution rules. |
| [4](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) | NASA Advertising Guidelines | official_nasa_guidance | 'official NASA', 'NASA approved' and similar wording prohibited; NASA identifiers prohibited in promotional materials; current astronauts' likenesses cannot be displayed in advertisements or marketing material; NASA may not grant likeness rights on their behalf. |
| [5](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) | NASA Strategic Partnerships - Promotional Content | official_nasa_guidance | Publicly available content usable if Media Usage Guidelines followed; promotional content with NASA identifiers / current astronauts may not be used; short-form social generally considered promotional; no endorsement or co-branding. |
| [6](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) | NASA image detail - Fun with Water Bubbles (Artemis II) | official_nasa_asset | The single locked source clip used by both V10 and the V11 idea. |
| [7](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json) | V10 rights ledger and QC evidence | workspace_evidence | Recorded flags: no written astronaut/CSA permission, no human legal review, no commercial monetization clearance, not a legal opinion. |
| [8](workspace://research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md) | V11 long-form idea selection study | workspace_evidence | The idea whose upload safety is being asked about; idea selected, video not built. |

---

## 8. Ek line ka nateeja

**Private review upload = haan (sirf file daalna). Public educational = kam risk par certified-safe nahi. Monetized / ad / sponsor / 'official NASA' / astronaut chehra thumbnail par = abhi NAHI.** Pehle written clearance + identifiable-person permission + human legal review, tab aage. Main legal opinion nahi de raha.

