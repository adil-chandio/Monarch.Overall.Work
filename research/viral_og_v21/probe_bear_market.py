"""Measure the cave-bear / ancient-human+bear market before writing the episode."""
import json, sys, statistics as st
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "viral_og_v21"))
import discovery_v21 as disc

QUERIES = [
    "cave bear ancient humans",
    "why ancient humans feared cave bears",
    "cave bear explained animation",
    "prehistoric animals humans feared",
    "bear attacks survival animation",
    "every bear species explained",
]
out = {}
for q in QUERIES:
    try:
        rows = disc.inner_search(q, max_pages=1)
    except Exception as e:  # noqa: BLE001
        print(f"### {q}  -> ERROR {repr(e)[:80]}", flush=True)
        continue
    print(f"\n### {q}  ({len(rows)} rows)", flush=True)
    keep = []
    for r in rows[:10]:
        secs = r.get("duration_seconds_hint") or 0
        print(f"  {r.get('view_text',''):>10s} {secs:>5}s {(r.get('channel_title') or '')[:24]:24s} {r['title'][:64]}", flush=True)
        keep.append({"views_text": r.get("view_text"), "duration": secs,
                     "channel": r.get("channel_title"), "title": r.get("title"), "id": r["id"]})
    out[q] = keep
Path("research/viral_og_v21/api_evidence/bear_market_probe.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print("\nwrote bear_market_probe.json")
