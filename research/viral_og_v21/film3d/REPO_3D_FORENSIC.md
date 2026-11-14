# Repo ka 3D stack — forensic audit (2026-11-05)

Aap ne poocha: "repo me 3D ka hamara level kya hai, kaise kaam karte hain, har detail nikaal ke lao."
Ye woh audit hai. **Har claim ke saath file path hai** taake aap khud check kar sakein. Jahan cheez
maujood nahi, wahan `NAHI HAI` likha hai — guess nahi kiya.

---

## 1. Repo me 3D ke **paanch** raste hain (aur unka asli status)

| # | Route | File | Status | Yahan chalega? |
|---|---|---|---|---|
| 1 | `blender_world` (Blender 4.5 LTS, Eevee Next, GPU) | `skills/openmontage/.agents/skills/3d-asset-generation/SKILL.md:20` | **Best quality** — poora scene, GI, fur, volumetrics | ❌ Blender binary nahi, GPU nahi |
| 2 | Atlas Tripo H3.1 / fal Hunyuan 3D (text-to-3D meshes) | same file, `:11-19` | Paid API ($0.22–$0.44 per asset) | ❌ Registry/tool maujood nahi, key nahi |
| 3 | Three.js / WebGL (browser-native world) | `skills/openmontage/.agents/skills/threejs-*/SKILL.md` (11 skills) | Real-time, PBR, shaders | ⚠️ Shim possible, magar **libGL nahi** — `ldconfig` me `libGL`, `libEGL`, `libOSMesa` kuch bhi nahi |
| 4 | Hyperframes (HTML/GSAP motion, 2.5D) | `skills/hyperframes/*/SKILL.md` | Motion graphics, captions, typography | ✅ (magar 3D nahi) |
| 5 | **Numpy point/raymarch renderer** (maine likha) | `research/viral_og_v21/film3d/{geo3d,render3d}.py` | Real geometry, real lights, per-frame | ✅ **yahi chal raha hai** |

**Nateeja:** repo me 3D ka *instruction layer* poora hai (947 skills me 189 `monarch-studio` me, jisme 11 Three.js + 1 Blender + 1 asset-gen), magar **is machine par sirf route 5 chal sakta hai.**

---

## 2. Blender route — kya likha hai, kya chahiye

`skills/openmontage/.agents/skills/3d-asset-generation/SKILL.md` se, word-for-word requirements:

- **Renderer:** Blender 4.5 LTS / Eevee Next. (`:20`)
- **Asset pipeline:** repeated scatter → CC0 Kenney catalog (`threejs_asset_catalog`); unique hero object → `atlas_3d` `tripo-h3.1/text-to-3d`; concept-image match → `fal_3d` Hunyuan v3.1 Rapid; regional extraction → SAM 3D Objects. (`:11-19`)
- **Mandatory QA:** front/rear/silhouette, holes, ground contact, UV seams, PBR maps, triangle count — *"Do not approve from the provider thumbnail alone."* (`:52-64`)
- **Normalization:** `target_height` declared, bounding box measured, floor offset to terrain. Arbitrary scene-scale guessing **mana** hai. (`:66-70`)
- **World fidelity budget — teen density layers:** macro (terrain silhouette, waterways) + meso (hero buildings, cliffs, canopy) + micro (ground cover, rocks, debris). (`:85-93`)
- **Primitive-only previews** ko `blockout` label karna **zaroori** hai; wo production review pass nahi kar sakte. (`:91`)
- **Render protocol:** pehle bounded frame range render karo, **per-frame time measure karo**, phir resolution chuno — intuition se nahi. Numbered PNG sequence, `resume: true`. (`:98-101`)

**Kya missing hai:** `blender_world`, `atlas_3d`, `fal_3d`, `threejs_asset_catalog` — ye **OpenMontage MCP tools** hain, is repo me sirf unki *documentation* hai, **implementation nahi**. `grep -r "atlas_3d" --include=*.py --include=*.mjs` → **zero results**.

**Isliye (a) Blender install, (b) GPU, (c) ya woh MCP tools chahiye.** Teeno is sandbox me nahi.

---

## 3. Three.js route — 11 skills, magar GL nahi

`skills/openmontage/.agents/skills/` me: `threejs-fundamentals`, `-geometry`, `-materials`, `-lighting`,
`-shaders`, `-postprocessing`, `-textures`, `-animation`, `-loaders`, `-interaction`, `-world-generation`.
Plus `character-rigging`, `character-animation-qa`, `canvas-procedural-animation`, `svg-character-animation`.

