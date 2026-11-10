# REPLAY LAB Ep.1 — Phase C: Voice Preview

> **Aage badh gaye ✅** — aapne audition me **`voice-02`** chuni. Usi voice se 4 preview clips bane hain: 3 hooks + Chapter 5 (liquid lens). Ye **preview** hain, final voiceover ya mix nahi. Koi video render, caption, upload ya publish nahi hua.

**Edition:** `v11_replay_lab_ep01_phase_c_preview_2026-11-05` · **HEAD:** `5f8fcdaf5c4220f472eddbb01137b2478988af58` · **Voice:** `voice-02` · **Language:** `en`

---

## 1. Sunne ke liye 4 files

| Clip | File | Words | Bytes | Kyun |
| --- | --- | --- | --- | --- |
| H1 | `audio/vo_preview_h1_v11.mp3` | 26 | 99492 | Default / selected in the idea study. Pattern interrupt; 'not a lens' resolves honestly in Chapter 4. |
| H2 | `audio/vo_preview_h2_v11.mp3` | 32 | 100746 | Replay promise up front. No reach or shock claim. |
| H3 | `audio/vo_preview_h3_v11.mp3` | 28 | 76295 | Question-first; native audio mentioned in the hook itself. |
| CH05 | `audio/vo_preview_ch05_liquid_lens_v11.mp3` | 92 | 266049 | Longest excerpt - pacing / pronunciation check for the core physics chapter (3:30-5:00). |

Sab 4 MP3 valid `ID3` header ke saath hain; SHA256 niche JSON me. File size se zyada koi audio QC claim nahi — is snapshot me ffprobe/numpy maujood nahi [2](workspace://production/monarch-cam/replay_lab_ep01_v11/PHASE_A_SOURCE_AUDIT_V11.md).

---

## 2. Script se exact text

**H1:** That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, because every replay hides a different layer.

**H2:** A sphere of water, a face, and one impossible-looking flip. In the next ten minutes we will watch the same 42 seconds eight times, and each time something new will make sense.

**H3:** Why is that face upside down? The answer is inside the water - not the camera. Let's replay it slowly, then slower, then with the sound still on.

**CH05:** Now the flip. A curved boundary between air and water bends light. Light crossing that boundary is refracted, and the curved surface sends the rays into a reversed arrangement, so the picture arrives upside down. The same bending makes rainbows in raindrops. So the sphere is behaving like a small optical element - a liquid lens. That is why the opening line said it is not a lens: there is no glass, no manufactured optic. The water is doing the job. Freeze here, at twenty-three seconds, and watch it at half speed.

---

## 3. Voice rules (V10 se aage)

- Generic synthetic narration only. No real-person voice clone, no astronaut voice imitation.
- No time-stretch / speed change of the generated speech.
- NASA native crew audio stays in the master; these previews are isolated narration files, NOT a replacement or a final mix [2](workspace://production/monarch-cam/replay_lab_ep01_v11/PHASE_A_SOURCE_AUDIT_V11.md) [5](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/qc_summary.json).
- No music, SFX, procedural bed or audio substitution.
- VO text never says 'according to NASA' and never implies NASA reviewed or approved the analysis [3](https://www.nasa.gov/nasa-brand-center/images-and-media/).
- No 'official NASA', no insignia, no endorsement, no invented date/outcome/view claim.
- AI-use toggle remains a human decision at upload time [4](https://support.google.com/youtube/answer/14328491?hl=en).
- Human listening, full-motion review, creative approval and legal review are all still pending [5](workspace://production/monarch-cam/caught_on_camera_commentary_v10/review/final/qc_summary.json).

---

## 4. Abhi bhi 3 rukavatein

- 16:9 source: local master is 1080x1920 vertical; original 4K not present locally.
- Render/QC toolchain (ffmpeg, ffprobe, numpy, bundled v10_deps) absent in this snapshot.
- NASA promotional / identifiable current-astronaut rights gate OPEN; user-reported Short monetization ON; human_legal_review=false; commercial_monetization_clearance=false [6](workspace://research/long_form_viral_idea_v11/MONETIZATION_ON_IMMEDIATE_ACTION_V11.md).

---

## 5. Non-claims (sab `false`)

`final_voiceover_complete`, `voiceover_mixed_with_nasa_native_audio`, `captions_burned`, `video_rendered`, `sixteen_by_nine_master_created`, `technical_qc_run_on_previews`, `human_creative_approval`, `human_native_audio_listening`, `human_full_motion_review`, `human_legal_review`, `legal_opinion`, `commercial_monetization_clearance`, `written_astronaut_or_csa_permission`, `nasa_endorsement`, `official_nasa_status`, `guaranteed_virality`, `guaranteed_retention`, `perfection_or_zero_omission`, `rights_gate_closed`, `upload_or_publish_performed`, `monetization_changed_by_agent`, `youtube_data_api_called`

---

## 6. Status table

| Phase | Status |
| --- | --- |
| A - Source audit | DONE |
| B - Script draft | DONE |
| C - Voice preview | DONE (4 clips, voice-02) — final VO baaki |
| D - Edit 16:9 | BLOCKED (source + tooling) |
| E - QC | BLOCKED (tooling) |
| F - Metadata | PENDING |

---

## 7. Aapka agla faisla

1. **Hook** final karein: `H1` (default) / `H2` / `H3` — 3 clip sun kar.
2. **Voice** `voice-02` theek hai? Nahi to dobara audition kar sakte hain.
3. **16:9 source** ka tarika: original 4K re-fetch, ya human-approved crop/pillarbox plan.

Uske baad main 12 chapters ka poori VO + caption timings taiyar karunga; render tabhi jab blockers clear hon. Ye legal opinion, clearance, human approval ya guaranteed result ka dawa nahi hai.

