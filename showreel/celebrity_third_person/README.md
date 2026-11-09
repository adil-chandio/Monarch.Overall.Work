# A Day in the Spotlight — third-person 3D study

Fictional, generic celebrity-day animation, not a biography or portrayal of any named real person. Every scene is built as Blender geometry, with an articulated character, 3D sets, lamps and cameras. No source frames, footage, music or stock plates are used. The black head and white eyes, warm/cool colour contrast, horizon and letterboxing are loosely inspired by the user-provided reference, not a faithful reproduction.

This remains a **rough, stylized test**, not a polished or reference-quality production. The character is an adapted Quaternius CC0 mannequin with simple 3D face geometry; generic looping actions and hand-authored root translations are not performance capture or physically solved movement. Sets are sparse, hands and interactions are approximate, and the fan scene does not depict a literal autograph. Character expressions, realistic physics, believable object contact and premium detailed environments remain unresolved. Synthetic narration is fictional, and its final mix has not been human-listened to. The voice clips use Piper Amy; its model card identifies Mycroft Mimic 3 voice data, with one third-party description reporting CC BY-SA 4.0 for training data. Exact rights and conditions for the model and audio have not been independently established. Check voice rights and any required reference permissions before publication.

- Mannequin and action library source and CC0 attribution: `../celebrity_3d/README.md` and `../celebrity_3d/assets/LICENSE-CC0.txt`.
- Amy model card: https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/medium/MODEL_CARD
- Amy third-party description: https://huggingface.co/qualcomm/PiperTTS-EN-Amy

Render with Python 3.11, `bpy==4.2.23`, Pillow, NumPy, imageio-ffmpeg and system graphics libraries. `render.py` outputs a silent selected time range. For a local render, run `python showreel/celebrity_third_person/render.py --output silent.mp4`, followed by `python showreel/celebrity_third_person/mux.py silent.mp4 <output.mp4>` to add the included voice clips and synthesized score. The animation is sampled at 18 fps by default; the CC0 motion clips are evaluated on a 24 fps Blender timeline. The generated WAVs are included; model weights are not.

Tests verify narration cue durations only; rendering and visual review do not verify artistic quality.

## Render QC

`deliverables/celebrity-third-person-3d.mp4` is 60 seconds, 480×270, 18 fps, H.264/AAC. FFmpeg decoded all 1,080 frames and audio; mean/max sample levels were -16.4/-1.4 dBFS. Thirty samples at 2-second intervals were visually reviewed. These checks are not continuous motion review, a true-peak/loudness certification, or a listening test. SHA-256: `563f15b9a39f55b5f8d44630455cd899b40dc2d7c5eb61baf18db3a718bd0f68`.
