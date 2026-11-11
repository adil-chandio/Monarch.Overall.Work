# A Day in the Spotlight — illustrated POV draft

A fictional, generic celebrity's day, narrated in English from the viewer's perspective. It is not a biography, portrayal of a named person, or a factual account of any individual's schedule. The story moves from waking and messages to training, travel, interview, fan interaction, a premiere and a quiet night.

The film draws all images per frame with Pillow. It borrows broad framing, subdued sunset colours, circular-faced illustrated figures, lettering and vignette conventions from the user-provided farm-outbreak reference; no source frames or audio are embedded. This is a simplified procedural 2D draft, not photoreal, a physically simulated animation, or an exact stylistic match. Actions and lighting are keyframed/kinematic; the tests establish neither realism nor story quality. The final audio has not been human-listened to. Obtain necessary permissions for public/commercial use of reference-derived elements.

The original script is in `script.json`; the included clips were generated with Piper's Amy voice. The score and transition sounds are synthesized in `render.py`. The Amy model card identifies Mycroft Mimic 3 voice data as its training source; a third-party description reports CC BY-SA 4.0 for that data. The precise license requirements for the model and generated audio have not been independently resolved; verify rights before publication.

- Voice card: https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/medium/MODEL_CARD
- Model description: https://huggingface.co/qualcomm/PiperTTS-EN-Amy

## Render and verify

Python 3, Pillow, NumPy, imageio-ffmpeg and DejaVu Sans Bold at `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` are required. The renderer imports `showreel/farm_reference/render.py` for drawing utilities. Voice weights are not required: the generated narration WAVs are included.

```sh
python -m unittest discover -s showreel/celebrity_day/tests -v
python showreel/celebrity_day/render.py --output deliverables/celebrity-day-pov.mp4
```

The checks cover cue fit, deterministic seeking and frame changes only.
