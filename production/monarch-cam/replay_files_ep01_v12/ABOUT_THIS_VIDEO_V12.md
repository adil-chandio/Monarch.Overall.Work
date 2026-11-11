# REPLAY FILES Ep.1 — ACTUAL RENDERED VIDEO (V12)

**Deliverable:** `REPLAY_FILES_Ep01_V12_10min_1080p30.mp4` — a real, playable, edited
10-minute long-form commentary video. This is **not** a plan, a gate, a storyboard or a
render planner. It was rendered locally and verified frame-by-frame.

> Roman Urdu me: **Video ban gaya hai.** 10 minute ka asli MP4, 8 alag clip moments,
> upar original commentary, 10 original diagrams, captions, aur QC. Neeche sab kuch
> sach-sach likha hai — kya bana, kis cheez se bana, aur kya abhi nahi kiya gaya.

---

## 1. What exists (verified, not claimed)

| Item | Measured value |
|---|---|
| File | `REPLAY_FILES_Ep01_V12_10min_1080p30.mp4` |
| Bytes | 69,402,336 |
| SHA-256 | `7920dc6868e2271c9ad0c0ed2f2d99200979358e9ba8e0cd3f875d6e7542b355` |
| Duration | **600.00 s (10:00.00)** |
| Frames | **18,000** (exact, counted by decoding the whole file) |
| Canvas | 1920×1080 landscape, 30 fps, yuv420p |
| Video | H.264 High, ~724 kb/s |
| Audio | AAC-LC 48 kHz stereo, ~191 kb/s |
| Integrated loudness | **−14.02 LUFS** (two-pass EBU R128 linear normalisation) |
| Technical QC | **8 / 8 checks PASS** (`QC_REPORT_V12.json`) |

## 2. What is actually in the edit

- **8 DIFFERENT clip windows / moments.** Eight different Monarch Cam archived finals
  (`deliverables/*.mp4`), each a distinct file, each with its own in-point, ≤10 s excerpt and
  its own playback speed (1.00×, 0.77×, 0.46×, 1.00×, 1.00×, 0.83×, 1.00×, 0.71×). See
  `CONTACT_SHEET_V12.png` for visual proof they are different moments, and
  `EDL_V12_ACTUAL.json` for exact in/out/speed. **The excluded NASA Artemis II / water-bubble
  V10 Short is NOT used anywhere in this video.** The exact trimmed/speed-ramped excerpt of
  each window is **vendored in `clips/clip_window_01..08.mp4`** and pinned by SHA-256 in the
  EDL, so the render stays reproducible even when a `deliverables` final is rebuilt by CI.
- **10 original diagrams** from Phase D (`research/multi_clip_long_form_v12/assets_v12/`),
  used as full-frame analytical holds and as thumbnails inside the clip-window sidebars.
- **Original commentary VO**: 10 TTS chunks (`vo/vo_A.mp3` … `vo/vo_J.mp3`), one consistent
  voice (`voice-02`), 1,045 spoken words across 13 chapters, cut from the Phase C script with
  stage directions removed. **Sentence-level captions** in `captions_v12.srt` (word-count-
  proportional cue timing; approximate, not forced alignment).
- **Original editing**: hook/title card, method card, public-evidence card, 8 labelled clip
  windows with the six-step rule and real public-viewCount data in the sidebars, replay-beat
  annotation strips on every diagram hold, a slow 5% push-in on every static card, and a
  closing card with the honest limits. 22 visual blocks concatenated into one continuous
  18,000-frame master.
- **Original audio bed**: a self-generated, low-level procedural chord ambience (~−30 dB),
  mixed under the VO. No third-party music, no stock SFX.
- **Original thumbnail** `thumbnail_v12.png` (1280×720) and **contact sheet**
  `CONTACT_SHEET_V12.png`.

## 3. Provenance — read this carefully

Aap ne "doosri bohat saari best clips / millions-view wali videos" mangi thin. Is sandbox me
**koi nayi third-party clip download, acquire ya legally clear nahi ki gayi** (na network se,
na raw source files se — repo me woh maujood hi nahi hain). Is liye 8 alag moments **Monarch
Cam ke apne hi pehle se render kiye gaye finals** se liye gaye hain, taake multi-clip
commentary + editing ka asli 10-minute video ban kar haath me mil jaye. Ye 8 alag files hain,
alag in/out aur alag speed ke saath — lekin ye **competitor clips ka substitute claim nahi
hai**. Unhe human rights review ke baad `EDL_V12_ACTUAL.json` ke 8 slots me replace kiya ja
sakta hai; builder ka structure waise hi kaam karega.

