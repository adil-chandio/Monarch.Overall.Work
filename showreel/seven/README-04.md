# Reference 04 – MONARCH adaptation

Editable procedural 720×1280 / 30 fps / 1097-frame adaptation of the selected Arabic-captioned reference. The layout and sequence approximately follow the reference: product cards, red spotlight, storefront, audience, customer-question collage, connected marketing icons, creative tests, results folder, analytics, and closing typography. Graphics and animations are rebuilt, rather than taken from the reference frames. It is not a pixel-identical or full 3D recreation: some photographic objects are AI-generated stills animated as layered cutouts, and other objects are drawn. Product, store and audience images are illustrations, not real MONARCH clients, products, or results. The charts are explicitly illustrative.

Build:

```
python3 showreel/seven/render_04.py --reference /path/to/04.mp4
```

The supplied reference file itself is not stored here. Its original HE-AAC track is stream-copied and trimmed to video duration. That track includes the reference's Arabic narration, which may mention the original brand and does not match the new English on-screen copy; it should be replaced with a licensed MONARCH voiceover for publication. Rights to the original soundtrack are not established; obtain permission before reuse. Some browsers do not support HE-AAC.

Requires Pillow, NumPy, OpenCV, the bundled assets/fonts and FFmpeg from `tools/ffbin.py`. The AI-generated source assets are kept under `assets/04-*.png` for editing. Validation: all 1097 video frames decode; 36 seconds of decoded audio match the source.
