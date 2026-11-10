# Experimental mammoth locomotion — evidence and limitations

## Reference, not a claim of direct mammoth observation

- Kongsawasdi et al. studied walking Asian elephants at a reported average 1.1 m/s. Their sample had lateral-sequence footfalls, approximately 2.26–2.34 s stride times and 72.64–76.09% stance fractions. [Paper](https://vetdergikafkas.org/uploads/pdf/pdf_KVFD_L_2053.pdf).
- Genin et al. measured living Asian elephant limb mechanics: compliant limbs and small vertical center-of-mass movement even during slow walking. [PNAS, 2010](https://www.pnas.org/doi/full/10.1073/pnas.0911396107).
- Dagenais et al. investigated live elephant trunks as continuously flexible muscular hydrostats with complex motion. This model does **not** reproduce those degrees of freedom. [Current Biology, 2021](https://www.cell.com/current-biology/fulltext/S0960-9822(21)01133-7).

These papers describe living elephants, not direct measurements of woolly mammoths. They guide a conservative illustrative approximation, not a validated reconstruction. The prototype model's proportions and speed are not a measured specimen. It is not appropriate to describe this as a scientifically proven mammoth gait.

## Prototype behavior

`gait.mjs` uses a four-beat lateral footfall sequence (left hind, left fore, right hind, right fore), 76% stance, a 2.3 s steady-state cycle and smooth acceleration from rest. The body advances while each stance target stays fixed horizontally. Swing height is eased to zero at contact. `scene.mjs` projects foot centers onto rendered terrain triangles, pivots and stretches simple single-segment legs toward those targets, and keeps separate foot meshes level. Fur instances are parented with the corresponding limb or foot. Camera follows the moving animal; the contact shadow follows the body.

These are **kinematic constraints**, not a simulation of momentum, muscles, gravity, forces, balance or real skin. The geometry does not solve a multisegment skeleton. Foot edges can intersect sloped terrain or rocks despite the centre target being on the mesh. Leg stretch and rigid segments can look artificial; body motion and weight transfer are not validated, and the trunk, ears and face have no animation rig. No trunk, vegetation, foot or rock collision is solved. The mesh and materials are stylized and the landscape is not a geographic reconstruction. The animal can walk through rocks. These issues must be resolved, followed by real motion-reference review, before calling the scene realistic or final.

## Tests

- `node --test .../test_gait.mjs`: analytic phase and continuity; planted horizontal targets; 3-foot minimum support; lateral sequence.
- `node .../verify_scene.mjs`: terrain triangle ray samples, target/world-transform agreement, planted-target slip over the sampled frames, deterministic posing and console/page errors.
- Neither test detects full-foot intersection, proves real-world gait accuracy, checks all possible inputs, validates moving-body mass distribution or replaces continuous visual review.

The previously committed 22-second test (`Last-Mammoths-3D-Isolation-Test-22s.mp4`) predates this locomotion work. It does not contain the current gait.
