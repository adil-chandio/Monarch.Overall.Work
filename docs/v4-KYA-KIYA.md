# v4 — Kya Kiya / Kya Nahi

Reference: REF-01 (`analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4`)
Rebuild: `public/demo/v4.mp4` · 720×1280 · 30 fps · 701 frames · 23.37 s

**Numeric diff: 21 / 24 rows PASS.** Teen row fail hain, aur teeno ke number neeche hain.

---

## Kya Kiya

### 1. Film galat picture bana rahi thi — `s4` kabhi gaya hi nahi

19 second par jo frame aata tha, usme portrait ke peeche **BILLION** ka label, paison ka
fan aur ek **khaki/green field** tha. Ye layers CTA ke hain hi nahi — ye `s4`
(1.00–1.30 s) ka plate `plate-bag-green.png` tha.

Wajah ek line ka arithmetic thi:

```
s4 ka window      1.000 → 1.300 s          (0.300 s)
uska entrance     duration = max(0.43*0.75, 2/30) = 0.3225 s, shuru 1.000
                  matlab khatam 1.3225 s
uska hide         tl.set(s4, {opacity:0}, 1.300)
```

Hide 1.300 par chala, aur uske baad **abhi chalta hua entrance** ne agle tick par
`opacity: 1` wapas likh diya. GSAP aakhri tween ko jeetta hai. Isliye `s4`
**1.33 s se film ke aakhir tak** full opacity par khada raha — 22 second, har scene
ke neeche, aur jahan scene ke andar `backdrop-filter` ya `screen` blend hai wahan
sabse aage.

Isi wajah se CTA `[118,101,70]` khaki tha (reference `[59,26,23]` maroon), aur flash
ke baad **green** ho jata tha — `#s14red` `mix-blend-mode: screen` hai, jo apne neeche
jo hai usse blend karta hai; neeche green money bag tha.

**Fix:** entrance tween apne window se aage nahi ja sakta —
`entDur = min(max(dis*0.75, 2/FPS), max(outT - inT, 1/FPS))`.

### 2. Frame 0 kaala tha — asli wajah alag thi

Pehle lagta tha ki `tl.set(id,{opacity:0},0)` aur show ek hi tick par takra rahe hain.
Wo fix karne ke baad bhi frame 0 kaala tha. Asli wajah: **`t = 0` par zero-duration
set GSAP kabhi apply nahi karta** — timeline 0 par baithi ho to set insert hi nahi
hua hota. `0.0001` par rakhne se bhi kaam nahi chala (peeche seek karne par GSAP
recorded start value wapas likh deta hai).

**Fix:** opening scene ka `opacity:1` markup me likha hai, timeline uske baad control
leti hai. Delivered master par verified: **frame 0 luma 0 → 205**, 701 frames me
**0 black frames**.

### 3. Flash reference se chhota aur tez tha

REF-01 ko frame-by-frame decode kiya (mean luma): `49 49 49 46 46 46 61 61 145 139 139 48 47 49 48 45…`
Matlab flash **teen** frame ka hai — 145, 139, 139 — ek frame 61 par ban raha hai aur
48 se girta hai. Build me do frame the, seedha 217 par (opacity 0.9).

**Fix:** opacity 0.52 → 0.50 → 0.50, ek frame pehle 0.22 par build. Aur composition gate
jo `flash >= 0.9` maang raha tha wo bhi galat tha — wo mere purane flash ka number tha,
reference ka nahi. Ab gate measurement ke around band assert karta hai.

### 4. CTA ka yellow pill galat jagah aur galat waqt par

REF-01 me pill **19.03** par aana shuru hota hai aur 19.9 tak badhta rehta hai
(yellow share 0.8% → 3.1% → 4.5% → 6.0% → 7.5%). Build me 18.72 par poora aa jata tha.
Aur wo **flash wale frame par gayab** ho raha tha — flash ke upar ek doosra poora change
stack karke, jo diff ne "1 extra cut" gina.

**Fix:** 19.03 par slow spring (0.92 s), aur pill 20.750 par clear hota hai — flash ke
baad, glass card me, jaise reference karta hai.

### 5. Do naye gate — taaki ye galti dobara 7-minute render na khaye

- **`tools/timeline_probe.mjs`** — GSAP deterministic hai, isliye timeline ko headless
  sample karta hai (~2 s) aur **scene ke naam aur second ke saath** fail karta hai agar
  koi scene apni window se aage zinda rahe, ya frame 0 unpainted ho. 10 minute me 4
  render jalane ke baad likha. CI me render se **pehle** chalta hai.
- **Workflow ka path filter** sirf `showreel/v4/**` aur `tools/ref_diff.py` dekh raha tha.
  Isliye `1cd1d96` jaise fix commit ho kar **CI me chale hi nahi**. Ab `tools/**` bhi
  trigger karta hai.
- **`tools/grade_sim.py`** — CSS filter chain (brightness/saturate/contrast/hue-rotate)
  numpy me reproduce karta hai, taaki grade reference ke **measured colour** ke against
  chuna jaaye, aankh se nahi.

### 6. Chhote measured fixes

