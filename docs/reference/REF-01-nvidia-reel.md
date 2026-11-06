# REF-01 · "How to Edit VIRAL REELS Animations in After Effects"

**Verdict: ye screen-recording nahi hai. Ye ek finished, delivery-ready viral reel hai.**
Naam tutorial ka hai, content 23.35 s ka finished short. Har frame composite hai — koi UI chrome,
koi timeline, koi cursor nahi. Isliye ise **reference film** ki tarah treat kiya gaya, tutorial ki tarah nahi.

Measured on the real file (`analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4`,
3,244,599 B, md5 `b09a37ef77ac1438326715b0bdbe2f02`) by `tools/analyse_ref.py`,
`tools/ref_shots.py` and `tools/ref_deep.py`. Sab numbers machine se aaye hain.

---

## 1 · Container (measured)

| | |
|---|---|
| size | 720×1280 — **9:16**, exactly half of a 1440×2560 master |
| fps | 30.0 |
| duration | 23.35 s |
| video | h264 · yuv420p · **980 kb/s** · tv range, bt709, progressive |
| audio | aac · 44100 Hz · stereo · **127 kb/s** |

720p30 @ 980 kb/s — ye deliberately **tiny** master hai. Instagram-grade delivery, quality
screenshot nahi. Yani "premium" yahan texture se nahi, **design aur timing** se aata hai.

---

## 2 · Beat map — 14 shots, 13 cuts (33.4 cuts/min)

| # | in | hold | in-transition | on screen |
|---|---|---|---|---|
| 1 | 0.00 | 0.53 s | — | "TWENTY" — green Anton on white, slow reveal |
| 2 | 0.53 | 0.30 s | hard cut | black plate, "TWENTY" **slams** in from left, "BILLION" snaps in → one word |
| 3 | 0.83 | 0.17 s | dissolve 0.50 s | green macro blur (plastic) |
| 4 | 1.00 | 0.30 s | dissolve 0.43 s | bag on green, "BILLION" tilted, hand-pinned tag |
| 5 | 1.30 | 1.83 s | dissolve 0.27 s | **the match-move**: bag shrinks out of green, lands on a stool in a cloudscape → "HE" "SAID" "NO" slam on top |
| 6 | 3.13 | 6.00 s | hard cut | red NVIDIA plate, logo spin, two hands + $100 note, "2008", Jensen rises in from bottom |
| 7 | 9.13 | 2.57 s | hard cut | same frame **on red eyes**, "subscribe & like" yellow pill |
| 8 | 11.70 | 0.47 s | hard cut | "TWENTY" again — **the loop restarts** |
| 9 | 12.17 | 0.30 s | hard cut | "TWENTY BILLION" slam |
| 10 | 12.47 | 0.20 s | dissolve 0.50 s | green macro blur |
| 11 | 12.67 | 0.30 s | dissolve 0.43 s | BILLION bag |
| 12 | 12.97 | 0.37 s | dissolve 0.50 s | bag on stool, pale |
| 13 | 13.33 | 1.47 s | dissolve 0.37 s | HE SAID NO again (slower this time) |
| 14 | 14.80 | 8.55 s | hard cut | CTA plate → Jensen + yellow pill → **white flash** → glass pill, holds to the end |

**Asli skeleton ye hai:** motif (1–5) → reveal (6–7) → **same motif, double speed** (8–13) → payoff (14).
Yani pehle 3 second me jo dikha diya, wahi 11.7 s pe **sasta repeat** hota hai taake dimaag
"arre ye to dekha hai" kare — phir 14.8 s se 8.55 s ka **sirf CTA** chalega. 36 % film sirf CTA hai.

---

## 3 · Transition grammar (measured, alpha-profile)

- **6 hard cuts** — 0.033 s = exactly 1 frame. Zero ramp.
- **6 dissolves** — 0.27 / 0.37 / 0.43 / 0.50 / 0.50 / 0.50 s. Sab **short**, sab motif ke andar (bag ↔ green macro). Reveal ke cuts kabhi dissolve nahi — wo 1-frame hard cut hain.
- **1 exposure flash** — t = 20.63 s: ek frame me R/G 1.35 → **0.81**, luma 43 → **144**, agle frame me wapas 1.71. Ye transition nahi, **camera flash** hai: 2 frames ka white wash, subject ko "re-graded" karne ke liye.

> Rule jo nikalta hai: **dissolve sirf texture ke andar, hard cut story ke andar.** Kahani modne ke liye kabhi >1 frame nahi diya.

---

## 4 · Type metrics (native px, measured)

