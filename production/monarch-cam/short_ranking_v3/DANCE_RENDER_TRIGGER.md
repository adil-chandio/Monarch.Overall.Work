# V3 render trigger

Render the separate 35-second clean-premium V3 ranked-animal Short after all five CC0 sources are contact-sheet reviewed and exact timecodes are locked.

Use explicit dispatch for the render:

```bash
gh workflow run monarch-cam-short-ranking-v3.yml --ref arena/390292fc-monarch-overall-work
```

The source-reconstruction workflow is explicit-dispatch / `SOURCE_RECON_TRIGGER.md` only, so a V3 render commit does not race it.

Render re-triggered after bounding all 13 narration slots at +12% TTS rate and preserving the 9:16 CC0 starfish aspect ratio with a centred 16:9 crop.
