## Celebrity morning — painted 2D cut (60 s)

A 60-second portrait film, animated **frame by frame** from painted cels — not stills with a filter on them. Same script, narration takes and cue timings as the 3D v6 cut.

### Download

| File | Spec |
| --- | --- |
| `monarch-celebrity-story-2d-60s.mp4` | 60.00 s · 1080×1920 · 24 fps · H.264 High + AAC · 46.5 MB · −16.3 LUFS · −0.8 dBTP |
| `monarch-celebrity-story-2d-60s-preview.mp4` | 608×1080 · 4.3 MB |

### How it is made

| Production step | Implementation |
| --- | --- |
| Cel library keyed off flat green | `anim2d.py` |
| Poses locked to the model sheet | `assets/frames/`, generated against `assets/hero_*.png` |
| Head-anchored placement so a swinging arm never shifts the body | `anim2d.Cel.pivot` |
| Pose changes as **cuts**, not dissolves | `scene2d.pose_frame` |
| Lip sync driven by the recorded narration | `voice2d.py` → `anim2d.speak_mix` |
| Virtual camera over overscan plates | `scene2d.view_of` |
| Per-act light, grade, bloom, halation, grain | `scene2d.apply_grade` |

**14 shots, 1440 frames**, every one rendered individually.

### Verified

- 1440 frames, exactly 60.00 s
- −16.3 LUFS integrated, −0.8 dBTP true peak, LRA 3.0
- All 10 narration cues present and audible; tail resolves to near-silence
- Every shot reviewed at full resolution as a frame probe
- Character consistency checked across all 9 cels

### Where it is still short

- **Nine cels per character** — true limited animation, not 24 unique drawings per second
- **Two-drawing walk cycle** — readable but without a real weight shift
- **No eye blinks or eyelid acting**
- **The camera does the acting in static beats**

A real animated short made frame by frame; not a studio production.
