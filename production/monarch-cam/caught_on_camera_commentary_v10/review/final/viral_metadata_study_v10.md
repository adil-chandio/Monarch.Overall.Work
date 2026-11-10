# V10 Forensic Metadata Study — Artemis II Water Bubble Short

> **Roman Urdu note:** Ye pack “viral hone ki guarantee” nahi deta. Ye evidence-based, discovery-oriented metadata + forensic audit hai. Jo verify nahi ho saka (legal clearance, human listening, analytics, perfection) usse explicitly **uncertain / pending** rakha gaya hai.

**Evidence cut-off:** `8965bebca9634139e1f42854fb84380eff189def` — `2026-11-10T01:06:51+00:00` — `fix(v10): clear choked VO with narrow declick and gentle limiter [skip ci]`  
**Deliverable:** `deliverables/MONARCH_CAM_Artemis_II_Upside_Down_Face_V10_Short.mp4`  
**SHA-256:** `efce2ea3391828d4d638d980db179330bd88f21a12f7864e6b0bcac58d50a91f`  
**Size:** 34,500,681 bytes  
**Machine-readable pack:** `production/monarch-cam/caught_on_camera_commentary_v10/review/final/viral_metadata_v10.json`  
**Sources ledger:** `production/monarch-cam/caught_on_camera_commentary_v10/review/final/viral_metadata_sources_v10.json`

> **Updated recommendation:** category aur pinned comment ka final, evidence-linked pack `production/monarch-cam/caught_on_camera_commentary_v10/review/final/category_and_pinned_comment_v10.md` me hai. Neeche wali category/pinned values usi se sync ki gayi hain.

> **Post-cut-off audio revision (VO glitch fix).** Is study ke baad user ne report kiya ke voice over me *“buffering glitches jesa sound”* tha. Isliye audio chain badla gaya: 7-sample narrow declick aur uski linear ramps hata kar ek continuous soft-knee slope conditioner lagaya gaya; kisi sample ko interpolation se replace nahi kiya gaya, aur VO ka 200–1000 Hz fundamental lagbhag untouched rakha gaya. Neeche diye gaye audio-forensics numbers (SHA-256 `efce2ea…`, 34,500,681 bytes, −14.66 LUFS, air −0.28 dB, narrow-repair events) **evidence cut-off `8965beb` ka historical snapshot** hain, current deliverable nahi. Current values ke liye `qc_summary.json`, `audio_qc.json` aur `vo_quality_fix_v10.json` dekhen: SHA-256 `608aa065cd3c53894b96df1ebb6fa74dd3ce1e846366e40a940426b4823586a7`, 34,495,086 bytes, chain `dualmono_linear_loudnorm_clear_vo_continuous_slew_no_declick`, −14.60 LUFS, 9/9 audio gates, 33/33 technical checks. Metadata recommendations, title/description/hashtags, policy matrix aur rights/legal caveats **unchanged** hain. Ye ek objective engineering correction hai — human listening sign-off, creative approval, legal clearance, perfection ya guaranteed result ka claim nahi.

---

## 0. Honesty gate — what this study does NOT claim

- No virality, reach, retention, revenue, subscriber, CTR, RPM, view-count or audience-result claim.
- No perfection, zero-flaw, zero-omission or “nothing was missed” claim — the user's requested absolute is explicitly declined as unverifiable.
- No human creative approval, human full-motion review, or human native-audio listening sign-off.
- No legal opinion, human legal review, written astronaut/CSA permission, or commercial/monetization clearance.
- No NASA endorsement, NASA approval, “official NASA” wording, insignia, or co-branding.
- `technical_pass=true` remains separate from `human_creative_approval=false`.
- No YouTube Data API key, channel analytics, trend database, search-volume data, A/B result or competitor retention graph was available.

## 1. Copy-paste primary metadata (YouTube Shorts)

**Title**

```text
NASA Water Bubble Flips an Astronaut's Face
```

