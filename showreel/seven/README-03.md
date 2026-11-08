# Reference 03 – MONARCH adaptation

A procedural 1280×720, 30 fps, 360-frame re-creation of the supplied “Hi” reference, with a hand-built satin background, drafting lines, dimensional typography, eye/pupil animation, and rotating role captions. “MONARCH” replaces the reference creator's name; the copy changes to “We're” and “Studio”. This is an approximation made from independently rendered shapes and text, not an exact or frame-for-frame reproduction. Text and timings are editable in `render_03.py`.

Build:

```
python3 showreel/seven/render_03.py --reference /path/to/03.mp4
```

The original input is not stored here. Its original HE-AAC soundtrack is stream-copied and cut at 12 seconds, so original spoken words (if present) may not match the new typography. Rights to that soundtrack have not been established; obtain permission before public or commercial use. HE-AAC might not work in all browsers. The build requires Python, Pillow, NumPy, OpenCV, the supplied fonts, and FFmpeg from `tools/ffbin.py`. Inter and Oswald are distributed in `assets/` with their respective SIL Open Font licenses.

Validation: all 360 frames decode; the first 11.9 seconds of decoded audio match the reference exactly.
