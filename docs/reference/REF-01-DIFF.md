# Reference diff

- reference: `analysis/attachment-filename-How-to-Edit-VIRAL-RE/report.json`
- rebuild: `analysis/v4-build/report.json`

| metric | reference | rebuild | delta | verdict |
|---|---|---|---|---|
| width | 720 | 720 | ±0.000 | PASS |
| height | 1280 | 1280 | ±0.000 | PASS |
| fps | 30.0fps | 30.0fps | ±0.000 | PASS |
| duration | 23.35s | 23.4s | ±0.050 | PASS |
| cut_count | 13cuts | 10cuts | ±3.000 | FAIL |
| cuts_per_minute | 33.4/min | 25.64/min | ±7.760 | FAIL |
| median_shot | 0.42s | 0.57s | ±0.150 | PASS |
| hook_first_cut | 0.533s | 0.533s | ±0.000 | PASS |
| hook_cuts_3s | 4cuts | 2cuts | ±2.000 | FAIL |
| hook_motion_1s | 0.1079abs | 0.0843abs | ±0.024 | PASS |
| motion_mean | 0.0566abs | 0.0512abs | ±0.005 | PASS |
| motion_peak | 1.0abs | 1.0abs | ±0.000 | PASS |
| static_share | 0.924abs | 0.957abs | ±0.033 | PASS |
| saturation | 0.5066abs | 0.5002abs | ±0.006 | PASS |
| luma | 68.17abs | 47.9abs | ±20.270 | FAIL |
| dark_share | 0.502abs | 0.651abs | ±0.149 | FAIL |
| bright_share | 0.064abs | 0.079abs | ±0.015 | PASS |
| edge_density | 1.6469abs | 2.5343abs | ±0.887 | FAIL |
| palette_distance | — | — | 29.6 rgb | FAIL |
| rms_db | -13.03dB | -12.15dB | ±0.880 | PASS |
| lufs | -14.02LUFS | -14.37LUFS | ±0.350 | PASS |
| true_peak | -0.31dBTP | -0.1dBTP | ±0.210 | PASS |
| lra | 1.7LU | 2.2LU | ±0.500 | PASS |
| cut_alignment | 13 cuts | 10 cuts | 2/10 within 1 frame (worst 10433 ms) | FAIL |

**16/24 rows pass.**
