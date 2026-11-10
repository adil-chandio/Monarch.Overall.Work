# REPLAY LAB Ep.1 — Phase A: Source Audit

> **Kaam shuru ho gaya.** Ye file sirf Phase A (source audit) ka natija hai. Koi video nahi bani, koi VO nahi bani, koi upload/publish/monetization nahi hua. Rights gate abhi bhi OPEN hai.

**Edition:** `v11_replay_lab_ep01_phase_a_start_2026-11-05` · **HEAD:** `2e48c3eec2c92ee099d51576d0108987f1cc7f5e` · **Status:** `phase_a_complete_phase_b_draft`

---

## 1. Verified ground truth

| Check | Result | Expected |
| --- | --- | --- |
| NASA ID | art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman | art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman |
| Vertical master bytes | 29314216 | 29314216 |
| Vertical master SHA (first 16) | 11395618c0db7416 | 11395618c0db7416 |
| V10 Short bytes | 34495086 | 34495086 |
| V10 Short SHA (first 16) | 608aa065cd3c5389 | 608aa065cd3c5389 |
| Source duration (s) | 42.709309 | 42.709309 |
| Evidence JSONs parsed | 13/13 | 13/13 |
| V10 VO WAVs present | 8 | 8 (reuse NAHI, sirf reference) |

## 2. Findings

### F1 — ✅ Single locked NASA source re-verified

NASA ID, vertical master SHA/bytes, V10 deliverable SHA/bytes and 13/13 evidence JSONs re-checked against committed ledgers [8](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json) [9](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/qc_summary.json). No second clip introduced, no repost, no compilation. Source duration 42.709309s [8](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json).

### F2 — ✅ NEW first-party physics source found (upgrade over the idea study)

NASA's own image article states: *"Chiao's picture is upside down because light is refracted, or bent, as it passes from one medium to another – in this case, air to water."* [2](https://www.nasa.gov/image-article/bubbly-chiao/) The idea study leaned on third-party reporting for this mechanism; ab isko official NASA wording se anchor kiya gaya hai. Surface tension / curved-liquid optics bhi NASA se [3](https://www.nasa.gov/science-research/astrophysics/what-is-the-fluidic-telescope/).

### F3 — ✅ Replay-first structure is evidence-backed