Title chars: **43** (internal target ≤50; YouTube limit 100 [2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop)). Baseline committed title was `NASA Water Bubble Flips an Astronaut's Face` (43 chars). Accurate, succinct, important words first, no ALL CAPS/emoji [9](https://support.google.com/youtube/answer/12340300?hl=en-GB).

**Description**

```text
A floating water bubble aboard Artemis II acts like a liquid lens and flips an astronaut's face upside down. We break down the refraction, keep NASA's native crew audio, and replay the inverted-face detail.

Source: NASA, "Fun with Water Bubbles" (2026-04-04), NASA ID art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman. Official page: https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman

NASA media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ — NASA is acknowledged as the source; no NASA endorsement is implied and no NASA insignia is used. On-screen credit: "Source: NASA / Artemis II".

Original contribution: research, commentary, replay analysis, word-by-word burned captions and a generic synthetic deep-male voiceover. NASA's native crew audio is retained; no music, sound effects, procedural bed or audio substitution was added.

Educational / informational commentary and analysis, not a raw reupload. Identifiable astronauts / possible CSA personnel appear. Commercial, promotional, advertising, packaging or cover-art use may require additional clearance; no written permission, human legal review or legal opinion is claimed.

No invented date, injury, outcome, view count, AI-status claim or audience-result claim. No guaranteed virality or retention.

#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity
```

Description chars: **1388** / 5,000 [3](https://support.google.com/youtube/answer/12948449?hl=en). Unique, first lines carry the payoff, and the 1–2 main words are **water bubble** / **refraction** [3](https://support.google.com/youtube/answer/12948449?hl=en).

**Hashtags**

```text
#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity
```

6 hashtags, no spaces, all directly related. Up to 3 may appear near the title; >60 would be ignored; unrelated/misleading tags and ordinary descriptive tag lists in the description are prohibited [1](https://support.google.com/youtube/answer/6390658?hl=en). Deliberately excluded: `#Viral, #ViralShorts, #Trending, #FYP, #ForYou, #YT Viral, #YouTubeShorts, #Subscribe`.

**Tags — Studio tag field only**

```text
water bubble, NASA, Artemis II, Artemis 2, artemis ii, refraction, microgravity, astronaut, water sphere, liquid lens, space science, upside down face, NASA water bubble, Fun with Water Bubbles
```

Tags mainly correct misspellings and otherwise play a minimal role [2](https://support.google.com/youtube/answer/146402?hl=en); do not paste this list into the description [1](https://support.google.com/youtube/answer/6390658?hl=en).

**Pinned comment**

```text
Which moment made you replay — the face flipping upside down, or the loop back at the end?
Curved water bends light (refraction), so the sphere acts like a tiny liquid lens.
Source: NASA / Artemis II, "Fun with Water Bubbles". NASA is credited; no endorsement implied.
```

A genuine question is allowed; incentives/coercion/fake engagement are not [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365).

---

## 2. Title alternatives (forensic comparison)

| Title | Chars | Type | Rationale |
| --- | --- | --- | --- |
| `NASA Water Bubble Flips an Astronaut's Face` | 43 | searchable + intriguing | Adds NASA for source/search clarity while keeping 'water bubble' and the flip payoff near the front. |
| `NASA Water Bubble Flips an Astronaut's Face` | 43 | searchable | Existing committed baseline; shortest accurate description of the payoff. |
| `Artemis II Water Bubble Flips a Face` | 36 | searchable | Mission keyword first; useful for Artemis II search intent. |
| `Why Is That Astronaut Upside Down?` | 34 | intriguing | Curiosity gap matching hook 1; weaker explicit search terms. |
| `This Water Bubble Acts Like a Lens` | 34 | searchable | Science-forward; leads with the object rather than the face. |
| `Not a Lens: NASA's Floating Water Ball` | 38 | intriguing | Echoes exact first VO line; avoid if it reads as a lens claim. |
| `A Water Bubble Turned Into a Lens in Space` | 42 | searchable | Long-tail optics phrasing; still under 50 chars. |
| `NASA Refraction: The Upside-Down Face` | 37 | searchable | Puts the science term 'refraction' early. |
| `Watch a Water Bubble Flip a Face in Space` | 41 | intriguing | Soft imperative matches the 'watch it again' loop, without clickbait. |
| `Artemis II: Water Sphere Refraction` | 35 | archival/searchable | Most literal; least emotional pull. |

Rejected style lanes: ALL CAPS, emoji stuffing, `viral/trending/guaranteed`, fake counts, “shocking”, “official NASA”, “NASA approved”. Accurate titles and avoiding clickbait/sensational wording are explicit YouTube guidance [9](https://support.google.com/youtube/answer/12340300?hl=en-GB) [2](https://support.google.com/youtube/answer/141805?hl=en) [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365) [4](https://www.nasa.gov/nasa-brand-center/merchandise-approvals/).

## 3. Description alternatives

### 3.1 `short` — 654 chars

```text
A floating water bubble aboard Artemis II acts like a liquid lens and flips an astronaut's face upside down. We break down the refraction, keep NASA's native crew audio, and replay the inverted-face detail.

Source: NASA, "Fun with Water Bubbles" (2026-04-04), NASA ID art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman. Official page: https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman

NASA is acknowledged; no endorsement implied. Generic synthetic voiceover; native NASA audio retained. Identifiable persons appear; commercial/promotional use may require clearance.

#Shorts #NASA #ArtemisII #Science #Refraction
```

### 3.2 `science_forward` — 1004 chars

```text
Refraction through a curved floating water sphere inverts the image of an astronaut behind it. This Short replays the Artemis II 'Fun with Water Bubbles' footage, explains the liquid-lens effect, and keeps NASA's native crew audio.

Source: NASA, "Fun with Water Bubbles" (2026-04-04), NASA ID art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman. Official page: https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman

Science terms: refraction, surface tension, microgravity, liquid lens, image inversion. Original commentary, word-by-word captions and a generic synthetic voiceover; no music or SFX.

Educational / informational commentary and analysis, not a raw reupload. Identifiable astronauts / possible CSA personnel appear. Commercial, promotional, advertising, packaging or cover-art use may require additional clearance; no written permission, human legal review or legal opinion is claimed.

#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity #Physics
```

### 3.3 `rights_first` — 1098 chars

```text
A floating water bubble aboard Artemis II acts like a liquid lens and flips an astronaut's face upside down. We break down the refraction, keep NASA's native crew audio, and replay the inverted-face detail.

Source: NASA, "Fun with Water Bubbles" (2026-04-04), NASA ID art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman. Official page: https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman

NASA media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ — NASA credited; no endorsement, insignia, co-branding or 'official NASA' wording. Identifiable current astronauts / possible CSA personnel appear; short-form social content is generally treated as promotional by NASA, so commercial or promotional use may require written clearance. No legal opinion or written permission is claimed.

Generic synthetic deep-male voiceover disclosed. Native NASA audio retained. No music, SFX, procedural bed, audio substitution, invented date, injury, outcome, view count or audience-result claim.

#Shorts #NASA #ArtemisII #Science #Refraction #Microgravity
```

All stay under 5,000 chars [3](https://support.google.com/youtube/answer/12948449?hl=en); each remains unique rather than a reused default [3](https://support.google.com/youtube/answer/12948449?hl=en).

---

## 4. Asset microscope — exact committed facts

| Field | Value | Source |
| --- | --- | --- |
| Duration | 49.400 s | qc_summary.json |
| Frames / fps | 1482 / 30 | qc_summary.json |
| Resolution | 1080x1920 | qc_summary.json |
| Video / audio | H.264 / AAC 48 kHz stereo | qc_summary.json / technical_qc.json |
| Deliverable SHA-256 | efce2ea3391828d4d638d980db179330bd88f21a12f7864e6b0bcac58d50a91f | qc_summary.json |
| Technical checks | 33/33 | qc_summary.json |
| Audio gates | 9/9 true | audio_qc.json |
| Integrated loudness | -14.66 LUFS | audio_qc.json |
| Sample peak / clipping | -1.88 dBFS / 0 samples | audio_qc.json |
| LRA / movement | 3.48 LU / 20.13 dB | audio_qc.json |
| Harsh / air over high-mid | +0.98 dB / -0.28 dB | audio_qc.json |
| Click runs | 0 | audio_qc.json |
| VO fix air delta | +5.27 dB (-5.55 → -0.28) | vo_quality_fix_v10.json |
| Legacy broad declick damage | 3,888 groups / 100,724 samples / 4.2478% | vo_quality_fix_v10.json |
| Narrow repair | 5,214 + 937 jumps; ~1.32% + ~0.24% samples | vo_quality_fix_v10.json |
| Captions | 118 word-by-word events | caption_timings.json |
| Safe zone | top 250 / bottom 1560 / left 80 / right 1000 | edit_ledger_v10.json |
| On-screen credit | "Source: NASA / Artemis II" @ 44.24–49.40 s | captions_v10.ass |
| On-screen label | REFRACTION @ 23.42–29.90 s | captions_v10.ass |
| Contact sheets | 7 + first3s + last3s | contact_sheets_manifest.json |

## 5. Source provenance

| Field | Value |
| --- | --- |
| NASA ID | art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman |
| Title | Fun with Water Bubbles |
| Date created | 2026-04-04 |
| Source page | https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman |
| Direct 4K asset | https://images-assets.nasa.gov/video/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman~orig.mp4 |
| Original SHA-256 | 7fd9cd0cfc22451910ac8fa8848b5252c51320a82c193e3a98cf7c0aa725c0dc |
| Vertical master SHA-256 | 11395618c0db74164e35de8186b079f974316f13fd5c25efb789574b22d5960c |
| Rubric | 91/100 vs 78 minimum; 0 kill switches |
| Clip lock | N01; bear/NPS, V9 ranking, reposts and compilations superseded |

NASA content is generally not subject to US copyright and may be used for educational/informational purposes, with NASA acknowledged as source [1](https://www.nasa.gov/nasa-brand-center/images-and-media/). NASA identifiers/insignia are protected and endorsement must not be implied [3](https://www.nasa.gov/nasa-brand-center/).

## 6. Edit / retention map

| Time | Event | Evidence |
| --- | --- | --- |
| 0.0–1.5 s | Payoff flash: inverted face + 'THAT IS NOT A LENS...' word captions; mute-readable | edit_ledger_v10.json / captions_v10.ass |
| 0.0–5.074 s | Beat 1 hook | edit_ledger_v10.json |
| 5.174–12.337 s | Context / rewind | edit_ledger_v10.json |
| 13.55–15.95 s | Native reaction window 1 (+8 dB) | native_audio_ledger_v10.json |
| 23.423 s | Rehook: 'the astronaut behind it is upside down' | edit_ledger_v10.json |
| 23.42–29.90 s | REFRACTION label | captions_v10.ass |
| 24.70–26.17 s | Native reaction window 2 (+8 dB) | native_audio_ledger_v10.json |
| 30.303 s | Science explanation: refraction | edit_ledger_v10.json |
| 36.672 s | Authenticity line: no CGI / no staged skit | edit_ledger_v10.json |
| 40.40–43.17 s | Native reaction window 3 (+8 dB) | native_audio_ledger_v10.json |
| 44.2 s | Loop-back to payoff frame | edit_ledger_v10.json |
| 44.24–49.40 s | Source credit on screen | captions_v10.ass |
| 49.392 s | Last narrated word; 49.400 s file end | native_audio_ledger_v10.json / qc_summary.json |

This is transformative commentary/analysis with original VO, captions and replay structure — not a scraped raw reupload [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365) [7](https://support.google.com/youtube/community-guide/271248162/%F0%9F%94%8E-faq-reused-content-youtube%E2%80%99s-partner-program?hl=en). Shorts performance signals include view duration, average % viewed, likes and post-watch surveys [4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts); search also weighs title/description/content match [2](https://support.google.com/youtube/answer/141805?hl=en). No result is claimed.

---

## 7. Rights & publicity — high-severity gate (new finding)

- NASA should be acknowledged; factual educational/informational use without implied endorsement is generally permitted [1](https://www.nasa.gov/nasa-brand-center/images-and-media/).
- If NASA media includes an identifiable person, commercial use may infringe privacy/publicity rights and permission should be obtained [1](https://www.nasa.gov/nasa-brand-center/images-and-media/).
- Current astronauts' names/likenesses/personality traits may not be used on commercial products, advertisements, promotional material or packaging [1](https://www.nasa.gov/nasa-brand-center/images-and-media/).
- **NASA says short-form social media content is generally considered promotional content, and imagery with NASA identifiers, current astronauts or current employees may not be used in promotional content** [8](https://www.nasa.gov/nasa-brand-center/strategic-partnerships/).
- Advertising/marketing must not imply endorsement; no insignia in ads [2](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
- No 'NASA approved', 'official NASA' or co-branding wording [4](https://www.nasa.gov/nasa-brand-center/merchandise-approvals/).

**Consequence for this 49.4 s Short:** it is educational/informational commentary, but it is also a social Short featuring identifiable Artemis II astronauts. Under NASA's own wording it can be treated as promotional. Therefore **commercial/monetized publication, sponsorship, ads, packaging, cover art using astronaut faces, or brand co-posting should not proceed without written clearance and human legal review.** The workspace records `commercial_monetization_clearance=false`, `publicity_or_privacy_permission_obtained=false`, `human_legal_review=false`, and `not_a_legal_opinion=true`. This study does not resolve that gate.

## 8. AI / synthetic disclosure

- Workspace: `generic_synthetic_voiceover=true`, `real_person_voice_clone=false`, `realistic_synthetic_media=false` (`native_audio_ledger_v10.json` / `upload_metadata_v10.json`).
- YouTube requires disclosure for realistic AI-generated/altered content; caption creation, voice/audio repair and cloning one's own voice are listed as minor examples that do not need disclosure [2](https://support.google.com/youtube/answer/14328491?hl=en).
- No real-person voice clone or false authorization/endorsement [8](https://support.google.com/youtube/answer/2801947?sjid=14893021524564886382-NA).
- Decision: keep the textual 'generic synthetic deep-male voiceover' disclosure in the description. Recommend the human publisher confirm the Studio 'AI use' toggle; this is a recommendation, not a compliance determination.
- Disclosure alone does not limit reach or monetization eligibility per YouTube [2](https://support.google.com/youtube/answer/14328491?hl=en).

## 9. Studio settings checklist

| Setting | Suggested value | Human confirm |
| --- | --- | --- |
| Title | NASA Water Bubble Flips an Astronaut's Face | YES |
| Description | primary description above | YES |
| Hashtags | in description, 6 tags | YES |
| Tags | tag field only | YES |
| Category | Science & Technology (primary); Education only if needed | YES |
| Language | English | YES |
| Audience / made for kids | human decision required | YES |
| License | Standard YouTube License suggested; not Creative Commons over NASA footage/persons | YES |
| Shorts remixing | disable unless rights reviewed | YES |
| Altered / synthetic content | human confirm; textual disclosure retained | YES |
| Comments and ratings | enable | YES |
| Visibility | keep draft/unlisted until rights review | YES |
| Branded content / paid promotion | none | YES |
| Recording date | 2026-04-04 from NASA source metadata | YES |
| Recording location | Artemis II mission (NASA footage), not asserted as our filming location | YES |
| Related video | optional; requires advanced feature access | YES |
| End screen | not used for this Short; 49.4 s would qualify only if applicable | YES |

Title/description limits, category/education type, language, captions, license, remixing, audience/COPPA, altered-content setting, related video and recording date/location all come from YouTube's settings documentation [2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop).

## 10. Thumbnail / cover frame

- Visual anchor: 0.0–1.5 s payoff flash — inverted face inside the water sphere, burned word captions already present.
- Optional overlay: `NOT A LENS` or `UPSIDE DOWN?` — accurate to the hook, no sensational wording.
- Custom thumbnails are recommended for videos generally [9](https://support.google.com/youtube/answer/12340300?hl=en-GB), but Shorts cover-frame controls vary; human must confirm in Studio.
- Do not add NASA insignia/logotype/seal, astronaut face as promotional cover art without clearance, 'official NASA' wording, co-branding, or fake counts.

---

## 11. A/B plan — plan only, zero results

| Variable | Variants |
| --- | --- |
| Title | `NASA Water Bubble Flips an Astronaut's Face` / `NASA Water Bubble Flips an Astronaut's Face` / `Why Is That Astronaut Upside Down?` |
| First description line | `payoff-first` / `science-first` / `rights-first` |
| Cover frame | `0.0 s flash` / `23.42 s REFRACTION label frame` |
| Pinned comment | `A — replay question (recommended)` / `D — one-line Shorts` / `No pinned comment` |
| Hashtag order | `#Shorts #NASA #ArtemisII first` / `#NASA #ArtemisII #Shorts first` |

- Observe impressions, viewed-vs-ignored, average view duration, average % viewed, likes, post-watch survey and 'not interested' [4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts) [2](https://support.google.com/youtube/answer/141805?hl=en).
- Change one variable at a time where possible; prefer Studio title/thumbnail edits over duplicate re-uploads.
- Never use misleading titles, fake engagement or detection-evasion edits [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365).
- Publish time is not known to affect long-term performance and no upload cadence is required [2](https://support.google.com/youtube/answer/141805?hl=en) [4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts).
- No A/B result, retention curve or CTR number exists yet.

## 12. Cross-platform adaptations

### Instagram Reels

```text
A floating water bubble aboard Artemis II flips an astronaut's face upside down. Refraction, not a lens. Native NASA audio kept. Source: NASA / Artemis II. Generic synthetic voiceover. #NASA #ArtemisII #Science #Refraction
```

*Verify current in-app caption/hashtag limits before posting; no platform limit asserted here.*

### TikTok

```text
This NASA water bubble acts like a liquid lens — and the face behind it flips. Refraction in microgravity. Source: NASA / Artemis II. Generic synthetic VO. #NASA #ArtemisII #Science
```

*Verify current in-app disclosure tools and limits; no audience-result claim.*

### Facebook Reels

```text
NASA's Artemis II crew played with a sphere of water. Look through it: the astronaut behind it is upside down. Refraction explained, native audio retained. Source: NASA / Artemis II. #NASA #Science
```

*Keep NASA credit and no-endorsement wording intact.*

### X / LinkedIn

```text
Forensic breakdown of one official NASA Artemis II clip: a floating water sphere refracts light like a liquid lens and inverts the face behind it. 49.4s commentary Short with native audio, captions and measured reaction windows. Source: NASA / Artemis II; no endorsement implied.
```

*Long-form post; link to the YouTube Short or raw file, not a re-upload claim.*

## 13. Keywords (research only, not tags)

```text
NASA water bubble, Artemis II water bubble, Fun with Water Bubbles NASA, astronaut upside down water, water sphere refraction, liquid lens in space, microgravity water sphere, surface tension water ball, NASA Artemis II refraction, water bubble flips face, inverted face water bubble, NASA crew laughs water bubble, straw water sphere astronaut, water orb crystal ball space, refraction explained, curved water lens, image inversion water, Artemis II science moment, NASA 4K water bubble, zero gravity water ball, space bubble optics, NASA native crew audio, not CGI water bubble, shorts science explanation, NASA credited commentary, generic synthetic voiceover, word by word captions
```

No search-volume, difficulty or ranking claim is made. Tags are minimal aids [2](https://support.google.com/youtube/answer/146402?hl=en) [2](https://support.google.com/youtube/answer/141805?hl=en).

---

## 14. Pre-publish checklist

| # | Check | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Deliverable SHA-256 matches committed evidence | verified | qc_summary.json |
| 2 | Source NASA ID / page / SHA recorded | verified | candidate_scout_v10.json / rights_ledger_v10.json |
| 3 | 49.4 s / 1482 frames / 1080x1920 / 30 fps / H.264+AAC | verified | qc_summary.json |
| 4 | Nine audio gates true | verified | audio_qc.json |
| 5 | 33/33 technical checks true | verified | qc_summary.json |
| 6 | VO clarity correction applied and measured | verified | vo_quality_fix_v10.json |
| 7 | 118 word-by-word caption events | verified | caption_timings.json |
| 8 | Safe zones / no black bars / no fade-in / no title card | verified | technical_qc.json |
| 9 | NASA on-screen credit exact: 'Source: NASA / Artemis II' | verified | captions_v10.ass |
| 10 | NASA credited in description | verified | this pack |
| 11 | NASA guidelines URL included in description | verified | this pack |
| 12 | No NASA insignia / logotype / seal | verified | rights_ledger_v10.json |
| 13 | No 'official NASA' / 'NASA approved' / co-branding wording | verified | this pack |
| 14 | No endorsement implied | verified | rights_ledger_v10.json + this pack |
| 15 | Identifiable astronauts / possible CSA personnel disclosed | verified | rights_ledger_v10.json + this pack |
| 16 | Commercial/promotional clearance obtained | pending_human | rights_ledger_v10.json |
| 17 | Written astronaut/CSA permission in workspace | not_claimed | rights_ledger_v10.json |
| 18 | Human legal review completed | pending_human | rights_ledger_v10.json |
| 19 | Human full-motion review completed | pending_human | qc_summary.json |
| 20 | Human native-audio listening completed | pending_human | qc_summary.json |
| 21 | Human creative approval | pending_human | qc_summary.json |
| 22 | Monetization / ads / sponsorship decision | pending_human | this pack |
| 23 | No music / SFX / procedural bed / audio substitution | verified | native_audio_ledger_v10.json |
| 24 | No 1.08x time-stretch | verified | script_variants_v10.md / native_audio_ledger_v10.json |
| 25 | No real-person voice clone | verified | native_audio_ledger_v10.json |
| 26 | Generic synthetic voiceover disclosed in description | verified | this pack |
| 27 | Studio AI-use toggle confirmed by human | pending_human | this pack |
| 28 | Title <=100 platform chars and <=50 internal chars | verified | this pack |
| 29 | Title accurate, no ALL CAPS / emoji / clickbait | verified | this pack |
| 30 | Description <5000 chars and unique | verified | this pack |
| 31 | First two lines carry payoff + 1-2 main words | verified | this pack |
| 32 | Hashtags <=60, relevant, no spaces | verified | this pack |
| 33 | No #Viral / #Trending / #FYP stuffing | verified | this pack |
| 34 | Tags only in tag field; no descriptive tag list in description | verified | this pack |
| 35 | Category / language / caption certification set by human | pending_human | this pack |
| 36 | Audience / made-for-kids decision by human | pending_human | this pack |
| 37 | License set to Standard (not CC) by human | pending_human | this pack |
| 38 | Shorts remixing decision by human | pending_human | this pack |
| 39 | Visibility kept draft/unlisted until rights review | pending_human | this pack |
| 40 | Cross-platform limits verified in-app | pending_human | this pack |
| 41 | No invented date / injury / outcome / view count | verified | this pack |
| 42 | No guaranteed virality / retention / revenue claim | verified | this pack |
| 43 | No perfection / zero-flaw / zero-omission claim | verified | this pack |
| 44 | A/B plan documented but no results claimed | verified | this pack |
| 45 | Publish time not claimed to affect long-term performance | verified | [2](https://support.google.com/youtube/answer/141805?hl=en) |

## 15. Inconsistencies / stale flags found under the microscope

| Item | Resolution | Status |
| --- | --- | --- |
| candidate_scout_v10.json review_flags.technical_qc_pass=false | Stale pre-render research flag. Current qc_summary.json / technical_qc.json technical_pass=true at commit 8965beb. | explained |
| upload_metadata_v10.json target_title_chars_max=50 vs YouTube 100-char limit | 50 is an internal mobile-readability target, not the platform maximum. [2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop) | explained |
| native_audio_ledger source_audio_duration_s=42.688 vs rights_ledger source_duration_seconds=42.709309 | Decoded audio stream duration vs official 4K video metadata duration; not a contradiction. | explained |
| edit_ledger beat 1 source_in=6.0 but source_out=3.574 | Beat 1 crosses the 1.5 s flash into the main source; source_for_time mapping wraps from 6.0 back to 0.0-based main. Not an error. | explained |
| candidate_scout clip_lock.locked_at_utc=2026-11-09 vs commit time 2026-11-10 | Research lock predates the render/push commit; chronology only. | explained |
| technical_pass=true vs human_creative_approval=false | Deliberately separate; objective QC is not creative sign-off. | explained |
| vo_quality_fix before SHA 1cfd... vs after SHA efce... | Two distinct committed MP4s; the de03272 audio was replaced by the corrected 8965beb audio. | explained |
| upload_metadata status=draft_not_published | Still true; no upload, analytics, or audience result exists. | verified |

## 16. Forensic claim audit

| Claim | Evidence | Status |
| --- | --- | --- |
| The deliverable is the corrected 8965beb MP4, not de03272. | qc_summary.json sha256=efce2ea... | verified_workspace |
| Duration is 49.4 s / 1482 frames. | qc_summary.json | verified_workspace |
| Resolution is 1080x1920 at 30 fps. | qc_summary.json | verified_workspace |
| Video is H.264, audio is AAC 48 kHz stereo. | qc_summary.json / technical_qc.json | verified_workspace |
| All nine web audio gates pass. | audio_qc.json checks | verified_workspace |
| Integrated loudness is -14.66 LUFS. | audio_qc.json | verified_workspace |
| True peak is -1.88 dBFS with 0 clipped samples. | audio_qc.json | verified_workspace |
| 0 click runs remain after the narrow declick fix. | audio_qc.json | verified_workspace |
| Air/high-mid improved from -5.55 dB to -0.28 dB. | vo_quality_fix_v10.json | verified_workspace |
| Legacy broad declick changed 4.2478% of samples. | vo_quality_fix_v10.json | verified_workspace |
| Narrow repair changed ~1.32% then ~0.24% of samples. | vo_quality_fix_v10.json | verified_workspace |
| 33/33 technical checks pass. | qc_summary.json | verified_workspace |
| technical_pass is separate from human_creative_approval=false. | qc_summary.json | verified_workspace |
| One official NASA clip only. | edit_ledger_v10.json / candidate_scout_v10.json | verified_workspace |
| NASA ID is art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman. | candidate_scout_v10.json | verified_workspace |
| Source title is 'Fun with Water Bubbles', dated 2026-04-04. | candidate_scout_v10.json | verified_workspace |
| Original 4K SHA is 7fd9cd0c...c0dc. | candidate_scout_v10.json | verified_workspace |
| Vertical master SHA is 11395618...5960c. | candidate_scout_v10.json | verified_workspace |
| Clip rubric is 91/100 vs 78 minimum, no kill switches. | candidate_scout_v10.json | verified_workspace |
| Variant A / hook 1 is selected. | script_variants_v10.md / edit_ledger_v10.json | verified_workspace |
| Script has 118 words across 8 beats. | edit_ledger_v10.json / caption_timings.json | verified_workspace |
| Eight voice-01 VO WAVs are sequential with 0.1 s gaps. | native_audio_ledger_v10.json | verified_workspace |
| Native NASA audio bed is retained. | native_audio_ledger_v10.json | verified_workspace |
| Three reaction windows are boosted +8 dB with measured envelope. | native_audio_ledger_v10.json | verified_workspace |
| No music, SFX, procedural bed or audio substitution. | native_audio_ledger_v10.json | verified_workspace |
| No 1.08x time-stretch. | script_variants_v10.md | verified_workspace |
| Word-by-word burned captions use 118 events. | caption_timings.json / captions_v10.ass | verified_workspace |
| On-screen label is REFRACTION at 23.42-29.90 s. | captions_v10.ass | verified_workspace |
| On-screen credit is 'Source: NASA / Artemis II' at 44.24-49.40 s. | captions_v10.ass | verified_workspace |
| Safe zone is top 250 / bottom 1560 / left 80 / right 1000. | edit_ledger_v10.json | verified_workspace |
| 7 contact sheets + first3s/last3s review images exist. | contact_sheets_manifest.json | verified_workspace |
| Human full-motion review is false. | contact_sheets_manifest.json / qc_summary.json | verified_workspace |
| NASA is credited on-screen and in metadata. | captions_v10.ass / upload_metadata_v10.json | verified_workspace |
| No NASA insignia used. | rights_ledger_v10.json | verified_workspace |
| No NASA endorsement implied. | rights_ledger_v10.json | verified_workspace |
| Identifiable astronauts / possible CSA personnel appear. | rights_ledger_v10.json | verified_workspace |
| No written astronaut/CSA permission in workspace. | rights_ledger_v10.json | verified_workspace |
| Commercial monetization clearance is false. | rights_ledger_v10.json | verified_workspace |
| Human legal review is false; not a legal opinion. | rights_ledger_v10.json | verified_workspace |
| Generic synthetic voiceover is disclosed; no real-person clone. | native_audio_ledger_v10.json / upload_metadata_v10.json | verified_workspace |
| No audience-result or virality guarantee claim. | qc_summary.json / upload_metadata_v10.json | verified_workspace |
| YouTube title limit is 100 characters. | [2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop) | verified_external_guidance |
| YouTube description limit is 5,000 characters. | [2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop) | verified_external_guidance |
| Titles should be accurate/succinct with important words first. | [9](https://support.google.com/youtube/answer/12340300?hl=en-GB) | verified_external_guidance |
| First description lines appear before 'Show more'. | [3](https://support.google.com/youtube/answer/12948449?hl=en) | verified_external_guidance |
| Descriptions should be unique with 1-2 main words. | [3](https://support.google.com/youtube/answer/12948449?hl=en) | verified_external_guidance |
| Up to 3 hashtags may appear near the title. | [1](https://support.google.com/youtube/answer/6390658?hl=en) | verified_external_guidance |
| More than 60 hashtags are ignored. | [1](https://support.google.com/youtube/answer/6390658?hl=en) | verified_external_guidance |
| Misleading/unrelated hashtags are prohibited. | [1](https://support.google.com/youtube/answer/6390658?hl=en) | verified_external_guidance |
| Tags play a minimal discovery role. | [2](https://support.google.com/youtube/answer/146402?hl=en) | verified_external_guidance |
| Search uses title/description/content match and engagement. | [2](https://support.google.com/youtube/answer/141805?hl=en) | verified_external_guidance |
| Shorts use view duration, % viewed, likes and surveys. | [4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts) | verified_external_guidance |
| No minimum posting cadence is required. | [4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts) | verified_external_guidance |
| Publish time is not known to affect long-term performance. | [2](https://support.google.com/youtube/answer/141805?hl=en) | verified_external_guidance |
| Scraped content needs transformative editing/commentary/educational value. | [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365) | verified_external_guidance |
| Malicious clickbait and detection evasion are prohibited. | [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365) | verified_external_guidance |
| Asking for likes/comments is allowed without incentives. | [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365) | verified_external_guidance |
| Realistic AI-altered content needs disclosure; minor edits listed as not required. | [2](https://support.google.com/youtube/answer/14328491?hl=en) | verified_external_guidance |
| No AI voice clone of a real person / false endorsement. | [8](https://support.google.com/youtube/answer/2801947?sjid=14893021524564886382-NA) | verified_external_guidance |
| NASA content generally not US-copyrighted; educational/informational use allowed. | [1](https://www.nasa.gov/nasa-brand-center/images-and-media/) | verified_external_guidance |
| NASA should be acknowledged as source. | [1](https://www.nasa.gov/nasa-brand-center/images-and-media/) | verified_external_guidance |
| Identifiable persons in NASA media may need permission for commercial use. | [1](https://www.nasa.gov/nasa-brand-center/images-and-media/) | verified_external_guidance |
| Current astronauts' likenesses restricted in promotional material. | [1](https://www.nasa.gov/nasa-brand-center/images-and-media/) | verified_external_guidance |
| Short-form social media is generally promotional content. | [8](https://www.nasa.gov/nasa-brand-center/strategic-partnerships/) | verified_external_guidance |
| NASA identifiers/current astronauts may not be used in promotional content. | [8](https://www.nasa.gov/nasa-brand-center/strategic-partnerships/) | verified_external_guidance |
| No 'NASA approved' / 'official NASA' / co-branding wording. | [4](https://www.nasa.gov/nasa-brand-center/merchandise-approvals/) | verified_external_guidance |
| NASA endorsement must not be implied in advertising. | [2](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) | verified_external_guidance |
| The proposed title will rank or go viral. | no evidence | prohibited_claim |
| The video is legally cleared for commercial monetization. | no evidence | prohibited_claim |
| NASA approved or endorsed this edit. | no evidence | prohibited_claim |
| A human listened to the final mix and approved it. | no evidence | prohibited_claim |
| The metadata pack is perfect / has zero flaws / missed nothing. | no evidence | prohibited_claim |
| Audience results, retention, CTR, RPM or view counts are known. | no evidence | prohibited_claim |
| The AI-use toggle is definitively not required. | cited examples only | inferred_human_confirm_required |
| Custom thumbnail editing is available for this Short. | Studio UI varies | inferred_human_confirm_required |
| Cross-platform character/hashtag limits are current. | not asserted | unverified |
| Best publish time or posting cadence can be predicted. | official help says no long-term effect / no cadence | unverified |
| Competitor/trend/search-volume data was used. | no API/analytics available | unverified |

Statuses: `verified_workspace` = committed evidence; `verified_external_guidance` = cited official page; `inferred_human_confirm_required` = reasoned but needs human check; `unverified` = not available; `prohibited_claim` = explicitly not made.

## 17. Uncertainty ledger

- No human listening, full-motion review, or creative approval is documented.
- No legal opinion, human legal review, or written astronaut/CSA permission is documented.
- No commercial monetization, advertising, sponsorship, packaging or cover-art clearance is documented.
- No YouTube Data API key, channel analytics, trend/competitor database, search-volume data, retention graph, CTR, RPM, view count or A/B result was available.
- No virality, reach, retention, revenue, subscriber or audience-result claim is made.
- Platform policies and Studio UI can change; the human publisher must re-check current settings before publishing.
- The AI-use toggle decision is a recommendation based on cited examples, not a compliance determination.
- Cross-platform character/hashtag limits are not asserted; verify in each app.
- NASA's 'short-form social media is generally promotional' guidance creates a high-severity rights gate for commercial use; this study does not resolve it.
- Perfection, zero flaws, zero omissions and 'nothing missed' are explicitly not claimed; unverifiable items are listed here instead.

## 18. Sources

| Ref | Citation | Authority | Used for |
| --- | --- | --- | --- |
| YT_TITLE_TIPS | [9](https://support.google.com/youtube/answer/12340300?hl=en-GB) | official_help | accurate succinct titles; important words first; limit ALL CAPS/emoji; custom thumbnail guidance; searchable vs intriguing titles |
| YT_DESCRIPTIONS | [3](https://support.google.com/youtube/answer/12948449?hl=en) | official_help | first lines visible before Show more; unique description; 1-2 main words; 5000-char limit; chapters for longer videos |
| YT_EDIT_SETTINGS | [2](https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop) | official_help | 100-char title limit; 5000-char description limit; tags field; category/education type; language and captions; license; Shorts remixing; audience/COPPA; altered content setting; related video; recording date/location |
| YT_HASHTAGS | [1](https://support.google.com/youtube/answer/6390658?hl=en) | official_help | up to 3 hashtags shown near title; >60 hashtags ignored; no misleading/unrelated hashtags; no ordinary descriptive tags in description; no spaces in hashtags |
| YT_TAGS | [2](https://support.google.com/youtube/answer/146402?hl=en) | official_help | tags play a minimal role; title/thumbnail/description matter more; excessive tags in description prohibited |
| YT_SHORTS_DISCOVERY | [4](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts) | official_help | Shorts ranked by performance and personalization; avg view duration / avg % viewed / likes / post-watch surveys; metadata matches viewer search; no minimum posting cadence |
| YT_PERF_FAQ | [2](https://support.google.com/youtube/answer/141805?hl=en) | official_help | search ranks by title/description/content match and engagement; tags not important; avoid clickbait/ALL CAPS/!!!!!; publish time not known to impact long-term performance; no required upload cadence; monetization status not a discovery signal |
| YT_SPAM | [1](https://support.google.com/youtube/answer/2801973?hl=en-GB&amp=&ref_topic=9282365) | official_help | scraped content needs transformative editing/commentary/educational value; malicious clickbait prohibited; detection evasion prohibited; asking for likes/comments is allowed; no incentives/coercion |
| YT_GENAI | [2](https://support.google.com/youtube/answer/14328491?hl=en) | official_help | disclose realistic AI-altered content; caption creation / voice or audio repair / cloning own voice are minor examples; AI use toggle in Studio; disclosure alone does not limit reach or monetization |
| YT_REUSED_FAQ | [7](https://support.google.com/youtube/community-guide/271248162/%F0%9F%94%8E-faq-reused-content-youtube%E2%80%99s-partner-program?hl=en) | official_community_faq | transformative commentary/educational value; AI channels can be eligible if original |
| YT_IMPERSONATION | [8](https://support.google.com/youtube/answer/2801947?sjid=14893021524564886382-NA) | official_help | no AI voice clone of a real person; no false authorization/endorsement |
| YT_ADS | [6](https://support.google.com/youtube/answer/6162278?hl=en) | official_help | no profanity/stronger language in title/thumbnail; science content is generally suitable |
| NASA_IMAGES | [1](https://www.nasa.gov/nasa-brand-center/images-and-media/) | official_nasa | NASA content generally not US-copyrighted; educational/informational use; NASA should be acknowledged; no implied endorsement; identifiable persons / commercial use may need permission; current astronauts' names/likenesses restricted in promotional material; clearances may be needed for cover art / promotional content |
| NASA_ADVERTISING | [2](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) | official_nasa | no NASA endorsement; no insignia in ads; current astronauts/employees not in ads or marketing |
| NASA_STRATEGIC | [8](https://www.nasa.gov/nasa-brand-center/strategic-partnerships/) | official_nasa | publicly available content usable if guidelines followed; short-form social media generally considered promotional content; imagery with NASA identifiers/current astronauts/current employees may not be used in promotional content; no co-branding / sponsorship / endorsement |
| NASA_BRAND | [3](https://www.nasa.gov/nasa-brand-center/) | official_nasa | no endorsement or misleading use; NASA identifiers protected; third-party copyrighted material needs its own permission |
| NASA_MERCH | [4](https://www.nasa.gov/nasa-brand-center/merchandise-approvals/) | official_nasa | no 'NASA approved' / 'official NASA' / co-branding wording; insignia/logotype/seal not public domain |

*Official YouTube Help and NASA pages are used for policy claims. Community posts surfaced in search (e.g. a 60-second Shorts definition or tag-stuffing anecdotes) are not used as authoritative policy here.* External claims use Arena web_search result IDs/URLs in [id](url) form. Workspace claims cite committed file paths.

---

## 19. Final position

This is an exhaustive evidence-linked metadata pass from the committed workspace plus official platform/rights documentation. It supplies copy-paste titles, descriptions, hashtags, tags, keywords, settings, cover guidance, pinned comment, cross-platform captions, an A/B plan, a 45-item pre-publish checklist, a 78-row claim audit and an explicit uncertainty ledger. It does **not** supply a guaranteed viral outcome, a legal clearance, a human listening sign-off, or a claim of perfection — those remain human/rights gates, not metadata problems.

