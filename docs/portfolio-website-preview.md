# Portfolio website update — branch preview

This is a reviewable snapshot of the separately maintained `adil-chandio/portfolio`
website (source main commit `4a0664ce4e9d11a3c8836d42467fccdcd522140b`). It is
hosted at `public/portfolio/` in this branch for review. It does **not** update the
separate repository or its GitHub Pages deployment automatically.

The intro/replay and the first card in “Films I made” use
`public/demo/monarch-portfolio-v5.mp4` (36.57 seconds). Paanch Rules and Monarch: Law
One remain, using the repository's existing copies under `public/proof/`. Seven
individual enhanced MONARCH adaptations replace the other old film cards. For browser
compatibility, the 01–05 web MP4s in `public/portfolio/media/` copy the video stream
and transcode the original reference audio to AAC-LC. 06 is the BTS-free crop; 06 and
07 are silent. Their original videos and the main film are shared from `public/demo/`
and were not overwritten. Full-frame posters and player sizing retain the different
aspect ratios; the phone layout has a swipeable carousel.

## Review locally

```sh
python3 scripts/preview-portfolio.py
# Open http://localhost:4176/portfolio/
```

The preview server serves the repo's `public/` root and supports HTTP range requests
for seeking. The main Vite build also copies the portfolio snapshot to `dist/`; on the
Vite dev server use `/portfolio/index.html` rather than `/portfolio/`.

## Before publishing the separate website

Publishing this branch does not publish `adil-chandio.github.io/portfolio/`. The
satellite's files/media must be updated in its own deployment workflow. In particular,
the snapshot's `../demo/` and `../proof/` media paths refer to this repo's public root;
a standalone portfolio deployment must copy those MP4s to its own `media/` directory
and update those URLs, while retaining its own Paanch Rules, Law One and proof-loop
files. Check current upstream changes before applying this snapshot. Rights for the
reference-derived soundtrack(s) have not been established; obtain permission before
public or commercial publication. The individual enhanced videos are motion studies,
not client work or exact copies; see `showreel/seven/enhanced/README.md`.

## Verification

The main Vite build and config tests pass. The preview was checked in desktop and
mobile Chromium: the intro plays, all ten cards have the expected titles and media,
and player metadata loads for the new portfolio, both retained films and the new
showcase clips. HTTP range requests return 206. Video 06 has 720×964 cropped footage;
video 07 has 1080×1920 footage. Sample frame posters were extracted from the actual
videos. The original website in the separate repository has not been changed.
