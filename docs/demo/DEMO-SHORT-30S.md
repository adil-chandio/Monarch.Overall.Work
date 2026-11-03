## 30-second demo short — `youtube automation`

Every number on screen is read out of `public/yt-intel/*.json` at render time. Nothing is typed by hand.

| fact | value |
|---|---|
| verdict | **SHARPEN 59.4** (confidence 0.85) — not a GO |
| demand signal | 80/100 |
| sample | 30 videos, median 51,654 views, top-3 share 0.50 |
| comments read | 100 — **11% want to buy teaching**, 1% asked for a sequel |
| packaging | 100% of thumbnails carry a face; 8/12 use red |
| audio | −16.6 LUFS (integrated) |
| video | 1920×1080, 30 fps, 30.0 s, 1.2 MB |

The short is not a tutorial. It is the 30 seconds that earns the right to make one — and it ends on the topic's real verdict rather than a promise.

Rendered by `showreel/demo_short.py` (PIL frames piped straight to ffmpeg). Re-render with:

```bash
python showreel/demo_short.py
```

## Download

Direct link (branch-scoped, always the latest render):

```
https://raw.githubusercontent.com/adil-chandio/Monarch.Overall.Work/arena/8bfd4d0e-monarch-overall-work/public/demo/demo-short-30s.mp4
```

Verified: 1,193,804 bytes, git blob `547c254`. To keep the link stable across branches, merge
this into `main` and swap the branch segment for `main`.

## Why these numbers

The topic was chosen by the data, not by taste. `youtube automation` scored demand 80/100 with
a top-3 share of 0.50 — real appetite, no single owner — while 3 of its top 5 videos are titled
"how to start" and none of them show who quietly failed. The audience then said the rest: 11%
of 100 comments want to buy teaching, so the next asset is not another free tutorial.

The video ends on `SHARPEN 59.4`, not `GO`. A demo that promised a winner would be the exact
thing this research pipeline was built to stop doing.