| kya | pehle | ab | reference |
|---|---|---|---|
| plate blur | 3 px | **4 px** | reference ki photography soft hai |
| grain opacity | .014 | **.008** | grain akela ~0.55 edge jodta hai |
| light plate | `#bababa` | **`#bcbbba`** | `[188,187,186]` |
| 2008 plate | `#b81f20` | **`#a81d1b`** | `[113,9,9]` |

---

## Kya Nahi — teen row, poore number ke saath

### FAIL 1 · `edge_density` — reference 1.6469, rebuild 2.9223 (allowed ±0.45)

Hamari picture reference se **zyada sharp** hai. Ye opinion nahi, measurement hai:

- Reference ko **hamari settings par re-encode** kiya (crf 20 / 1600k) → uska edge
  `2.126 → 2.121`. Matlab compression wajah **nahi** hai. Difference content me hai.
- Extra global blur ka price measured: `+0 → 2.83`, `+1 px → 2.27`, **`+2 px → 1.59`**,
  `+3 px → 1.25`.
- **`+2 px` par ye row PASS ho jayegi (1.59, reference 1.65) — lekin 701 frames poori
  film ke blur ho jayenge**, aur zoom par reference ka leather, texture aur type
  khoyega. User ne kaha quality par compromise nahi. Isliye maine ye nahi kiya.

**Asli fix:** per-shot softness. Reference har shot me same sharp nahi hai. Abhi plate
blur ek global 4 px hai; hona chahiye per-scene — portrait shots (s6, s7, s14) soft,
graphic cuts (s4, s15, s13) sharp. Ye composition ka kaam hai, ek constant ka nahi.

### FAIL 2 · `palette_distance` — 38.2 rgb (allowed ≤ 22.0)

Ab exactly pata hai kaunse do colour pair kharab hain:

| reference | hamara | distance | kya galat |
|---|---|---|---|
| `#710909` `[113,9,9]` | `#9c1b17` `[156,27,23]` | 48.7 | red **43 luma zyada bright**, orange ki taraf |
| `#bcbbba` `[188,187,186]` | `#e1e4e3` `[225,228,227]` | 68.8 | white plates **37 luma zyada white, greenish** |

Doosra `t=2.0s` par `#s1` ka plate hai (jahan green reveal hota hai) — wo pure white
hai jahan reference halka grey hai.

**Fix:** `#54c`-type plate ko `[113,9,9]` par le jao (measured solve: `#710909`), aur s1
ka base `#e1e4e3` → `#bcbbba`. Ye measurable hai, ~1 render.

### FAIL 3 · `cut_alignment` — recall 12/13, 1 extra, worst offset 333 ms

- **12/13 sahi** — 12 cuts reference ke timecode par mil rahe hain.
- **Missing:** `13.333` (s13 ka cut) — 333 ms ka offset, jabki hamara 12.967 aur 14.833
  exact hai. Iska matlab s13 ka cut **detector ke liye** visible nahi. s13 par kaam
  chahiye: s12 (grey stool) se s13 (HE SAID NO) ka change type ki wajah se kaafi bada
  hona chahiye.
- **Extra: `20.633`** — ye **flash hi hai**, jo reference me bhi maujood hai. Reference
  ke apne detector ne usay cut nahi gina, kyunki uska flash picture ke ~6% par chalta hai;
  hamara frame-to-frame jump 41 → 57 → 95 karta hai jahan reference 128 → 131 karta hai.
  **Saaf baat:** is row ko 13/13 karne ka ek hi tareeka hai — flash ko hatao (jo reference
  me hai) ya itna halka karo ki detector use na dekhe. Dono galat hain. Isiliye ye row
  jaan-boojh kar fail hai, aur maine ise chhupaya nahi.

---

## Measured: pehle vs ab (delivered master se, 720×1280 par)

| kya | pehle | ab | REF-01 |
|---|---|---|---|
| frame 0 luma | **0.0** | **205.2** | white plate |
| black frames | 15 | **0** | 0 |
| CTA field @18 s | `[118,101,70]` khaki | **`[65,20,17]`** | `[59,26,23]` |
| CTA field @22 s | `[100,135,92]` **green** | **`[30,15,13]`** | `[49,6,7]` |
| `hook_motion_1s` | 0.0568 | **0.1127** | 0.1079 |
| `palette_distance` | 42.5 | **38.2** | — |
| cuts matched | 12/13 | **13/13** | 13 |

`hook_motion_1s` alag se tune **nahi** kiya — zombie `s4` hatne par khud theek hua,
kyunki hook par 15 frame usi ke neeche composite ho rahe the. Jab root cause theek
hota hai, uske numbers khud theek hote hain.

## Ek revert jo maine kiya

Shot 7 ko reference ke colour `[52,29,29]` par grade kiya (build `[22,12,6]` tha) —
solve karke `brightness 1.70`. Result: shot 7 shot 6 jitna bright ho gaya, **9.133 s ka
cut hi nahi raha**, cuts 13 → 12, `cut_alignment` 11/13 with 2600 ms offset. Ek edit ka
node kho kar wo luma point lena jo pehle se pass tha — trade nahi hai. **Revert kiya.**
Sahi fix: us shot ke liye **alag plate**, brighter grade nahi.
