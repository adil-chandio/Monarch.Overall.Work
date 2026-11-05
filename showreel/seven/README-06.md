# Reference 06 — MONARCH adaptation

`public/demo/monarch-reference-06.mp4` is a 10-second, 1080 × 1920, 60 fps adaptation of the sixth supplied reference. The main floating card, editor-like panel, statue, book, portrait and circular end graphic follow the reference's broad arrangement and sequence, with MONARCH OS and MONARCH Studio copy. The five work domains mentioned on screen are documented in the repository README.

This is an approximation, not a pixel-identical reconstruction: the editor panel and book are procedural illustrations, and the sculpture, profile and crown are independently AI-generated stills animated as layers rather than the reference's original artwork or 3D animation. The book is a graphic metaphor, not an actual MONARCH product. All 600 output frames decoded successfully. The supplied reference has no audio stream, so this adaptation is also silent.

## Rebuild

Requires Python 3, Pillow, NumPy, OpenCV and the FFmpeg helper/dependencies used elsewhere in the repo:

```sh
python3 showreel/seven/render_06.py
```

The render does not require the original reference file. Generated assets are `assets/06-bust.png`, `assets/06-profile.png` and `assets/06-crown.png`. Fonts: Inter (`assets/Inter-OFL.txt`), Instrument Serif (`assets/InstrumentSerif-OFL.txt`) and Poppins (`assets/Poppins-OFL.txt`).