| element | width | cap height | colour | note |
|---|---|---|---|---|
| BILLION (green shot) | 461 px = **64.0 %W** | 101 px = **7.9 %H** | ink `#0d1a02` on `#446f02` | Anton-class grotesk, **−7° rotation**, gradient dark→mid |
| HE SAID | 449 px = 62.4 %W | 53 px = **4.1 %H** | `#9d090a` | Anton, tracking tight, no outline |
| NO | 464 px = 64.4 %W | 232 px = **18.1 %H** | `#9d090a` | **4.4× the height of its own kicker** |
| 2008 numerals | ~52 %W at full reveal | 151 px = **11.8 %H** | `#d7d6d8` @ 60 % | optical top at 37.9 %H = Jensen ki aankhon ki line |
| yellow pill | 51.5 %W × 11.2 %H | radius ≈ 0.5 × H | fill `#c3a403`, glyph `#efe7d6` | 2 lines, "subscribe" bold / "& like" light, centred, cy 67 % |
| glass pill | 49.7 %W × **14.1 %H** | radius ≈ 18 %H | fill `#9f9494` @ 22 % + blur(backdrop) + 1 px light edge | cy **85.2 %** — reachable-by-thumb zone |

Type ka poora system **do fonts** pe chalta hai: ek condensed heavy grotesk (Anton-class) + ek
geometric sans (Poppins-class). Bas. Koi script font, koi gold gradient nahi.

---

## 5 · Motion (measured per shot, phase correlation)

- **92 % frames static.** Per-shot drift 0.0–0.56 %W — matlab plates **locked-off** hain.
  Camera jahan chalti hai, wahan **jaan-boojh kar** chalti hai.
- Jo shots hilte hain, wo sirf hook ke 0.17–0.30 s wale: drift **2.2–16.1 %W** per shot = full-frame push.
- `brightness_ramp` per shot: hook shots −129 → +48 (exposure slam), CTA shots −105 → −18 (grade change).
  Yani **motion ka kaam entry/exit hai, hold nahi.**
- 1.83 s ka 5th shot ek hi continuous move hai: bag green se nikal kar stool pe land karta hai
  (scale + position + background swap), **ek bhi cut ke bina** — is film ka sabse mehnga shot.

---

## 6 · Colour (measured)

- Green plate `#446f02`; ink `#0d1a02`. Green **dirty kelly**, neon nahi.
- "HE SAID NO" shot **near-monochrome**: mean saturation **0.06**, luma 130 — sirf 2 red words.
- Red plate base `#a21a1b`, numeral `#d7d6d8` 60 %, NO letter `#9d090a`.
- **Red-eye grade**: normal frame R/G **1.40** → red-eye frame R/G **1.75–1.79**, luma 43 → 41,
  aur switch **3 frames me hard** hota hai (20.57 → 20.73). Ye plugin ka smooth "horror" look nahi,
  ye **toggle** hai — jhatka hi uska point hai.
- Global palette: `#140a0a` 37 %, `#bcbbba` 18 %, `#480605` 14 %, `#710909` 13 %.

---

## 7 · Sound (measured)

- **Koi voice-over nahi.** Spectral flatness **0.019** (p10 0.011 / p90 0.029) = tonal, sustained
  music bed + sound design. VO hota to speech ki formants aur flatness ka pattern dikhta.
- **Har cut se pehle transient**: 33–110 ms **pehle**, 10 me se 9 cuts pe. Yani whoosh cut ke
  andar nahi, cut ke **pehle** land karta hai — ear ko cut se pehle taiyaar karta hai. Ye wo
  detail hai jo amateur miss karta hai.
- Loudest transients −4.7 dBFS @ 17.37 s, −5.7 @ 20.57 (flash ke saath), −6.2 @ 3.10 (Jensen entry).
- Envelope p10/p50/p90 = **−24.6 / −15.2 / −8.8 dBFS** — 16 dB ka dynamic window, yani loudness
  war nahi, **breathing** hai.
- Bass E pe centred (21 votes) = E minor-ish bed.
- **Loudness −14.02 LUFS · TP −0.31 dBTP · LRA 1.7.** Ye exact delivery target hai.

---

## 8 · KYA KIYA (aur kyun chalta hai)

1. **Hook 3 second me 4 cuts** (0.53 / 0.83 / 1.00 / 1.30) — pehla cut 0.533 s pe, aur pehle second
   ka motion 0.1079 (poori film ka 0.0566 — **do guna**). Retention pehle 3 s me kharidi jaati hai.
2. **Motif repeat**, same 5 shots, 11.70 s pe, double speed — familiarity se attention wapas.
3. **8.55 s ka CTA** — film ka 36 %. Subscribe pill dono states me (yellow, phir glass) dikhta hai.
4. **Reveal = grade change, naya shot nahi.** 9.13 s pe shot badla nahi, sirf aankhein laal hui.
   Isliye "same frame, naya matlab" — sasta aur strong.
