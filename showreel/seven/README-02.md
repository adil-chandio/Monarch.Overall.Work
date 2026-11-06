# Reference 02 – MONARCH adaptation

Procedural 720×1280, 30 fps, 786-frame recreation of the selected “Faceless video edit” reference. The original's clock, audience, cards, countdown, hexagons, kinetic words and pills are independently redrawn and retimed approximately, not copied as images or represented as pixel-identical. Text and colors were adapted for MONARCH. The cards describe illustrative services, not real testimonials. The small ending monogram is an original graphic, not a claim to be an official logo.

Build:

```
python3 showreel/seven/render_02.py --reference /path/to/02.mp4
```

The reference video is not stored in this repository. Audio is stream-copied unchanged from the supplied reference and trimmed to 26.2 seconds; any original narration can differ from the rewritten captions. Obtain permission for the source soundtrack before public or commercial use. The original HE-AAC track may not be supported by all browsers. Requires Python, Pillow, NumPy, the repository fonts and FFmpeg from `tools/ffbin.py`. Instrument Serif is included with its SIL Open Font License in `assets/InstrumentSerif-OFL.txt`.

Validation: all 786 rendered video frames decoded; the first 25 seconds of decoded audio exactly matched the source audio.
