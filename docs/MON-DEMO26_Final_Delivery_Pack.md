# MONARCH® STUDIO — Official Final Delivery Pack (`MON-DEMO26`)

**Project Title:** `THREE SECONDS.` — Flagship AI Brand Commercial & Vault Pack  
**Client / Showcase Partner:** Vanguard Studio Labs (`MON-DEMO26`)  
**Founder & Executive Creative Director:** Adil Chandio (`workadilchandio@gmail.com`)  
**Delivery Date:** November 2, 2026  

---

> **Current cut:** the 60 fps "Absolute Cinema" showreel supersedes this pack's
> showreel numbers. See [`MON-DEMO26_v4_Showreel_Delivery.md`](./MON-DEMO26_v4_Showreel_Delivery.md)
> for the v4 master (−14.0 LUFS / −4.0 dBTP, 10.7 dB sectional dynamics) and its
> measured audio-QC table. The B2B commercial described below is unchanged.

## 1. Unlocked Master Assets & Cloud Delivery Links

- **Primary Clean Broadcast Master (`1920x1080`, `30fps`, `42.633s`, Unwatermarked):**  
  https://drive.google.com/uc?id=1U4ktuy-yq7ddgHXjaVPs0eMQnRcdMoG2&export=download
- **Cloud Delivery Vault Folder (`MONARCH_B2B_DELIVERY`):**  
  https://drive.google.com/drive/folders/1ULb_LwBLOHM9GdvPXf6KXsp0Do9n0Zr1
- **Live Storefront & Watermarked Client Vault (`MON-DEMO26`):**  
  https://monarch-workspace-beryl.vercel.app/?portal=MON-DEMO26

---

## 2. Production Architecture & Provenance (`RENDER_LAWS` + `WF-05` + `Vane-Motion`)

1. **Real Dual-T4 GPU AI Video Generation (`8/8` Scenes):**
   - Rendered on Kaggle Dual-T4 GPUs (`Lightricks/LTX-Video`, `768x448`, `49` real temporal frames per scene, Run `41474620591`) conditioned on bespoke 16:9 dark-luxury cinema keyframes (`gpu-engine/keyframes/s01.png` – `s08.png`).
   - Visually audited start/middle/end frames on every scene (`RENDER_LAWS.md` Law #01) before compositing.
2. **7-Layer 2.5D Parallax & 3D Perspective HUD Compositor (`gpu-engine/compose_b2b_flagship.py`):**
   - Optical-flow `minterpolate` temporal smoothing + Lanczos `1920x1080` upscale + cinema micro-contrast unsharp pass.
   - Multi-plane depth separation, giant `Anton` background bleed parallax typography (`03 SEC`, `AUTHORITY`, `WEB 3D`, `14 LUFS`, `VAULT`, `INSPECT`, `GLOBAL`, `MONARCH`), drifting crimson volumetric atmosphere, and `WF-05` §3 3D perspective-extruded glass HUD telemetry cards (zero cheap bottom subtitle pills).
   - Directional whip-pan, depth-push, and feathered transitions (`max_dluma_2frame = 3.39 < 8.0` — zero white strobes).
3. **Studio Voiceover & 76-Style Procedural Foley Master (`gpu-engine/audio/master_mix.m4a`):**
   - Studio narrator voiceover (`94.3%` voice share, `0.16s` first word) + NumPy procedural foley (shattering glass transient, sub-bass authority drop, mechanical lens rack, titanium vault lock click, crystalline settlement chime, and crimson finale braam).
   - EBU R128 broadcast loudness master: **`-14.31 LUFS` integrated**, **`-1.61 dBTP` true peak**, `48 kHz` `192 kbps` stereo AAC.

---

## 3. 8-Scene Commercial Timeline

| Scene | Timecode | Display Bleed | Headline | Foley Signature | Motion Delta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `s01` | `00.00s – 04.93s` | `03 SEC` | **THREE SECONDS.** | `shatter` | `20.29` |
| `s02` | `04.93s – 08.60s` | `AUTHORITY` | **TEMPLATES LEAK TRUST.** | `sub_hit` | `8.73` |
| `s03` | `08.60s – 14.87s` | `WEB 3D` | **DARK-LUXURY 3D WEBSITES.** | `whoosh_deep` | `8.42` |
| `s04` | `14.87s – 21.27s` | `14 LUFS` | **FRAME-ACCURATE FILMS.** | `lens_rack` | `7.32` |
| `s05` | `21.27s – 24.17s` | `VAULT` | **ZERO GUESSWORK.** | `vault_lock` | `14.43` |
| `s06` | `24.17s – 29.90s` | `INSPECT` | **INSPECT INSIDE VAULT FIRST.** | `whoosh_deep` | `9.71` |
| `s07` | `29.90s – 37.53s` | `GLOBAL` | **SETTLE & UNLOCK IN ONE TAP.** | `chime_unlock` | `6.21` |
| `s08` | `37.53s – 42.63s` | `MONARCH` | **MONARCH® STUDIO** | `finale_braam` | `6.32` |

---

## 4. Commercial Usage License

Upon milestone verification inside the MONARCH® Client Vault, the client receives a **Worldwide, Perpetual, Royalty-Free Commercial Usage License** across web, paid social, broadcast digital, and founder presentations.
