# Farm outbreak opening — recreation study

This is an independently drawn, approximately 60-second study of the opening of a user-supplied farm-outbreak video. It is **not an exact recreation**: character designs, action, shot timing, detail, dialogue, sound and music differ substantially from the reference. It uses procedural 2D imagery, not fully rendered 3D or source screenshots. Reference frames were sampled during study rather than exhaustively reviewed, and the final audio has not been human-listened to.

The nine English narration passages in `script.json` are original paraphrases, not a verified transcript. The WAV files were synthesized using the Piper English Amy voice; the music and effects are procedurally synthesized by `render.py`. No reference images or audio are included. Amy's model card identifies Mycroft Mimic 3 voice data as its training source; a third-party model description reports CC BY-SA 4.0 for that data. The exact rights and obligations for this voice model and its generated output have not been independently established. Verify those rights and obtain any necessary permission for the reference-derived elements before public or commercial use.

Voice references: https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/amy/medium/MODEL_CARD and https://huggingface.co/qualcomm/PiperTTS-EN-Amy

## Rebuild

Python 3 with Pillow, NumPy and imageio-ffmpeg is required, plus DejaVu Sans Bold at `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`. Existing generated voice clips are included; model weights are not needed for rendering.

```sh
python -m unittest discover -s showreel/farm_reference/tests -v
python showreel/farm_reference/render.py --output deliverables/monarch-farm-reference-recreation.mp4
```

Tests check deterministic frames, scene action changes, and narration cue durations; they do not establish fidelity or perceptual quality.