5. **Type ka scale contrast**: 4.1 %H kicker vs 18.1 %H punch. Ratio 4.4×. Ye ek hi cheez hai
   jo thumbnail me bhi padhi jaati hai.
6. **Sound cut se pehle** (33–110 ms) — cut "feel" hota hai, "dekha" nahi jaata.
7. **Locked plates + 2 pushed shots** — motion ko value milti hai kyunki baaki kuch nahi hilta.

## 9 · KYA NAHI (aur kyun nahi)

1. **VO nahi** — kyunki 23 s me 6 beats hain; VO 6 lines ko 3.9 s average deta hai, aur tab
   type ko bhi padhna padta. Iska kaam rhythm hai, narration nahi. **Hamare v3 me VO hai** — ye
   structural difference hai, aur v4 me ise jaan-boojh kar chunna hoga.
2. **Captions / karaoke nahi** — text hi caption hai. Alag subtitle lane banani hi nahi.
3. **Koi transition > 0.5 s nahi** — kyunki 0.5 s se lamba dissolve "sloppy" padhta hai at this pacing.
4. **Koi beat-grid nahi** — hamare rig ne 70 BPM @ score 0.076 pe "no stable grid" kaha. Cuts music
   ke grid pe nahi, **SFX ke transients** pe hain. Isliye pehle SFX place karo, phir picture cut karo.
5. **Koi handheld / drift nahi** — 92 % static. "Cinematic shake" is format me zeher hai.
6. **Koi 3D camera move nahi**, koi parallax layer nahi — sab 2D plates + scale.
7. **Koi end-card text wall nahi** — sirf pill, sirf do lafz.
8. **Koi logo animation nahi siwaye NVIDIA ke** — brand mark asli footage ka hissa hai, extra nahi.
9. **Koi 1080p/4K master nahi** — 980 kb/s. Yani noise/grain se "premium" nahi aata.

**Sabse bada "nahi":** is film me **koi cheez ek saath do kaam nahi kar rahi**. Hold me kuch
nahi hota. Cut pe sab kuch hota hai. Hamare v3 me kabhi-kabhi teen cheezein saath chalti hain —
wahi "busy" feeling deta hai. Ye reference uske ulta hai: **spikes, not streams.**

---

## 10 · Rebuild plan (v4) — exact map

Har number neeche reference ka measured value hai, na ki "inspiration".

| ref | rebuild | measured target |
|---|---|---|
| 720×1280 · 30 fps · 23.35 s | same canvas | 9:16, 30 fps, **23.35 s ± 0.05** |
| 14 shots / 13 cuts | same count | 13 cuts, 33.4 / min |
| cut list 0.533 / 0.833 / 1.000 / 1.300 / 3.133 / 9.133 / 11.700 / 12.167 / 12.467 / 12.967 / 13.333 / 14.800 (+0.033 x) | **frame-exact same timecodes** | ±33 ms |
| dissolves 0.27–0.50 s | same 6 spans | ±40 ms |
| flash @ 20.63 (2 frames, luma 144) | same | 2 frames |
| red-eye toggle | grade layer on the hero plate | R/G 1.40 → 1.75, 3 frames |
| type 4.1 % / 18.1 % cap heights | same ratio | ±2 % |
| pill 51.5 %W at cy 67 %, glass 49.7 %W at cy 85.2 % | same | ±2 % |
| −14.02 LUFS · TP −0.31 · LRA 1.7 | same master | ±0.5 LUFS |
| SFX 33–110 ms **before** each cut | same | 9/10 cuts |
| 92 % static frames, drift ≤0.56 %W | locked plates | ±10 % |

**Proof protocol:** rebuild render pe wahi rig chalao —
`analyse_ref.py` + `ref_shots.py` + `ref_deep.py` — aur upar ki har row ka **numeric diff** dikhao.
"Same lag raha hai" nahi chalega; table chalega.

---

## 11 · Jo decide karna hai (mera guess nahi chahiye)

Reference ek doosre creator ka **brand content** hai (NVIDIA / Jensen Huang story). Hum uske
**format, timing, typography aur sound grammar** ko exactly clone kar sakte hain — uske
**footage, chehra aur brand** ko nahi (wo kisi aur ka hai, aur clone karna bhi galat hoga).

To teen faisle chahiye (aage sawal poochh raha hoon):

1. **Kahani** — hamara apna topic (YouTube automation) isi 23 s skeleton pe, ya bilkul naya topic?
2. **Hero plate** — photoreal generated portrait / object plates banayein (premium), ya pure
   CSS/SVG-object plates (safe, brand-clean)? Reference ka asli weight photoreal plates se aata hai.
3. **VO** — is format me VO nahi hoti (measured). Hamare v3 me VO hai. v4 VO ke saath, ya
   reference ki tarah music+SFX only?
