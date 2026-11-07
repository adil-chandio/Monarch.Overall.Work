# MONARCH — night temple (20-second motion study)

Five requested scenes, with two keyframes for the final turn/close-up. Keyframes
are AI-generated from the user-supplied character image, and were uploaded to this
public branch with the user's permission. No original user photo is committed.

The first phase uses private Kaggle notebooks to make six short LTX image-to-video
clips, if the existing configured GPU access is still available. Generation is
not deterministic quality assurance: face identity, anatomy, walking, running,
turning and scene continuity must all be reviewed before editing. The final edit
must not claim these are accurate if the clips fail that review.

Planned duration: 0–4 street, 4–9 gate, 9–13 aerial, 13–16 running,
16–20 turn and glowing-eye close-up. No reference sound was supplied.

## Native-motion review cut

`monarch-temple-native-review.mp4` is a 20-second review cut using the WAN 2.2
scene candidates (512×288 generated at 24 fps, upscaled to 1280×720). It uses
native generated frames instead of optical-flow interpolation. The 0/4/9/13/16
second cuts are frame-accurate, and it reuses the earlier procedural ambience.
The close-up red-eye effect is added using tracked facial landmarks. This is
not a flawless final: the face changes during the turn, the running frame cuts
off the feet later in the shot, and the aerial descent is subtle. These are
model limitations visible in the review, not quality guarantees.

Rebuild with `python production/mafia-temple/build_native_edit.py` after
installing numpy, opencv-contrib-python-headless, mediapipe and imageio-ffmpeg.
The generated scene clips and earlier video provide the source video/audio.
