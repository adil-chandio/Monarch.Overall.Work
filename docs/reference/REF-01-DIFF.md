# Reference diff

- reference: `analysis/attachment-filename-How-to-Edit-VIRAL-RE/report.json`
- rebuild: `analysis/v4-build/report.json`

| metric | reference | rebuild | delta | verdict |
|---|---|---|---|---|
| width | 720 | 720 | ±0.000 | PASS |
| height | 1280 | 1280 | ±0.000 | PASS |
| fps | 30.0fps | 30.0fps | ±0.000 | PASS |
| duration | 23.35s | 23.4s | ±0.050 | PASS |
| cut_count | 13cuts | 13cuts | ±0.000 | PASS |
| cuts_per_minute | 33.4/min | 33.33/min | ±0.070 | PASS |
| median_shot | 0.42s | 0.52s | ±0.100 | PASS |
| hook_first_cut | 0.533s | 0.533s | ±0.000 | PASS |
| hook_cuts_3s | 4cuts | 4cuts | ±0.000 | PASS |
| hook_motion_1s | 0.1079abs | 0.0873abs | ±0.021 | PASS |
| motion_mean | 0.0566abs | 0.0588abs | ±0.002 | PASS |
| motion_peak | 1.0abs | 1.0abs | ±0.000 | PASS |
| static_share | 0.924abs | 0.97abs | ±0.046 | PASS |
| saturation | 0.5066abs | 0.4653abs | ±0.041 | PASS |
| luma | 68.17abs | 57.54abs | ±10.630 | PASS |
| dark_share | 0.502abs | 0.58abs | ±0.078 | PASS |
| bright_share | 0.064abs | 0.065abs | ±0.001 | PASS |
| edge_density | 1.6469abs | 3.1308abs | ±1.484 | FAIL |
| palette_distance | — | — | 33.5 rgb | FAIL |
| rms_db | -13.03dB | -12.15dB | ±0.880 | PASS |
| lufs | -14.02LUFS | -14.37LUFS | ±0.350 | PASS |
| true_peak | -0.31dBTP | -0.1dBTP | ±0.210 | PASS |
| lra | 1.7LU | 2.2LU | ±0.500 | PASS |
| cut_alignment | 13 cuts | 13 cuts | recall 8/13, 5 extra, worst offset 300 ms | FAIL |

**21/24 rows pass.**
