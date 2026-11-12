# V15 Plan — Social Viral Shocking + Intro + Audio Design

**User demands (2026-11-12):**
1. Clips social media se viral short reels TikTok shocking moments accidents incidents, mazedar unique caught-on-camera — NOT Wikipedia chutiya clips.
2. 1 acha intro jo curiosity + FOMO build kare, audience ko roke.
3. Audio map: kahan clip awaz, kahan hamari voice, kahan dono — volume control me, voice sahi se sunai de.
4. Clips Reddit/Twitter/Dailymotion/TikTok/Instagram/YT/Facebook/Chinese app se — andar mazedar hooked engaging eye-catching mind-blowing unbelievable shocking moments, bekar clips nahi.

**Honest boundary (no invented claims):**
- Direct TikTok/Instagram/Reddit/Twitter/Facebook downloads: blocked hosts (only github/pypi/npm allowed in sandbox), no API for those platforms, no rights ledger. Cannot download unverified reposts and claim clearance.
- What IS possible: (a) Real YouTube Data API scouting via GitHub Actions (`YOUTUBE_API_KEY` secret) for viral caught-on-camera shocking moments — real view counts, real titles, real transcripts where available. (b) Commons `video2commons` mirrors whose metadata records YouTube/TikTok/Dailymotion origin — these ARE social viral clips, rights-documented (PD/CC0/CC BY). V14's 20 are already social-origin (Bean YouTube, Chiitan YouTube, etc.), not old Wikipedia films.
- Shocking accidents/incidents: safety gate blocks graphic/tragic (crash, disaster, blood, gore, dead). V15 keeps shocking-but-safe: funny accidents, near-misses, slips, prank screams, instant karma — NOT graphic injuries/deaths. This matches owner's original "funny/shocking, NOT graphic/tragic" rule.
- No invented retention/CTR/RPM, no guaranteed views/virality, no legal clearance, no upload/publish.

**V15 changes:**
1. **API scouting:** Trigger `yt-caught-on-camera-forensic-v13.yml` with new shocking queries (caught on camera shocking, viral accident caught on camera, unbelievable moment, etc.) via marker file. Real API lanes, real million-view details.
2. **Intro (0–15s, footage-based, no static card):** New `chunk_00.mp3` curiosity/FOMO VO over fastest clips (Bean close-up, Chiitan, scary maze scream). Text: "You won't believe clip 17..." style. Frame 1 still footage. On-screen: ROUND 1 label + captions. No title card.
3. **Audio design (ducking):** Native 0.60 between VO, 0.15 during VO (volume enable between VO windows), VO 1.0. VO clearly audible, native audible in gaps. Map documented in EDL + ABOUT.
4. **Clips:** Keep V14 20 (social-origin, rights-documented, audited). No new Commons shocking funny files exist beyond V14 (doorbell/viral searches return crime/crash/missile — blocked). API scouting informs VO/intro wording, not new downloads.
5. **Rebuild:** Pilot → full 540s, QC, contact sheet, release v15.

**Files:**
- `research/caught_on_camera_v13/V15_PLAN.md` (this)
- `production/monarch-cam/caught_on_camera_v13/vo/chunk_00.mp3` (intro)
- `production/monarch-cam/caught_on_camera_v13/vo_script_v13.json` (11 chunks: 00 intro + 01–10)
- `production/monarch-cam/caught_on_camera_v13/build_video_v13.py` (V15: intro + ducking)
- API evidence: `research/caught_on_camera_v13/api_evidence/lanes/*`, `channels/*`
