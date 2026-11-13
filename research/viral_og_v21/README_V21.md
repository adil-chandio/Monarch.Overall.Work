# V21 — Viral OG channels (user's own Drive swipe file), real-API forensic

**Read the report first:** `V21_VIRAL_OG_DEEP_FORENSIC_ROMAN_URDU.md` (Roman Urdu, 13 sections).

| File | What it is |
|---|---|
| `V21_VIRAL_OG_DEEP_FORENSIC_ROMAN_URDU.md` | The full report: method, boundaries, 28 verified channels, 178 outliers, 36 lanes, comments, thumbnails, 3-cluster comparison, gaps |
| `EPISODE_01_SCRIPT_V21.md` | Provisional episode: full English narration (~1,610 words / 9:20), measured spec, metadata, thumbnail spec, `[VERIFY]` list |
| `SHOTLIST_EP01_V21.csv` | 44 3D shots, 560 seconds exactly, with camera / build / sound / on-screen text per shot |
| `thumb_ep01_v21.png` | 1280×720 thumbnail built to the measured spec (small character, warm fire accent, red ochre, 3 words) |
| `thumb_ep01_v21_base.png` | Textless base plate for re-crops |
| `build_viral_og_v21.py` | Main pipeline (identity → catalogue → 36 lanes → outliers → thumbs → comments → captions) |
| `discovery_v21.py` | Discovery route that survives CI IP blocks (`youtubei` WEB search + `sp` protobuf filters) |
| `resolve_v21.py` | Cache-first channel resolver |
| `resolve_by_catalogue.py` | Channel identity by catalogue **shape**, not one title |
| `probe_search_routes.py` | Measured test of 5 discovery routes (why `v3/search` was abandoned) |
| `api_evidence/` | 15 JSON + 3 log files — every number in the report comes from here |

## The one engineering fact worth remembering

`youtube/v3/search` returns **HTTP 429** from GitHub-runner IPs (measured 7/7 runs, once after spending only 82 units). `youtubei/v1/search` with a WEB client context answers in the same runner, same minute. So: **discovery from the public web endpoint, every number from official Data API v3.** Each lane record carries its `route` so the boundary is auditable.

## Status

Research complete and reproducible (run `43402548122`, HARD QC green). Niche **not locked**. No upload / monetisation / virality claim. Every historical number in the script is `[VERIFY]` until a primary source is attached.
