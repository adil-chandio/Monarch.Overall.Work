# Reference 01 – MONARCH adaptation

This is a frame-by-frame procedural reconstruction of the first selected 11-second reference from the user's seven-video Drive folder. Its visuals are newly drawn, with a red/black treatment and the words “the MONARCH STUDIO.” The motion and typography approximate the reference; they are not a pixel-identical copy. The reference's original audio is copied from the supplied MP4 and trimmed at the video boundary. Rights to that soundtrack are not established: secure permission before public/commercial use.

## Build

```
python3 showreel/seven/render_01.py --reference /path/to/01.mp4
```

Output: `public/demo/monarch-reference-01.mp4`. Requires Python, NumPy, OpenCV, Pillow, the repository's Poppins font, and the FFmpeg binary resolved by `tools/ffbin.py`. The original reference is intentionally not stored in the repository and must be supplied when rebuilding. Output is 1276×718, 30 fps, 330 frames. The original is HE-AAC; the output retains that stream for fidelity, which may not play in every browser.
