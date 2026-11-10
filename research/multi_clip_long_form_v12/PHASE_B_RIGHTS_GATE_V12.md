# V12 PHASE B - Executable Per-Clip Rights Gate

> **Ye hard stop ko sirf likha nahi, chalaya bhi gaya.** 8 dossiers, har ek me 18 fields `null`, `clearance_status=pending`, `human_legal_review=false`. Generator me ek executable test hai jo **farzi "cleared" slot ko reject karta hai** — yani gate ko jumlon se bypass nahi kiya ja sakta. Koi clip download/clear nahi hua.

**Edition:** `v12_phase_bc_rights_gate_and_script_draft` · **API runs:** `42895703914`, `42905149277` · **Status:** `ALL_8_DOSSIERS_PENDING_NO_CLIP_CLEARED`
**Machine-readable:** `phase_b_rights_gate_v12.json`, `PHASE_C_SCRIPT_DRAFT_V12.md`, `phase_c_script_draft_v12.json`

---

## 0. Seedha jawab

- **Gate executable hai:** `fabricated cleared slot with NULL fields` → `rejected=True` (expected `True`).
- **18 fields**, **8 kill conditions**, **5 attribution templates**, **8 dossiers** — sab pending.
- **Real API probe targets** har dossier me hain, lekin wo **benchmarks** hain, source clips nahi. Written permission bhi reused-content eligibility guarantee nahi karta [7](https://support.google.com/youtube/answer/1311392?hl=en).
- **V10/Short clip EXCLUDED** (`art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman`) — kisi bhi slot me nahi.

---

## 1. 18 fields - kya verify karna hai

| # | Field | Verify | Pass | Fail |
| --- | --- | --- | --- | --- |
| 1 | official_source_url | The exact first-party page where the asset is published, not a repost or a search result. | URL resolves on the rights-holder's own domain and the asset ID matches. | Aggregator, mirror, embed, social repost, or an unverifiable link. |
| 2 | nasa_or_agency_asset_id | The agency's own catalogue / asset identifier for this exact file. | A stable agency asset ID is recorded and matches the downloaded file. | Only a YouTube video ID, or no catalogue ID at all. |
| 3 | licence_basis | The written licence or public-domain statement covering THIS file, with its URL and retrieval date. | Licence text explicitly permits this use, including commercial use if monetization is intended. | Assumed 'public domain', 'educational use', 'fair use' as a licence, or a generic site-wide statement that excludes some media. |
| 4 | third_party_copyrighted_material_check | Whether the frame or audio contains anyone else's content (music, logo, broadcast graphic, another creator's footage). | Written 'none found' after frame + audio inspection, or a documented clearance for each item. | Uninspected, or contains uncleared third-party material. |
| 5 | identifiable_persons_check | Whether any identifiable person appears and what consent/permissions exist. | No identifiable person, or documented permission plus the required likeness/AI-likeness review. | Identifiable person with no documented permission. |
| 6 | current_astronaut_or_employee_check | Whether the person is a current agency employee/crew member shown in a way that could read as promotional. | Confirmed not current personnel, or written clearance from the agency. | Current crew / employee in promotional framing, or status unconfirmed. |
| 7 | promotional_or_cover_art_use | Whether the asset is used to promote a product, service, or as cover art / thumbnail hero. | Editorial/educational context only, no promotional reading, no cover-art use. | Promotional or cover-art use of agency imagery or insignia. |
| 8 | native_audio_rights | Rights covering the ORIGINAL audio track if it is retained. | Native audio is licensed together with the picture, or audio is verified silent/own-recorded. | Retained audio with no separate rights basis, or substituted music/SFX. |
| 9 | attribution_string | Complete credit line required by the licence (title, author, source URL, licence, any change note). | Full credit string written and included on screen and in the description. | Name only, link only, or a generic 'credit to the owner'. |
| 10 | no_endorsement_implied_wording | On-screen and spoken wording must not imply agency/person endorsement. | Explicit 'no endorsement implied' wording present. | Title, caption or VO could be read as an endorsement. |
| 11 | no_insignia_confirmed | Frame-by-frame check for agency insignia, logos, mission patches or branding. | Documented 'no insignia in the selected frames'. | Insignia visible, or check not performed. |
| 12 | sha256_after_download | Hash of the exact file that will enter the edit. | SHA-256 recorded after download and matching the final media file. | No hash, or hash of a different/transcoded file. |
| 13 | duration_seconds | Exact selected in-point / out-point and duration. | Duration <= 10s on screen and the 8 clips together stay <= 80s / 600s (<=13.3%). | Longer excerpt, or the aggregate source share exceeds 13.3%. |
| 14 | scout_score_out_of_100 | V10-style 10-axis scout score for this specific clip. | Numeric score recorded with its rubric sheet. | No score, or a score copied from another clip. |
| 15 | scout_min_pass_78 | The >=78 minimum pass threshold from the rubric. | True only when scout_score_out_of_100 >= 78. | True with a lower score, or set without a score. |
| 16 | clearance_status | Final status after every other field passes. | 'cleared' ONLY when all fields above are verified AND human_legal_review=true. | 'cleared' with any null/failed field. |
| 17 | human_legal_review | A human reviewer has actually reviewed this clip's rights chain. | true with reviewer name and date in the sign-off block. | true without a named reviewer/date, or set by an agent. |
| 18 | not_a_legal_opinion | This ledger is a checklist, not legal advice. | true, always. | false - would imply a legal opinion. |

