# Reference-inspired celebrity-day test

A 60-second vertical, English, fictional football-celebrity day. This is an original illustration inspired by *observed* aspects of the user-supplied farm reference: circular dark faces with simple expressions, establishing views followed by face inserts, recurring locations, graphic labels and illustrated scenes. It does not reuse reference frames, sound, character designs or footage. It does not claim to depict a verified private routine, a physical likeness or an endorsement. Existing user-selected synthetic narration is reused, not a celebrity voice clone.

The script draws each of 1,440 frames at 540×960 and 24 fps from geometry, not still-image backgrounds or stock video. It contains 19 timed shots and hand-keyed body poses, camera-like shot changes, ball movement and crowd gestures; some parts of the sets remain static or reuse the same background geometry. This is 2D illustration, not physical 3D or a physics simulation. The kick and ball timing are approximate, not a validated foot-contact simulation. Captions paraphrase the narration. There is an original simple synthesized score and edit cues; no reference audio is copied.

Render with Pillow, NumPy and imageio-ffmpeg installed:

```sh
python showreel/reference_pov/render.py --output deliverables/monarch-reference-style-pov.mp4
```

QC performed: 18 sampled authoring frames visually checked on a contact sheet; final MP4 fully decoded by FFmpeg, reporting 1,440 frames and 60 seconds, with audio. No human listening pass or full frame-by-frame visual inspection was performed. Animation and design are still deliberately simple, the characters are generic, and this is a **test draft**, not evidence that the requested premium finish has been reached. File SHA-256: `2a8747691284cca13ed7fe164a5b52bb87161ba8c4e9aed6851b215206b22759`.
