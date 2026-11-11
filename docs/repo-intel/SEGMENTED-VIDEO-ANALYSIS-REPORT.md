# Target video analysis: 5 fps sampling experiment

## What was tested

Three public YouTube URLs were sent to Gemini `gemini-3.1-flash-lite-preview` as separate requested 5-second windows, at requested 5 fps. The final window of each video was shorter. All 12 requests returned HTTP 200 and `STOP`; all ranges from metadata time zero to the reported duration were requested (16 s, 13 s, 22 s). These are **model descriptions, not decoded frames**; no audio audit was performed in this pass.

In a separate Neymar 0–5 s test, VIDEO token usage was 441 at requested 1 fps versus 1701 at requested 5 fps; the 10–15 s window gave a different description. This is consistent with higher sampling and clipping but is not proof of exact sample count, offsets, or accurate timestamps. [Raw probe](gemini-sampling-probe.json); [all segment outputs and usage](gemini-segmented-forensics.json); [earlier full-video 1 fps pass](gemini-youtube-forensics.json).

## Model-reported patterns (unverified)

- **DusanFC / aWHX5Awe_TI:** The 0–5 s segment describes an outfield dribbling encounter, a POV switch, and then a yellow-kit match clip. Subsequent segments describe more match/POV action, celebration, and a crowd. The 15–16 s request reports POV hands, crowd, and a “Check the comments” overlay. Broad sequence may be useful for further investigation, but cuts and identities are not confirmed.
- **LV Animation / 8wtQAI_ZZlQ:** Segments consistently report three seated football-themed animated figures and a fixed field/goal setup. The 5–10 s response describes a purple spiked object affecting the right figure; 10–13 s describes a blue sphere and central figure. Exact action is disputed by the first full-video pass.
- **Stick Stuff Happens / GHT3RyE9wGI:** Segments describe a flat bedroom setup with a sleeping stick figure, clock, rooster, and a blue figure/drum. The final requested 20–22 s response describes a zoom-out and return to the bedroom. The precise order and actions need verification.

## Reliability checks and unresolved conflicts

- **Clip duration violation:** for the 5–10 s Neymar clip, the model reported local “6–7 seconds” despite a 5-second requested window. For Stick Stuff 20–22 s it described local seconds 0–6 despite a 2-second window. These entries must not be treated as evidence at those timestamps; even in-range events may be displaced.
- **Cross-pass disagreement:** for LV's opening, the first 1 fps pass says the ball repeatedly hits the center figure; the 5 fps opening says it rolls along the bottom and the figures remain seated. Both cannot be accepted as confirmed without visual verification.
- **Timing disagreement:** Neymar's 1 fps clip probe places the POV change around 0:01 and the yellow-kit cut around 0:03; its 5 fps probe places them near 0:02 and 0:04.2. These are model estimates, not measured cuts.
- **Source-frame and audio gap:** responses contain no inspectable frames; sampling at 5 fps misses intervening frames, and there is no independent playback or audio inspection. An HTTP 200 and video-token count do not establish fidelity or identity, nor do model-generated precise timestamps.

## Practical next step

Use independently accessible, authorized original footage if available to inspect frames and audio; otherwise try additional blind/overlapping model requests as consistency checks, not proof. A confidence-rated timeline should exclude boundary-violating events and keep disagreements unresolved. Do not use this output as a verified edit-by-edit blueprint or claim frame-by-frame analysis.