Underlying source credits of those earlier finals live in the V4–V9 `CREDITS.md` /
`review/*ledger*.json` files. This episode adds original commentary, original diagrams and
original editing on top.

**Reproducibility note.** The Clean V8 workflow regenerates
`deliverables/..._CLEAN_V8.mp4` on pushes (its bytes changed once right after this render,
in commit `c4938b3`). That does not change this MP4: slot 2's exact excerpt is vendored in
`clips/clip_window_02.mp4` and pinned by SHA-256. Re-running `--all` after CI rebuilt V8 was
verified to produce the **identical** 69,402,336-byte file with the identical SHA-256.

## 4. What is NOT done (honest, still open)

`EDL_V12_ACTUAL.json → honest_flags` records all of these as `false`:

- No third-party clip acquired or legally cleared; **per-clip human legal review pending**.
- **No human creative approval**, no full-motion / native-audio human review of the final cut.
- **No upload, no publish, no monetisation change, no YouTube Studio action** of any kind.
- No NASA endorsement / official status; no identifiable-person permission claimed.
- **No guarantee of views, virality, retention, CTR, RPM or "perfection"**. "Best viral
  video" here means the strongest evidence-based local attempt, not a promise.
- No private retention / CTR / RPM data, no invented competitor transcripts, no invented
  "best growing channels" ranking, no invented keyword volumes. The numbers shown on screen
  are public `viewCount` figures from the committed Phase A GitHub Actions API reports,
  explicitly labelled as public viewCount, not retention.
- Clip-native audio is **not** in this mix (the sound A/B is drawn as an original diagram,
  exactly as Phase D specified); a human native-audio A/B review remains an open item.
- Captions are **sentence-level with approximate word-count-proportional timing**, not
  word-level force-aligned.

## 5. Structure (13 chapters → 10 VO segments)

| Seg | VO | Start | Frames | Visual |
|---|---|---|---|---|
| 1 | A | 0:00.00 | 3097 | hook + diagram 01 + method + evidence card |
| 2 | B | 1:43.23 | 1832 | clip window 01 (expectation violation) + diagram 02 hold |
| 3 | C | 2:44.30 | 1826 | clip window 02 (physics gap) + diagram 03 hold |
| 4 | D | 3:45.17 | 1821 | clip window 03 (three speeds, 0.46×) + diagram 04 hold |
| 5 | E | 4:45.87 | 1822 | clip window 04 (scale error) + diagram 05 hold |
| 6 | F | 5:46.60 | 1534 | clip window 05 (sound on/off) + diagram 06 hold |
| 7 | G | 6:37.73 | 1497 | clip window 06 (reaction shot) + diagram 07 hold |
| 8 | H | 7:27.63 | 1362 | clip window 07 (convergence) + diagram 08 hold |
| 9 | I | 8:13.03 | 1187 | clip window 08 (the grid) + diagram 09 hold |
| 10 | J | 8:52.60 | 2022 | diagram 10 + closing card (six steps + limits + CTA) |

The quiet "hold" tail of each segment (20–27 s) is an intentional **replay / study beat**:
the annotated diagram stays on screen with the original ambience while the viewer absorbs
the mechanism. It is not blank filler.

## 6. Reproduce / verify

```bash
python production/monarch-cam/replay_files_ep01_v12/build_video_v12.py --pilot  # filter smoke test
python production/monarch-cam/replay_files_ep01_v12/build_video_v12.py --all    # full rebuild
python production/monarch-cam/replay_files_ep01_v12/make_thumbnail_v12.py       # thumbnail + sheet
```

Requires `imageio-ffmpeg`, `numpy`, `Pillow`, DejaVu fonts. Intermediates live in
`production/monarch-cam/work/replay_files_v12/` (git-ignored, rebuildable).

## 7. Files

`REPLAY_FILES_Ep01_V12_10min_1080p30.mp4`, `QC_REPORT_V12.json/.md`, `EDL_V12_ACTUAL.json`,
`captions_v12.srt`, `thumbnail_v12.png`, `CONTACT_SHEET_V12.png`,
`clips/clip_window_01..08.mp4`, `vo/vo_A..J.mp3`, `build_video_v12.py`,
`make_thumbnail_v12.py`, `serve_v12.py`, `index.html`, `build.log` (ignored), this file.

`index.html` + `serve_v12.py` give a seekable in-browser player (HTTP Range / 206 support).