## 2. Kill conditions (koi ek bhi mila to slot REJECT)

- Current named crew / employee in promotional framing or an official mission broadcast used as a source clip.
- Agency insignia, mission patch, or logo visible in the selected frames.
- Native audio or music retained without its own documented rights basis.
- Asset obtained from a social repost, mirror, aggregator or embed instead of the rights holder.
- Licence cannot be read for this exact file, or excludes commercial use while monetization is intended.
- The V10/Short NASA water-bubble asset (any hero, callback, montage or whole-video use).
- Any clip that would make the 8-source aggregate exceed 80s / 600s (13.3%).
- Clips strung together with little or no narrative, or a mostly non-verbal reaction.

## 3. Attribution templates

| Lane | Template |
| --- | --- |
| NASA / agency | Source: NASA / [mission or centre], "[asset title]", [asset ID]. NASA is credited; no endorsement implied. Licence: [agency media usage statement + URL, retrieved YYYY-MM-DD]. |
| CC BY | "[title]" by [author], [source URL], licensed CC BY [version]. Changes: cropped to <=10s, slowed to 0.5x/0.25x, no audio substitution. No endorsement implied. |
| Verified public domain / agency original | "[title]", [agency], public domain per [statement URL, retrieved YYYY-MM-DD]. No endorsement implied. |
| Own-shot original | Original footage shot for this episode by [operator], [date]. No third-party material. |
| Licensed with permission | "[title]" used with written permission from [rights holder], dated [date], reference [ID]. Permission alone does not establish reused-content eligibility. |

## 4. 8 dossiers (sab pending)

| Slot | Analytic job | clearance | human_legal_review | NULL fields | Reviewer |
| --- | --- | --- | --- | --- | --- |
| 1 | expectation violation | pending | false | 18 | None |
| 2 | physics / optics surprise | pending | false | 18 | None |
| 3 | timing / slow-motion frame | pending | false | 18 | None |
| 4 | scale / size illusion | pending | false | 18 | None |
| 5 | native sound vs silence | pending | false | 18 | None |
| 6 | human reaction beat | pending | false | 18 | None |
| 7 | near-miss / coincidence | pending | false | 18 | None |
| 8 | prediction test / callback | pending | false | 18 | None |

