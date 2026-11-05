#!/usr/bin/env python3
"""Bounded, reproducible English-market discovery. Public metrics are not audience/RPM data."""
import datetime as dt
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yt_intel import client, http

SEEDS = ['prehistoric animals', 'extinct animals', 'life million years ago',
         'prehistoric ocean', 'evolution documentary', 'deep sea creatures',
         'ancient earth documentary', 'speculative evolution']
OUT = Path('docs/research/data/extinct-market-2026-11-05.json')


def collect():
    now = dt.datetime.now(dt.timezone.utc)
    report = {'checked_at': now.isoformat(), 'status': 'ok',
              'method': {'seeds': SEEDS, 'searches_per_seed': [
                  {'order': 'viewCount', 'window_days': 90}, {'order': 'date', 'window_days': 30}],
                  'max_results_per_search': 25, 'relevanceLanguage': 'en', 'regionCode': 'US',
                  'limitations': ['Not an exhaustive YouTube crawl or random sample.',
                    'English/US search settings do not establish actual audience country or RPM.',
                    'A single snapshot cannot prove subscriber growth, current view velocity or causality.',
                    'Duration <=180s is a short-length proxy, not confirmed Shorts classification.',
                    'Recent-channel inventories are first 50 playlist entries, not complete archives.',
                    'Comments are top-level samples only; not all replies. No video playback performed.']},
              'queries': [], 'videos': [], 'channels': [], 'channel_samples': [], 'comment_samples': []}
    if not client.API_KEY:
        report.update(status='error', detail='No API key resolved')
        return report
    hits, ids = {}, []
    for seed in SEEDS:
        for order, days in [('viewCount', 90), ('date', 30)]:
            params = {'part': 'snippet', 'q': seed, 'type': 'video', 'maxResults': 25,
                      'order': order, 'relevanceLanguage': 'en', 'regionCode': 'US',
                      'publishedAfter': (now - dt.timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')}
            q = {'query': seed, 'params': params}
            try:
                data = client._api('search', params, 'search')
                q['status'] = 'ok'
                q['video_ids'] = [i['id']['videoId'] for i in data.get('items', []) if i.get('id', {}).get('videoId')]
                q['additional_results_available'] = bool(data.get('nextPageToken'))
                for vid in q['video_ids']:
                    ids.append(vid)
                    hits.setdefault(vid, []).append({'query': seed, 'order': order, 'window_days': days})
            except Exception as e:
                q.update(status='error', detail=http.scrub(str(e)), video_ids=[])
                report['status'] = 'partial'
            report['queries'].append(q)
    ids = list(dict.fromkeys(ids))
    for start in range(0, len(ids), 50):
        try:
            report['videos'].extend(client.videos(ids[start:start + 50]).items)
        except Exception as e:
            report.setdefault('errors', []).append(http.scrub(str(e)))
            report['status'] = 'partial'
    for row in report['videos']:
        row['discovered_by'] = hits[row['id']]
        row['url'] = 'https://www.youtube.com/watch?v=' + row['id']
        try:
            then = dt.datetime.fromisoformat(row['published'].replace('Z', '+00:00'))
            age_hours = (now - then).total_seconds() / 3600
            row['age_hours'] = round(age_hours, 2)
            row['lifetime_average_views_per_day'] = round(row['views'] / (age_hours / 24), 2) if age_hours > 0 and row['views'] is not None else None
        except (ValueError, TypeError, KeyError):
            row['age_hours'] = None
    channel_ids = list(dict.fromkeys(r['channel_id'] for r in report['videos']))
    for start in range(0, len(channel_ids), 50):
        try:
            data = client._api('channels', {'part': 'snippet,statistics,contentDetails', 'id': ','.join(channel_ids[start:start + 50])}, 'channels')
            report['channels'].extend(data.get('items', []))
        except Exception as e:
            report.setdefault('errors', []).append(http.scrub(str(e)))
            report['status'] = 'partial'
    channels = {r['id']: r for r in report['channels']}
    # Small-channel breakout candidates, not confirmed growing channels.
    candidates = []
    for row in report['videos']:
        ch = channels.get(row['channel_id'], {})
        stats = ch.get('statistics', {})
        subs = int(stats.get('subscriberCount', 0))
        if not stats.get('hiddenSubscriberCount', True) and 0 < subs <= 250000 and (row['views'] or 0) >= 10000:
            candidates.append((row['views'] / subs, row))
    selected, seen = [], set()
    for _, row in sorted(candidates, key=lambda x: x[0], reverse=True):
        if row['channel_id'] not in seen:
            selected.append(channels[row['channel_id']])
            seen.add(row['channel_id'])
        if len(selected) >= 8:
            break
    for ch in selected:
        sample = {'channel_id': ch['id'], 'name': ch.get('snippet', {}).get('title'), 'scope': 'first 50 uploads playlist entries'}
        try:
            playlist = ch['contentDetails']['relatedPlaylists']['uploads']
            data = client._api('playlistItems', {'part': 'contentDetails', 'playlistId': playlist, 'maxResults': 50}, 'playlistItems')
            vids = [i['contentDetails']['videoId'] for i in data.get('items', []) if i.get('contentDetails', {}).get('videoId')]
            sample.update(status='ok', truncated=bool(data.get('nextPageToken')), videos=client.videos(vids).items)
        except Exception as e:
            sample.update(status='error', detail=http.scrub(str(e)))
        report['channel_samples'].append(sample)
    # Top videos by sampled public views; inspect relevance manually before making recommendations.
    for row in sorted(report['videos'], key=lambda r: r['views'] or 0, reverse=True)[:10]:
        comments = client.comments(row['id'], limit=50).to_dict()
        report['comment_samples'].append({'video_id': row['id'], 'title': row['title'], 'sample': comments})
    report['coverage'] = {'searches_attempted': len(report['queries']),
                          'searches_ok': sum(q['status'] == 'ok' for q in report['queries']),
                          'unique_search_ids': len(ids), 'videos_resolved': len(report['videos']),
                          'missing_video_ids': sorted(set(ids) - {r['id'] for r in report['videos']}),
                          'channels_resolved': len(report['channels']),
                          'small_channel_samples': len(report['channel_samples']),
                          'comment_video_samples': len(report['comment_samples'])}
    if report['coverage']['missing_video_ids']:
        report['status'] = 'partial'
    report['quota_state'] = {'used_this_runtime_day': client.BUDGET.state['used'], 'remaining': client.BUDGET.remaining}
    return report


if __name__ == '__main__':
    result = collect()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(http.scrub(json.dumps(result, ensure_ascii=False, indent=2)) + '\n')
    print(json.dumps({'status': result['status'], 'coverage': result.get('coverage'), 'path': str(OUT)}, indent=2))
    raise SystemExit(0 if result['status'] == 'ok' else 1)
