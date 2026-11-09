# V7 — viral-style ranking rebuild after V6 rejection

## What the user rejected

The user rejected V6 with six reference screenshots and said: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ... trending viral videos ko Uthao clips social media par TikTok Instagram yt or Reddit Dailymotion ... bas clips mazedar next level honi chaiye ... best perfect mazedar hooked engaging scene nikalenge ... ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha to aise hi to ab banao ache se poora`.

The screenshots show a vertical social video with:

- a **blurred full-frame background**, not a large empty black area;
- a sharp, **uncut source frame** with no subject cropped off;
- a centered two-line hook: `Ranking Most Impressive / Moments Ever`, with `Most` yellow and `Impressive` red;
- a left `1.`–`7.` list whose numbers and short black caption plates remain **fully visible** over the video;
- right-side heart/comment/save/share/remix icons;
- a bottom `@handle`, caption bubble, Subscribe button, caption line and app/nav chrome;
- all seven rank labels visible from the first frame, with the active-rank highlight progressing as moments play.

V6 instead produced a mostly empty dark top area, a boxed `1.-7. LIST` panel, small uppercase labels and CC0 animal-original clips. Its technical QC did not check the actual visual mismatch. V5 and V6 remain rejected; neither is modified.

## V7 build

V7 is a separate package. It uses **ten rights-cleared social-origin Commons originals** from YouTube, Vimeo, SWNS/Instagram and police/social-video sources. The runner:

1. verifies each candidate's Commons API extmetadata, licence, creator, source page, original SHA-1 and social-origin Credit;
2. downloads the original or a Commons-generated VP9/Opus transcode;
3. measures native audio RMS and one-frame-per-second motion, writes candidate contact sheets, and selects the seven strongest audible/moving 8.6-second windows;
4. locks exact 60.0s / 1800-frame / 30fps / 1080x1920 timeline scenes ranked `7 → 1`;
5. renders a **blurred full-frame background** plus a sharp uncut source frame, then overlays the screenshot-style hook, left rank plates, right platform UI, @Monarch-Cam handle, caption bubble, Subscribe button and bottom chrome;
6. builds only raw per-window native source audio and runs the unchanged nine web audio gates plus V7 technical QC.

The deliverable is `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.

## Rights boundary

The user asked for trending social-platform clips. V7 does **not** download unverified trending TikTok, Instagram, Reddit, Dailymotion or YouTube reposts, because no rights clearance exists for those files. It uses per-title rights-cleared social-origin originals mirrored on Wikimedia Commons, with PD/CC0/CC BY 3.0 API verification, CC BY attribution and a social-origin ledger. It does **not** claim the clips are currently trending, that the exact reference clips were used, or that every named platform is represented. If the user supplies specific clips plus permission/rights records, a later V8 can swap them in through the same pipeline.

## No acceptance claim

This is a technical build for human review. No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, subscribe/like, same-path or audience-result claim is made.
