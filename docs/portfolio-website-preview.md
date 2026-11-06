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

## MONARCH visual rebuild

The portfolio now has an independent, reference-inspired multi-cursor visual rebuild.
It plays once per browser session after the existing intro is completed or skipped;
visitors can replay it with **REBUILD** in the navigation. It is a staged presentation
of the existing page, not real agents or live coding. The desktop tour uses 24
color-coded cursors (12 on mobile), temporary selection frames, a progress control and
auto-scroll. Pause/resume, 1×/2×/3× speed, skip, replay and go-live are supported.
Wheel, touch, page clicks or Escape return control; reduced-motion users are not
shown the animation. No reference sound or original animation-engine code is used;
there is no rebuild-specific soundtrack. The effect is an interpretation, not a
pixel-identical copy. Intro and film cards are unchanged.

Implementation: `public/portfolio/assets/rebuild.js` and `rebuild.css`. During the
rebuild, native reveal and scramble animations are suspended; each element waits for
its assigned cursor to approach, draw its outline, then reveal the element in sync
with the cursor. The scroll pace gives unfinished work time to complete. Counters
start after their containing element is revealed. Skip restores the usual reveal
behavior for sections not yet visited. The intro flow emits `monarch:intro-done`;
the effect removes temporary UI and restores page content when it completes, is
interrupted, or encounters an animation error. The
reference's Swarm Rebuild project credits Joel Califa and states that its code has no
license; consult the original authors before reusing it. This implementation does not
include that code. Reference: https://github.com/DhvanilPatel/swarm-cursors

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

The rebuild was exercised in desktop (1440×900) and mobile (390×844) Chromium:
first-visit intro/skip, once-per-session auto-start, full accelerated tours,
pause/resume, speed, skip, Escape, final controls, replay, reduced motion, cleanup,
and retained Paanch Rules player. The tour visits all sections, leaves no hidden
items and preserves all ten work cards.

### Browser synchronization regression test

The optional integration test requires a separate `puppeteer-core` installation and
a Chromium executable; it does not add either to the application dependencies.
It starts the range-aware preview server on a free port. For example:

```sh
CHROME_PATH=/path/to/chromium \
PUPPETEER_CORE_PATH=/path/to/node_modules/puppeteer-core \
node scripts/test-portfolio-rebuild.cjs
```

The test samples both desktop and mobile tours through all sections, checking that
waiting/drawing elements remain hidden, reveal masks and cursor positions agree,
no native reveal escapes the rebuild, and completion clears all temporary state.
