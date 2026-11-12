# Running pilot v2 — research only, NOT a final shot

24 frames, 24 fps, 512×512. The pose renderer's explicit face landmarks and corrected body joint colours recovered a male-looking, dark-suited character relative to the previous incorrect long-haired figure. Actual sampled frames were inspected, including enlarged head crops.

**Fails final quality gate:** the face is still stylised and not an accurate match, the mouth changes shape unnaturally, hands are incomplete/distorted, some foot shadows detach, and the setting remains locked in place. Only one second exists; there is no approved 20-second film. Third-party model weights need license clearance before commercial use.

A local face-tracking composite proof-of-concept using only the approved generated keyframe reduced some mouth distortion, but freezes facial expression and requires further testing of alignment, edges, and motion; it is not a replacement for true face animation and was not accepted as final. The next pilot extends the motion to 72 frames by repeating a near-matched recorded gait; this is an experiment, not a guarantee of continuous natural foot contact or temporal consistency.
