# Reference diff

- reference: `analysis/attachment-filename-How-to-Edit-VIRAL-RE/report.json`
- rebuild: `analysis/v4-build/report.json`

| metric | reference | rebuild | delta | verdict |
|---|---|---|---|---|
| width | 720 | 720 | ±0.000 | PASS |
| height | 1280 | 1280 | ±0.000 | PASS |
| fps | 30.0fps | 30.0fps | ±0.000 | PASS |
| duration | 23.35s | 23.4s | ±0.050 | PASS |
| cut_count | 13cuts | 12cuts | ±1.000 | PASS |
| cuts_per_minute | 33.4/min | 30.77/min | ±2.630 | FAIL |
| median_shot | 0.42s | 0.53s | ±0.110 | PASS |
| hook_first_cut | 0.533s | 0.533s | ±0.000 | PASS |
| hook_cuts_3s | 4cuts | 3cuts | ±1.000 | PASS |
| hook_motion_1s | 0.1079abs | 0.1366abs | ±0.029 | PASS |
| motion_mean | 0.0566abs | 0.0703abs | ±0.014 | PASS |
| motion_peak | 1.0abs | 1.0abs | ±0.000 | PASS |
| static_share | 0.924abs | 0.957abs | ±0.033 | PASS |
| saturation | 0.5066abs | 0.5193abs | ±0.013 | PASS |
| luma | 68.17abs | 66.9abs | ±1.270 | PASS |
| dark_share | 0.502abs | 0.445abs | ±0.057 | PASS |
| bright_share | 0.064abs | 0.064abs | ±0.000 | PASS |
| edge_density | 1.6469abs | 2.8195abs | ±1.173 | FAIL |
| palette_distance | — | — | 33.3 rgb | FAIL |
| rms_db | -13.03dB | -12.15dB | ±0.880 | PASS |
| lufs | -14.02LUFS | -14.37LUFS | ±0.350 | PASS |
| true_peak | -0.31dBTP | -0.05dBTP | ±0.260 | PASS |
| lra | 1.7LU | 2.2LU | ±0.500 | PASS |
| cut_alignment | 13 cuts | 12 cuts | recall 11/13, 1 extra, worst offset 333 ms | FAIL |

**20/24 rows pass.**
