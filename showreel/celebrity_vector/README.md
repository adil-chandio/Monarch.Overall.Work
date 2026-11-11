# Fully rendered celebrity POV test

An original, stylized imagined-day test, 60 seconds, 540×960, 30 fps, 1,800 frames. It is fictional and does not claim to show Ronaldo's private routine or endorsement.

**Visuals:** `render.py` draws each frame procedurally from lines, polygons, circles, text and gradients; there are no background image files, photo plates, stock footage or pre-rendered visual inputs. Character joint positions, hands, props, balls, foreground elements, lights and scene geometry are code-generated at render time. POV hand/cup and hand/phone shots are mixed with third-person stickman shots. Independent foreground and background geometry create a shallow, illustrated 2.5D-style look; this is not a 3D renderer or a physically simulated camera.

**Audio:** uses user-selected synthetic narration from `showreel/celebrity_pov/audio` and original synthesized score/cues from the script. The narration is the same as the previous test; no celebrity voice clone. Captions paraphrase, not a verbatim transcript.

**Quality limits:** deliberately simple vector art, approximate keyframe interpolation and walking, not a polished premium character performance; foot contact and object interaction can be improved. No verified competitor footage was replicated. Measured mix approximately -16.7 LUFS / -1.37 dBTP; below the repo's -14 LUFS target, not a final publishing master. This is a creative test and needs full editorial, legal/rights and factual review before publishing.

From repository root, with Pillow, NumPy and imageio-ffmpeg installed:

```bash
python showreel/celebrity_vector/render.py --output deliverables/monarch-pov-fully-rendered-test.mp4
```

QA: ffmpeg decoded 1,800 frames over 60 seconds; selected time samples produced identical results on rerender and changed over time. The code does not read any visual assets.
