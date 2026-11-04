# Reference diff

- reference: `analysis/attachment-filename-How-to-Edit-VIRAL-RE/report.json`
- rebuild: `analysis/v4-build/report.json`

| metric | reference | rebuild | delta | verdict |
|---|---|---|---|---|
| width | 720 | 720 | ±0.000 | PASS |
| height | 1280 | 1280 | ±0.000 | PASS |
| fps | 30.0fps | 30.0fps | ±0.000 | PASS |
| duration | 23.35s | 23.4s | ±0.050 | PASS |
| cut_count | 13cuts | 11cuts | ±2.000 | FAIL |
| cuts_per_minute | 33.4/min | 28.21/min | ±5.190 | FAIL |
| median_shot | 0.42s | 1.02s | ±0.600 | FAIL |
| hook_first_cut | 0.533s | 0.533s | ±0.000 | PASS |
| hook_cuts_3s | 4cuts | 2cuts | ±2.000 | FAIL |
| hook_motion_1s | 0.1079abs | 0.0869abs | ±0.021 | PASS |
| motion_mean | 0.0566abs | 0.0655abs | ±0.009 | PASS |
| motion_peak | 1.0abs | 1.0abs | ±0.000 | PASS |
| static_share | 0.924abs | 0.954abs | ±0.030 | PASS |
| saturation | 0.5066abs | 0.5128abs | ±0.006 | PASS |
| luma | 68.17abs | 55.26abs | ±12.910 | FAIL |
| dark_share | 0.502abs | 0.596abs | ±0.094 | PASS |
| bright_share | 0.064abs | 0.052abs | ±0.012 | PASS |
| edge_density | 1.6469abs | 3.2913abs | ±1.644 | FAIL |
| palette_distance | — | — | 30.8 rgb | FAIL |
| rms_db | -13.03dB | -12.15dB | ±0.880 | PASS |
| lufs | -14.02LUFS | -14.37LUFS | ±0.350 | PASS |
| true_peak | -0.31dBTP | -0.1dBTP | ±0.210 | PASS |
| lra | 1.7LU | 2.2LU | ±0.500 | PASS |
| cut_alignment | 13 cuts | 11 cuts | recall 5/13, 6 extra, worst offset 600 ms | FAIL |

**16/24 rows pass.**
