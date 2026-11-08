# Walk v2 — research QA, not final

96 frames at 24 fps, generated 512×512 (822.9 seconds inference). The wider source crop prevents the recurrent head crop seen in v1; the full body is visible in sampled frames, though feet approach the lower edge and gait sometimes crosses unnaturally. The figure's size and outline fluctuate and the background is effectively static. This does not prove identity, physical ground contact, or a cinematic tracking camera.

A test 2D segmentation composite onto the clean street plate was inspected at six frames. Its zoom is not a real spatial camera move, contact/reflections are not matched, and the actor visibly remains an inserted silhouette. It is not production-ready. Model and source licensing remain unresolved.

A follow-up compared selfie and pose segmentation masks on seven sampled walk frames. The pose mask generally retained the feet better and excluded some background spill; the resulting 96-frame composite was sampled at 12 frames. Motion, wet-ground reflections, full-frame matte quality, and physical camera tracking are still not validated; this remains a research test, not a final shot.
