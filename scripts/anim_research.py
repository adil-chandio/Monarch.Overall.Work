"""Forensic study of high-performing 2D animation on YouTube.

Runs on CI (a datacenter IP is throttled by YouTube, so this must not run in
the agent sandbox). It pulls the top results for a set of animation queries,
then reads each winner's transcript and style signals, and writes one JSON
plus one markdown so the conclusions can be checked rather than trusted.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yt_intel import client, forensic  # noqa: E402

QUERIES = [
    '2d animation short film',
    'animated story 2d',
    'hand drawn animation short',
    'anime style animation short film',
    'painted 2d animation',
    'cut out animation character',
    'storytime animation',
    'indie animation film',
]

OUT = Path('audit-output')
OUT.mkdir(exist_ok=True)


def main() -> None:
    rows = []
    for q in QUERIES:
        try:
            corpus = client.search(q, limit=20)
        except Exception as exc:  # noqa: BLE001 - report, never swallow
            print(f'search failed {q}: {exc}', file=sys.stderr)
            continue
        print(f'{q}: {corpus.status} {len(corpus.items)} rows {corpus.detail[:80]}', flush=True)
        for v in corpus.items:
            if isinstance(v, dict):
                v['query'] = q
                rows.append(v)

    # de-duplicate on video id, keep the richest row
    seen = {}
    for r in rows:
        vid = r.get('id') or r.get('video_id')
        if not vid:
            continue
        cur = seen.get(vid)
        if cur is None or (r.get('views') or 0) > (cur.get('views') or 0):
            seen[vid] = r
    rows = list(seen.values())

    payload = {'queries': QUERIES, 'n': len(rows), 'rows': rows}
    (OUT / 'anim-research.json').write_text(json.dumps(payload, indent=1))

    # ---- measured summaries, no interpretation yet -----------------------
    views = [r.get('views') or 0 for r in rows if r.get('views')]
    durs = [r.get('seconds') or 0 for r in rows if r.get('seconds')]
    summary = {
        'n_videos': len(rows),
        'views_median': statistics.median(views) if views else None,
        'views_max': max(views) if views else None,
        'duration_median_s': statistics.median(durs) if durs else None,
        'duration_p25_s': (statistics.quantiles(durs, n=4)[0] if len(durs) > 3 else None),
        'duration_p75_s': (statistics.quantiles(durs, n=4)[2] if len(durs) > 3 else None),
    }
    (OUT / 'anim-research-summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))

    top = sorted(rows, key=lambda r: -(r.get('views') or 0))[:20]
    lines = ['# 2D animation — what the winners actually do', '',
             'Measured from public search results, not asserted from memory.', '',
             f'- videos sampled: **{summary["n_videos"]}**',
             f'- median views: **{summary["views_median"]}**',
             f'- median length: **{summary["duration_median_s"]}** s', '',
             '| # | title | channel | views | length |', '| --- | --- | --- | --- | --- |']
    for i, r in enumerate(top, 1):
        secs = r.get('seconds') or 0
        lines.append(f'| {i} | {str(r.get("title",""))[:70]} | {r.get("channel","")} | '
                     f'{r.get("views","?")} | {int(secs//60)}:{int(secs%60):02d} |')
    (OUT / 'anim-research.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