Har dossier ke **3 real API probe targets** (IDs + watch URLs) JSON me hain. Ye **third-party copyrighted videos** hain — inka istemal likhit ijazat ke bagair nahi, aur ijazat milne par bhi alag se reused-content review hogi [7](https://support.google.com/youtube/answer/1311392?hl=en) [9](https://support.google.com/youtube/answer/6013276?hl=en).

## 5. Policy anchors

| Mauzoo | Source |
| --- | --- |
| reused_content | [7](https://support.google.com/youtube/answer/1311392?hl=en) |
| fair_use_four_factors | [8](https://support.google.com/youtube/answer/9783148?hl=en) |
| credit_insufficient | [10](https://support.google.com/youtube/answer/2797454?hl=en) |
| cc_by_attribution | [11](https://support.google.com/youtube/answer/2797468?hl=en) |
| content_id | [9](https://support.google.com/youtube/answer/6013276?hl=en) |
| ads_rights_confirmation | [17](https://support.google.com/youtube/answer/94522?hl=en) |
| nasa_media | [31](https://www.nasa.gov/nasa-brand-center/images-and-media/) |
| nasa_advertising | [32](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) |
| nasa_partnerships | [33](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) |

> **Ye checklist legal advice nahi.** `not_a_legal_opinion=true` har dossier me. Credit, disclaimer aur "non-profit" apne aap fair use nahi banate; chaar factors aur adoalat ka faisla alag baat hai [8](https://support.google.com/youtube/answer/9783148?hl=en) [10](https://support.google.com/youtube/answer/2797454?hl=en).

---

## 6. Phase B/C ki nayi real API forensics (run `42905149277`)

| Angle query | n | 1M+ | Median views | top3_share | fresh_30d | Verdict | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| why we rewatch moments | 20 | 1 | 20,351 | 0.854 | 1.0 | NO | 39.3 |
| frame by frame breakdown explained | 20 | 5 | 163,086 | 0.595 | 0.0 | NO | 31.6 |
| science commentary long form | 1 | 1 | 4,965,860 | 1.0 | 0.0 | NO | 33.7 |

**Imaandaar padhne ka tarika:**

- `science commentary long form` me **sirf 1 result** aaya — ye query bahut tang thi, "demand nahi hai" ka saboot **nahi**. `winnability=0.0` isi chhote sample ka natija hai.
- `why we rewatch moments` me `fresh_share_30d=1.0` aur Phase A ke `viewCount` reports me `0.0` — **dono order ka artifact** hain, trend ka faisla nahi.
- Lekin is query ka top video ka title hi **"The NO-GOAL Moment You Need to Watch TWICE"** hai (1,243,993 views, PT15S). Yani "watch twice" wala framing real audience tak pahunchta hai — hamare thesis ke liye ek **real** (magar chhota) signal.
- `frame by frame breakdown explained` ka top **jacksfilms** video **1H5M35S** ka hai with 4,355,247 views — lambi frame-by-frame analysis ka bhi real precedent hai.

| Real winner | Channel | Views | Duration | Transcript |
| --- | --- | --- | --- | --- |
| Perseverance Rover’s Descent and Touchdown on Mars (Official NASA Video) | NASA | 17,976,259 | PT3M26S | error |
| NASA or Sarychev Volcano Eruption from the International Space Station | NASA Goddard | 127,067,596 | PT9S | no_captions |
| Visualizing Magnetic Fields with Slow Mo #shorts #slowmoguys | The Slow Mo Guys | 59,568,824 | PT54S | error |
| How a slinky falls in slow motion #shorts | Veritasium | 36,618,923 | PT42S | ok |
| How lighter works close-up in #macro #slowmo | UrDay | 363,151,947 | PT9S | error |
| Cavitation in Bottle at 82,000fps #shorts | The Slow Mo Guys | 38,177,261 | PT38S | error |

**6 teardown me se 5 transcripts nahi mile** (4 par `yt-dlp` bot check, 1 par `no_captions`). **1 mila**: Veritasium *"How a slinky falls in slow motion"* — aur usse hamare script ko seedha fayda mila. Poora hisaab `PHASE_C_SCRIPT_DRAFT_V12.md` me.

> NOTE: in teardowns ke view counts Phase A reports se **kuch sau** differ karte hain (do alag waqt par fetch). Ye point-in-time public counts hain, koi stable analytics nahi.

---

## 7. Jo abhi nahi hua

- `clip_downloaded` = **False**
- `clip_cleared` = **False**
- `legal_opinion` = **False**
- `human_legal_review` = **False**
- `commercial_monetization_clearance` = **False**
- `nasa_endorsement` = **False**
- `astronaut_permission_obtained` = **False**
- `render_done` = **False**
- `upload_done` = **False**
- `publish_done` = **False**
- `monetization_changed` = **False**
- `human_creative_approval` = **False**
- `guaranteed_views` = **False**
- `perfection` = **False**

NO legal clearance, NO guaranteed views, NO human approval, NO render, NO upload, NO publish, NO monetization change, NO NASA endorsement.

---

## 8. Agla qadam

1. **Aap / human reviewer** 8 dossiers ke 18 fields bhartein, `sign_off` me naam + tareekh + decision.
2. `validate_phase_bc_v12.py` ka gate test tabhi `cleared` allow karega jab sab fields verified ho.
3. Uske baad VO recording → edit → QC → metadata. Abhi kuch record/render/upload nahi.
4. Pending safety: uploaded V10 Short ka monetization OFF (aapne ON bataya tha).