Content asli hai (materials skill me PBR/physical/shader material table, `MeshPhysicalMaterial` clearcoat/transmission, `ShaderMaterial` GLSL). Node v22 maujood hai.

**Block:** `ldconfig -p | grep -E "libGL|libEGL|libGLESv2|libOSMesa"` → **kuch nahi**. `/usr/lib/x86_64-linux-gnu/dri` → **khali**.
Yaani headless Chrome/WebGL render possible nahi, aur `three` ko software rasterizer nahi milta.

**Possible workaround (test kiya nahi, kyunki risk zyada):** `pip install moderngl` + `libOSMesa` — magar OSMesa package is Debian image me nahi hai aur `apt` bhi nahi chal sakta (no root).

---

## 4. Numpy route — jo maine banaya, aur uska asli level

`research/viral_og_v21/film3d/`:
- `geo3d.py` — procedural cave (implicit SDF: tube + floor + wobbly bore), bear (9 metaball parts, pose morph standing↔rearing, **walk cycle** with hip rotation + phase, fur clump displacement, eye spheres with specular), skull (*Ursus spelaeus*: long snout, steep forehead, sagittal crest, carved sockets, nasal aperture, occipital hole, 20 teeth), bone piles, rocks, dust particles (gravity/drag/curl noise), flame particles (life cycle + flicker noise).
- `render3d.py` — camera (fov/roll/look-at), ray-marched set with bisection refine + analytic normals + bump from noise gradient, **tube visibility** (light occlusion through the cave), portal + fire lights with inverse-square, GGX specular, Fresnel rim, volumetrics (24-step ray march, Henyey-Greenstein phase, height fog), splat rasteriser with adaptive soft taps + depth test, ACES, bloom, anamorphic streak, CA, vignette, grain, auto-exposure.
- `film1min.py` — 7 shots, 60 s, har shot camera curve + light rig + animation state.

**Measured per-frame time (is machine, 480×270):** ~3.9 s/frame. 1440 frames ≈ **96 minute**.

### Iska ceiling — honest table

| Cheez | Cinema level | Numpy route abhi | Gap |
|---|---|---|---|
| Geometry | milliions of tris, displacement, scans | metaball shells (9k pts/bear) | ❌ bada |
| Fur | 1–5M strands, self-shadow, wind | displaced shell + stray points | ❌ bada |
| Materials | layered PBR + SSS + anisotropy | albedo + GGX approx | ❌ |
| Lighting | path-traced GI, area lights, caustics | single-scatter + ambient approx | ❌ |
| Shadows | ray-traced, soft, contact | **koi shadow map nahi** | ❌ |
| Volumetrics | VDB, multi-scatter, denoise | 24-step single scatter, 1/3 res | ⚠️ |
| Motion blur / DOF | kamera-real | nahi | ❌ |
| AA | 16–64 spp | 1 spp + splat softness | ❌ |
| Resolution | 4K | 480×270 | ❌ |

**Ye ceiling architecture ki hai, speed ki nahi.** 3 ghante render karke bhi fur aur GI nahi aayega.

---

## 5. SFX — ab **asli** repo se

Pehle maine synthesize kiya tha kyunki mujhe laga repo me sirf spec hai. Galat tha:

- `audio/kit.json` — 21 roles, har role ka `sound` id, **measured** `bed_db`, `offset_ms` (cuts par alignment), `min_gap_ms`.
- `tools/sfx_takes.py` — earshot `forge.bank` se wav render karta hai + `onset_s/peak_s/end_s/peak_db/lufs_m_max` meta.
- earshot source (`github.com/Leonxlnx/earshot`) me **252 sounds** hain; repo ke 21 ids sab maujood.
- **Ab render ho chuke:** `audio/takes/` — 16 wav @48k + `meta.json` (measured). `soundfile` + `scipy` install kiye.

Aur file jo pehle miss ho gayi thi: **`audio/cues-23.json`** — ek asli cue sheet (23s, 17 cues, roles + gains).

**Ab cue alignment kit ke apne numbers se hoti hai:** `start = cut + offset_ms/1000 − onset_s`. Yaani tap cut se *pehle* aata hai, whoosh cut ke *baad* land karta hai — jaisa kit me measured hai.

---

## 6. Score — repo ka grammar use hua

`tools/film_score.py` + `tools/music_bed.py` ka pattern follow kiya:
- sections = (start, end, chord, intensity, kick rate, arp pattern, rms target)
- pads **4200 Hz lowpass** (2–5 kHz harshness band se door — `sound-design/SKILL.md` non-negotiable)
- sub mono, `film_score.py` ke `REF_ARC` jaisa slow dynamics contour
- `research/viral_og_v21/film3d/score3d.py` — 7 sections, 60 s.