YouTube Help defines spikes as moments viewers rewatched or shared [6](https://support.google.com/youtube/answer/9314415?hl=en); har chapter ek replay pass hai. Ye koi algorithm trick ka dawa nahi.

### F4 — ⚠️ BLOCKER: 16:9 ke liye source abhi vertical hai

Local master `1080x1920` vertical hai [8](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json), jabke target 16:9 landscape hai [11](workspace://research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md). Original 4K `3840x2160` file (SHA 7fd9cd0cfc22…) workspace me **present nahi** hai — sirf ledger me record hai [8](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json). Isliye Phase D shuru hone se pehle original 4K re-fetch ya human-approved crop/pillarbox plan chahiye. Maine koi upscale/crop invent nahi kiya.

### F5 — ⚠️ BLOCKER: render/QC toolchain is session me maujood nahi

System ffmpeg/ffprobe aur numpy available nahi, bundled `v10_deps` bhi is snapshot me nahi. Isliye **abhi koi render, VO synthesis ya QC nahi chalaya** — ye honest tooling gap hai, koi failure chhupaya nahi gaya.

### F6 — ⚠️ GATE: rights / monetization abhi OPEN

NASA promotional-content gate khula hai [5](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) [4](https://www.nasa.gov/nasa-brand-center/images-and-media/), `human_legal_review=false`, `commercial_monetization_clearance=false` [8](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json), aur user ne Short ka monetization ON bataya hai [13](workspace://research/long_form_viral_idea_v11/MONETIZATION_ON_IMMEDIATE_ACTION_V11.md). Long-form ko **monetized / promotional publish** tab tak nahi jaana chahiye. Script/audit ka kaam is gate ko close nahi karta [12](workspace://research/long_form_viral_idea_v11/UPLOAD_SAFETY_V11.md).

---

## 3. Rights / claim state (unchanged)

| Flag | Value |
| --- | --- |
| human_legal_review | False |
| commercial_monetization_clearance | False |
| publicity_or_privacy_permission_obtained | False |
| not_a_legal_opinion | True |
| human_creative_approval | False |
| technical_pass | True |
| technical_check_count | 33 |
| technical_checks_pass | 33 |
| nine_audio_gates_pass | True |
| technical_pass | True |
| human_creative_approval | False |
| human_native_audio_listening | False |
| human_legal_review | False |

## 4. Source ledger

| Ref | Source | Used for |
| --- | --- | --- |
| [1](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) | NASA image/video detail - Fun with Water Bubbles (Artemis II) | Locked single clip ID, title, date 2026-04-04. |
| [2](https://www.nasa.gov/image-article/bubbly-chiao/) | NASA - Bubbly Chiao (image article, 2008-03-23) | FIRST-PARTY physics confirmation: an image seen through a floating water sphere is upside down because light is refracted (bent) passing from air to water; same effect makes rainbows in raindrops. |
| [3](https://www.nasa.gov/science-research/astrophysics/what-is-the-fluidic-telescope/) | NASA - What is the Fluidic Telescope? (surface tension / liquid lenses) | Surface tension gives droplets their shape; curved liquid surfaces can act as optical elements. |
| [4](https://www.nasa.gov/nasa-brand-center/images-and-media/) | NASA Images and Media Usage Guidelines | Credit NASA, no endorsement implied, no insignia, educational/informational use, commercial and identifiable-person restrictions, SI/AI attribution rules. |
| [5](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) | NASA Strategic Partnerships - Promotional Content | Short-form social generally promotional; imagery with current astronauts may not be used in promotional content; no endorsement/co-branding. |
| [6](https://support.google.com/youtube/answer/9314415?hl=en) | YouTube Help - Audience retention / key moments | Spikes are moments viewers rewatched or shared; replay-first structure rationale. |
| [7](https://support.google.com/youtube/answer/14328491?hl=en) | YouTube Help - Disclosing use of GenAI content | AI use toggle is a human decision; disclosure alone doesn't limit audience or monetization eligibility. |
| [8](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/rights_ledger_v10.json) | V10 rights ledger | Source provenance, SHA, duration, flags (human_legal_review=false, commercial_monetization_clearance=false). |
| [9](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/qc_summary.json) | V10 QC summary | 33/33 objective checks, 9 audio gates, technical_pass=true, human_creative_approval=false. |
| [10](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/edit_ledger_v10.json) | V10 edit ledger / caption timings | 8 beats, 118 words, word captions, REFRACTION 23.42-29.90s, credit 44.24-49.40s, loop-back. |
| [11](workspace://research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md) | V11 forensic idea-selection study | Chosen idea RL-01, 93.3/100, 12 chapters, 6 phases A-F, 12 kill switches, guardrails. |
| [12](workspace://research/long_form_viral_idea_v11/UPLOAD_SAFETY_V11.md) | V11 upload-safety decision card | Rights gate OPEN; monetized/promotional publish not cleared. |
| [13](workspace://research/long_form_viral_idea_v11/MONETIZATION_ON_IMMEDIATE_ACTION_V11.md) | V11 monetization-ON action card | User reported Short monetization ON; recommended OFF; not agent-verified. |
| [14](workspace://config/channels.json) | config/channels.json | Legacy Monarch Lab 8-12 min 'one concept, one demo'; ban stock b-roll as hero / reaction-only / clickbait without payoff. |
| [15](https://factcheck.afp.com/doc.afp.com.A6WV668) | AFP Fact Check - broadcast-glitch clip misused for false 'staged' claims | Guardrail only: do not amplify a broadcast-glitch/staged conspiracy. Directional, unverified as analytics; never used as a view count or reach claim. |

## 5. Non-claims (sab `false`)

`video_rendered`, `voiceover_synthesized`, `captions_burned`, `original_4k_source_reacquired`, `sixteen_by_nine_master_created`, `upload_or_publish_performed`, `monetization_enabled_or_changed_by_agent`, `human_creative_approval`, `human_full_motion_review`, `human_native_audio_listening`, `human_legal_review`, `legal_opinion`, `commercial_monetization_clearance`, `written_astronaut_or_csa_permission`, `nasa_endorsement`, `official_nasa_status`, `guaranteed_virality`, `guaranteed_retention`, `perfection_or_zero_omission`, `rights_gate_closed`, `youtube_data_api_called`

---

## 6. Agla qadam

Script draft `SCRIPT_DRAFT_V11.md` aur chhota plan `WORK_PLAN_V11.md` isi folder me hain. Do blockers (16:9 source + tooling) aur ek open gate (rights/monetization) clear hone se pehle **render shuru nahi hoga**.

