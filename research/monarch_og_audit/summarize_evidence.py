"""Recalculate descriptive channel-sample statistics from stored public receipts.

This deliberately does not pool snapshots or turn selected samples into hit
rates. The pre-Oct-23 maturity cutoff does not backdate later-view counters.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import statistics

from fresh_youtube import MATURE_END, format_bucket
from collect_youtube import before_timestamp

ROOT = Path(__file__).resolve().parent
BUCKETS = ('short_candidate_le60s', 'ambiguous_61_to_239s', 'long_proxy_ge4min')


def metric(rows):
    if not rows:
        return {'n': 0, 'median_views': None, 'min_views': None, 'max_views': None,
                'ge_1m_count': 0, 'lowest': None, 'highest': None}
    ordered = sorted(rows, key=lambda r: (r['views'], r['id']))
    pick = lambda r: {k: r.get(k) for k in ('id', 'title', 'published_at', 'duration_seconds', 'views')}
    return {'n': len(rows), 'median_views': statistics.median(r['views'] for r in rows),
            'min_views': ordered[0]['views'], 'max_views': ordered[-1]['views'],
            'ge_1m_count': sum(r['views'] >= 1_000_000 for r in rows),
            'lowest': pick(ordered[0]), 'highest': pick(ordered[-1])}


def summarize(data, name):
    channels = {c['id']: c for c in data['channels']}
    videos = {v['id']: v for v in data['videos']}
    output = []
    for sample in data['channel_samples']:
        groups = {}
        for bucket in BUCKETS:
            ids = sample.get('format_samples', {}).get(bucket, [])
            if len(ids) > 30 or len(ids) != len(set(ids)):
                raise ValueError('Invalid sample size or duplicate IDs for ' + sample['channel_id'])
            rows = []
            for vid in ids:
                v = videos[vid]
                if (vid not in sample.get('ids', []) or v.get('channel_id') != sample['channel_id'] or
                    v.get('views') is None or format_bucket(v.get('duration_seconds')) != bucket or
                    not before_timestamp(v.get('published_at'), MATURE_END)):
                    raise ValueError('A sampled video violates the stated channel, inventory, format or publication cutoff: ' + vid)
                rows.append(v)
            groups[bucket] = metric(rows)
            if bucket == 'long_proxy_ge4min':
                groups['long_ge20min_subset'] = metric([v for v in rows if v['duration_seconds'] >= 1200])
        channel = channels.get(sample['channel_id'], {})
        output.append({'channel_id': sample['channel_id'], 'channel_title': channel.get('title'),
                       'channel_url': channel.get('url'), 'public_subscribers': channel.get('public_subscribers'),
                       'playlist_status': sample['status'], 'playlist_ids_selected': len(sample.get('ids', [])),
                       'playlist_has_more': sample.get('playlist_has_more'), 'groups': groups})
    return {'snapshot': name, 'runner_reported_utc': data['runner_reported_utc'],
            'channel_samples': output}


def main():
    sources = ('youtube_refresh.json', 'reference_channel_snapshot.json',
               'reference_channel_alternate_snapshot.json')
    data = {p: json.loads((ROOT / p).read_text()) for p in sources}
    snapshots = [summarize(data[p], p) for p in sources]
    original = data['youtube_refresh.json']
    retry = json.loads((ROOT / 'search_retry.json').read_text())
    media = json.loads((ROOT / 'visual_media.json').read_text())
    reference_runs = {}
    for p in sources[1:]:
        references = data[p]
        reference_runs[p] = {
            'handle_status': dict(Counter(x['status'] for x in references['handle_resolutions'])),
            'inventory_status': dict(Counter(x['status'] for x in references['channel_samples'])),
        }
    result = {
        'method': 'Descriptive statistics for the recorded, nonrandom and capped samples only; no results are probabilities, causal effects or Studio metrics. Screenshots are not pooled with API data; the overlapping reference runs are separate and must not be added together.',
        'clock_warning': 'Trusted session date 2026-11-05 UTC; runner/API reported 2026-11-13 UTC. All counters are runner-reported snapshots, not verified as-of the trusted date. Publication cutoff does not backdate counters.',
        'mature_before_exclusive': MATURE_END,
        'discovery': {'planned_original_queries': 39,
                      'original_success': sum(q['status'] == 'ok' for q in original['queries']),
                      'original_errors': sum(q['status'] != 'ok' for q in original['queries']),
                      'retry_pending': retry['pending_count'],
                      'retry_attempted': retry['attempted_queries'],
                      'retry_success': sum(q['status'] == 'ok' for q in retry['queries']),
                      'retry_error': sum(q['status'] != 'ok' for q in retry['queries'])},
        'reference_runs': reference_runs,
        'visuals': {'thumbnail_status': dict(Counter(x['status'] for x in media['thumbnails'])),
                    'model_window_status': dict(Counter(x['status'] for x in media['visual_descriptions']))},
        'snapshots': snapshots,
    }
    (ROOT / 'evidence_summary.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print('Summarized', sum(len(x['channel_samples']) for x in snapshots), 'non-pooled channel samples')


if __name__ == '__main__':
    main()
