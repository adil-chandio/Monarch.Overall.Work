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
| hook_motion_1s | 0.1079abs | 0.1371abs | ±0.029 | PASS |
| motion_mean | 0.0566abs | 0.0724abs | ±0.016 | PASS |
| motion_peak | 1.0abs | 1.0abs | ±0.000 | PASS |
| static_share | 0.924abs | 0.959abs | ±0.035 | PASS |
| saturation | 0.5066abs | 0.5029abs | ±0.004 | PASS |
| luma | 68.17abs | 66.5abs | ±1.670 | PASS |
| dark_share | 0.502abs | 0.444abs | ±0.058 | PASS |
| bright_share | 0.064abs | 0.069abs | ±0.005 | PASS |
| edge_density | 1.6469abs | 2.8542abs | ±1.207 | FAIL |
| palette_distance | — | — | 28.9 rgb | FAIL |
| rms_db | -13.03dB | -12.15dB | ±0.880 | PASS |
| lufs | -14.02LUFS | -14.37LUFS | ±0.350 | PASS |
| true_peak | -0.31dBTP | -0.05dBTP | ±0.260 | PASS |
| lra | 1.7LU | 2.2LU | ±0.500 | PASS |
| cut_alignment | 13 cuts | 12 cuts | recall 11/13, 1 extra, worst offset 333 ms | FAIL |

**20/24 rows pass.**
