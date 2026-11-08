# Full-duration tall running test — research QA, not final

The 72-frame, 24 fps portrait test reduced edge cropping and hand scale problems compared with tall v1. The sampled frames still show inconsistent arms and hands, a sleeve changing to a skin-like color at the start, floating feet and uncertain contact, and apparent likeness drift. A 16:9 composite with optional pose-tracked shadows was tested locally; the 2D plate slides, the figure still floats, and ground reflections are not physically matched. It is not an acceptable final shot. Model licenses remain unresolved.

A local-only reference-face warp was also tested using the supplied character image. It produced obvious dark patches and seams and was rejected. The source image and the derived test frames were not uploaded to the public repository.

Follow-up matting QA: selfie segmentation dropped the runner's raised rear leg (for example frame 6). Replacing that matte with MediaPipe pose segmentation preserved it in the sampled frames 0, 6, 12, and 18 and in a 12-frame composite contact sheet. The result still uses a flat panning plate and approximate projected shadows: foot contact, reflections, likeness, suit consistency, and all-frame matte quality remain unverified. It is research-only, not a finished shot.
