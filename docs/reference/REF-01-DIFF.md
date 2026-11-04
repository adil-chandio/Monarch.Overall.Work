# Reference diff

- reference: `analysis/attachment-filename-How-to-Edit-VIRAL-RE/report.json`
- rebuild: `analysis/v4-build/report.json`

| metric | reference | rebuild | delta | verdict |
|---|---|---|---|---|
| width | 720 | 720 | ±0.000 | PASS |
| height | 1280 | 1280 | ±0.000 | PASS |
| fps | 30.0fps | 30.0fps | ±0.000 | PASS |
| duration | 23.35s | 23.4s | ±0.050 | PASS |
| cut_count | 13cuts | 7cuts | ±6.000 | FAIL |
| cuts_per_minute | 33.4/min | 17.95/min | ±15.450 | FAIL |
| median_shot | 0.42s | 2.04s | ±1.620 | FAIL |
| hook_first_cut | 0.533s | 0.533s | ±0.000 | PASS |
| hook_cuts_3s | 4cuts | 1cuts | ±3.000 | FAIL |
| hook_motion_1s | 0.1079abs | 0.073abs | ±0.035 | FAIL |
| motion_mean | 0.0566abs | 0.0456abs | ±0.011 | PASS |
| motion_peak | 1.0abs | 1.0abs | ±0.000 | PASS |
| static_share | 0.924abs | 0.971abs | ±0.047 | PASS |
| saturation | 0.5066abs | 0.5093abs | ±0.003 | PASS |
| luma | 68.17abs | 46.37abs | ±21.800 | FAIL |
| dark_share | 0.502abs | 0.663abs | ±0.161 | FAIL |
| bright_share | 0.064abs | 0.073abs | ±0.009 | PASS |
| edge_density | 1.6469abs | 2.3744abs | ±0.728 | FAIL |
| palette_distance | — | — | 37.0 rgb | FAIL |
| rms_db | -13.03dB | -12.15dB | ±0.880 | PASS |
| lufs | -14.02LUFS | -14.37LUFS | ±0.350 | PASS |
| true_peak | -0.31dBTP | -0.1dBTP | ±0.210 | PASS |
| lra | 1.7LU | 2.2LU | ±0.500 | PASS |
| cut_alignment | 13 cuts | 7 cuts | 1/7 within 1 frame (worst 10933 ms) | FAIL |

**14/24 rows pass.**
