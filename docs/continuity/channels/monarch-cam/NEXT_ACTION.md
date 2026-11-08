# Exact next action — Monarch Cam

**Single next action:** push the separate V6 technical package on `arena/2b012328-monarch-overall-work`, watch its CI run, then inspect the built MP4 and `review/qc_summary.json`. Do **not** ask the user to explain the channel, the rejection, or the workflow again.

The active lane is the rejected ranking Short. A separate V6 package is now configured, without modifying V5:

- seven per-title CC0 1.0 Wikimedia Commons originals with `CREDITS.md`, `verify_sources.py` and a generated `social_origin_ledger.json`;
- `selected_windows.json`, `source_video_ledger.json`, `source_windows.json` and `source_audio_audit.json` ledgers;
- corrected centered colorful top hook, fully visible left `1.–7.` black label plates, right platform UI and bottom comment/Subscribe bar;
- `render_ranking_visual_raw_v6.py`, `ranking_short_spec.json`, `layout_manifest.json` and `visual_v6_qc.json`;
- raw per-window native Commons audio only, with nine web audio gates and `technical_qc_raw_v6.py`;
- safe-area and social-origin QC checks;
- `.github/workflows/monarch-cam-short-ranking-raw-v6.yml` and a V6 `.gitignore` exception.

**V6 MP4 and CI run are still pending.** V6 uses per-title verified CC0 Commons originals, not unverified real social-platform reposts. No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, or audience result is claimed. V4/V5 remain rejected; V5 remains untouched.

After the CI run: `checkpoint` → update `CHANNEL_STATE.json` / `STATE.json` with the exact run/MP4 hash → `refresh` → `render` → `validate` → `render --check` → commit/push on `arena/2b012328-monarch-overall-work`. If the run fails, read the workflow diagnostics, fix the V6 lane, and do not present V5 as the answer.

If the lane later changes to the broader channel rebuild, continue `PLAYBOOK.md` from `Too Close: Wildlife in Human Space`, two connected Shorts per long, rights/factual ledgers, old-winner bridge, About/home cleanup and Studio review. Do not restart the November plan from the beginning.