---

## 7. Kya karna chahiye (priority order)

1. **Blender route unlock** — isse quality 10× jump karti hai (fur, GI, SSS, shadows, 1080p). Chahiye: `blender` binary + `libEGL` ya GPU. Kaggle T4×2 route (`gpu-engine/kaggle/`) me Blender install + Cycles possible hai — **credentials chahiye**.
2. **Agar Blender nahi** — numpy route ko honestly upgrade karo: shadow maps (1 pass/frame), 2×2 AA supersample, motion blur (2 temporal samples), bear ko metaball se **marching-cubes mesh** bana ke sahi normals + fur shells (3 layers). Ye "indie 3D documentary" tak le jaata hai, cinema nahi.
3. **Aur kuch nahi** — jo abhi hai wahi ceiling hai. Main aap ko "Hollywood" nahi bolunga jab architecture allow nahi karta.

---

## 8. Jo aaj deliver hua

| File | Kya |
|---|---|
| `audio/takes/*.wav` + `meta.json` | repo ke 16 SFX, measured meta ke saath |
| `research/viral_og_v21/film3d/sfx_cues.py` | cue sheet kit levels + onset alignment se |
| `research/viral_og_v21/film3d/score3d.py` | 60 s score, repo score grammar |
| `research/viral_og_v21/film3d/build_mix3d.py` | VO + score + SFX + ambience mix, −16 LUFS |
| `research/viral_og_v21/film3d/out/EP01_BEAR_1min_3D_640x360_MASTER.mp4` | 60 s, 1440 3D frames, repo SFX + score muxed |
| `research/viral_og_v21/film3d/sdf.py` | bear / skull / boulder / torch **solid SDFs** (raymarched, not splatted) |
| `research/viral_og_v21/film3d/REPO_3D_FORENSIC.md` | ye audit |

---

## 9. Version 2 — jo 14 Nov ko rebuild hua (aur kyun)

Pehla 60 s render **bekaar** nikla: poora frame blue haze tha. Forensic karne par 6 asli bugs mile:

| # | Bug | Asar | Fix |
|---|---|---|---|
| 1 | `march_set` step 0.42 m × 34 steps = **14 m**, magar tunnel 30 m | deewar kabhi hit nahi hoti, rays mid-air shade hoti hain | sphere tracing + tmax 46 m |
| 2 | **normals ulti** (`N·V = −0.147`) | har surface backfacing, lighting flat | `normal()` = −gradient (sdf>0 = solid) |
| 3 | floor SDF ka **sign inverted** | floor kabhi solid nahi tha | `ff = floor_y − y` |
| 4 | `visibility()` light ko wall ke aar-paar maanta tha, aur skull ke liye **hamesha 0** | warm key light ka koi asar nahi | SDF soft shadow, 10 taps, penumbra |
| 5 | compositing `img + vol*1.5` | haze image ke upar add, transmittance ignore | `img*T + inscatter` |
| 6 | auto-exposure percentile par | ek blown highlight poori frame ko 0.4 stop kar deta | **per-shot fixed exposure** (DOP stop) |

Aur ek architectural badlav: **point-splatting hata diya.** Point cloud surface nahi banti — bear 9 alag ellipsoids jaisa dikhta tha, skull par bubbles. `sdf.py` me poora model smooth-union SDF hai (watertight, continuous normals, SDF AO), aur `march_objects()` usko cave ke saath hi raymarch karta hai. Isse parallax, occlusion, silhouette, sab asli hai.

**Nateeja (honest):** ab ye *indie 3D documentary* level hai — asli geometry, asli lights, asli camera, asli physics clock. Ye **Pixar/Blender cinema level nahi** hai, kyunki fur strands, GI, SSS, motion blur, DOF, 4K — inka koi rasta is machine par maujood nahi (section 4 ka table wahi hai).

## 10. Audio sync — kaise exactly sync hai

`sfx_cues.events()` hand-timed nahi hai:
- cut points seedha `film1min.film()` ke shot durations se aate hain,
- footsteps `BEAR_WALK` ke gait clock se (freq 1.0 Hz, 2 steps per cycle) — wahi clock jo pairon ko hilata hai,
- har cue ka level `audio/kit.json` ke measured `bed_db`, alignment `offset_ms`, gap `min_gap_ms` se.

Is liye agar kal shot ki length badle, **audio khud saath badal jayega** — kuch manually shift nahi karna padega.
