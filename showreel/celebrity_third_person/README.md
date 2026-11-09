# A Day in the Spotlight — third-person 3D study

Fictional, generic celebrity-day animation, not a biography or portrayal of any named real person. Every scene is built as Blender geometry, with an articulated character, 3D sets, lamps and cameras. No source frames, footage, music or stock plates are used. The black head and white eyes, warm/cool colour contrast, horizon and letterboxing are loosely inspired by the user-provided reference, not a faithful reproduction.

This remains a **rough, stylized test**, not a polished or reference-quality production. The character is an adapted Quaternius CC0 mannequin with simple 3D face geometry; generic looping actions and hand-authored root translations are not performance capture or physically solved movement. Sets are sparse, hands and interactions are approximate, and the fan scene does not depict a literal autograph. Character expressions, realistic physics, believable object contact and premium detailed environments remain unresolved. Synthetic narration is fictional, and its final mix has not been human-listened to. The voice clips use Piper Amy; its model card identifies Mycroft Mimic 3 voice data, with one third-party description reporting CC BY-SA 4.0 for training data. Exact rights and conditions for the model and audio have not been independently established. Check voice rights and any required reference permissions before publication.

- Mannequin and action library source and CC0 attribution: `../celebrity_3d/README.md` and `../celebrity_3d/assets/LICENSE-CC0.txt`.
- Amy model card: https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/medium/MODEL_CARD
- Amy third-party description: https://huggingface.co/qualcomm/PiperTTS-EN-Amy

Render with Python 3.11, `bpy==4.2.23`, Pillow, NumPy, imageio-ffmpeg and system graphics libraries. `render.py` outputs a silent selected time range. The manual GitHub Actions workflow renders 12 chunks; after downloading them into one directory, `python showreel/celebrity_third_person/mux.py <clips-dir> <output.mp4>` assembles the original script's included voice clips and synthesized score. The generated WAVs are included; model weights are not.

Tests verify narration cue durations only; rendering and visual review do not verify artistic quality.
