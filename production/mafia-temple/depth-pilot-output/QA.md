# Relative depth and camera experiment — not final

Depth Anything V2 Small inferred relative depth from three **generated scenery** images, not from the user's original reference. The upstream project states the small model is Apache-2.0: https://github.com/DepthAnything/Depth-Anything-V2. Review all model and third-party terms for the final use.

A local 96-frame aerial experiment reprojects the still with the inferred depth and a downward/forward virtual camera. The result has some depth-dependent movement, but is not a measured 3D scene, lacks unseen surfaces and animated fog, crops the roof, and can warp geometry. It is not an approved aerial shot. A depth-guided street composite was also checked at three frames; the character still has no matched reflections or verified foot contact and the scene is a 2.5D approximation, not a real camera track. Keep both internal and review every frame before any use.
