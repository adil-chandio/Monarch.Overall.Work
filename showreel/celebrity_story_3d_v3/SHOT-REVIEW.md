# Viewer and animation review: celebrity-day revision

This review concerns the previous 60-second video and the four screenshots the user supplied. The previous output was inspected at approximately one frame per second across 0–60s; selected movement windows had previously been sampled at 6 fps. These are samples, not a claim of frame-by-frame review or human audio listening. Narration timing comes from `script.json` and the cue WAV durations, not a fresh listening transcript.

| Approx. time / story beat | Viewer / animator problem in v2 | Revision |
|---|---|---|
| 0–3.5: call begins | Table penetrated the figure; first shot had little visual focus. | Moved table and dressing out of path; closer opening framing with eased push-in. |
| 3.5–7.2: call | Horizontal slab crossed mouth/chin instead of reading as a phone at the ear. | Rebuilt upright handset, repositioned at wrist/ear, changed shot angle. Grip remains authored, not solved. |
| 7.2–13.5: coffee | Thick white cylinder appeared to intersect or float beside the hand/mouth. | Smaller cup, dark liquid and handle; different hand-relative offset, tilted sip and camera angle. Contact is still approximate. |
| 13.5–19.7: hallway | Walk and camera were repetitive; skyline was a wall of thin bars. | Same underlying motion clip, eased camera, dimensional irregular buildings, gradient sky and surface relief. |
| 19.7–27.6: event | Static low-detail camera operators and unmotivated lights. | Two distinct textured rigged attendees behind barriers with held devices; short flashes aligned to the synthetic shutter cues. |
| 27.6–36.4: studio | Table penetrated the hero; the two speakers faced the audience rather than one another. | Table moved; root quaternion rotations orient subjects toward each other. They remain standing and interaction is not a physical conversation simulation. |
| 36.4–44.3: fan greeting | Subjects were on the same side of the barrier; generic figures obscured the view. | Fan moved behind the rail; revised camera keeps both subjects visible. A greeting is gestural, not a handshake/autograph. |
| 44.3–52.2: public attention | Same wave repeated; few surrounding people. | Distinct background performers and timed device flashes. The hero still reuses a generic wave. |
| 52.2–60: quiet ending | Table penetrated the legs; sunset did not clearly transition. | Clearer path and cooler sky; approximate facial animation and an eased shot remain. |

The spatial audit uses sampled foot/toe landmarks and table bounding boxes; it cannot prove the absence of every mesh collision. Props follow authored positions and do not have deformable grips, collision response or liquid simulation. The city, furniture and crowd remain simplified; the revised work cannot be guaranteed flaw-free or equivalent to a full high-end film production.

## Final render QC

The final 960×540, 24 fps file decoded all 1,440 video frames and 60 seconds of audio without decoder errors. All 60 one-second samples and 6 fps samples over one-second windows starting at 3, 10, 14, 27, 36, 44 and 52 seconds were visually inspected. The table crossings visible in the previous screenshots are no longer visible in those sampled shots. The phone reads upright near the ear and the cup reads near the mouth, although finger grip and precise contact remain approximate. The studio subjects face one another and the fan is beyond the rail. Walks and waves still reuse clips, and backgrounds remain sparse and stylized. Audio peak measured −1.3 dBFS; no human listening verification was performed. The landmark table audit reported a minimum separation of 1.2085 m at 0.25-second intervals, without full mesh collision verification.
