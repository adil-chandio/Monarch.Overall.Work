"""Bounded public-channel follow-up for the supplied reference screenshots.

Only public handles/IDs are sent to YouTube, never images, private filenames,
comments or analytics. A handle is inventoried only if its returned channel
name matches the screenshot. Even then, independently check selected video
titles before treating an externally guessed handle as the same channel.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'monarch_viral_audit'))
from collect_youtube import API, before_timestamp, compact_channel, compact_video
from fresh_youtube import PUBLICATION_END, TRUSTED_END, MATURE_END, focus_samples

ROOT = Path(__file__).resolve().parent


class BoundedAPI(API):
    """Pace requests, retry a rate limit once, and stop after repeated limits."""

    def __init__(self, key, sleep=time.sleep):
        super().__init__(key)
        self.sleep = sleep
        self.limit_streak = 0
        self.circuit_open = False

    def get(self, resource, **params):
        if self.circuit_open:
            self.calls.append({'resource': resource, 'http_status': None, 'reason': 'backoff_circuit_open'})
            return None
        self.sleep(0.25)
        result = super().get(resource, **params)
        if result is None and self.calls[-1].get('reason') == 'rateLimitExceeded':
            self.sleep(5)
            result = super().get(resource, **params)
        reason = self.calls[-1].get('reason') if result is None else None
        self.limit_streak = self.limit_streak + 1 if reason == 'rateLimitExceeded' else 0
        if self.limit_streak >= 5 or reason in ('quotaExceeded', 'dailyLimitExceeded'):
            self.circuit_open = True
        return result


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('Expected a JSON object.')
    targets = config.get('ids', {})
    handles = config.get('handles', [])
    if not isinstance(targets, dict) or any(
        not isinstance(k, str) or not k.startswith('UC') or len(k) != 24 or not isinstance(v, str)
        for k, v in targets.items()
    ):
        raise ValueError('Expected public channel IDs and purpose labels.')
    if not isinstance(handles, list) or len(handles) > 50:
        raise ValueError('Expected at most 50 public handles.')
    seen = set()
    for item in handles:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k] for k in ('handle', 'expected_title', 'purpose')):
            raise ValueError('Every handle requires a name, screenshot title and purpose.')
        handle = item['handle']
        if not handle.startswith('@') or len(handle) < 2 or handle.casefold() in seen:
            raise ValueError('Handles must be unique and start with @.')
        seen.add(handle.casefold())
    return dict(targets), handles


def normalize_title(title):
    return ' '.join((title or '').split()).casefold()


def resolve_handles(api, handles, targets):
    targets = dict(targets)
    resolved = []
    for item in handles:
        reply = api.get('channels', part='snippet,contentDetails,statistics', forHandle=item['handle'], maxResults=1)
        found = (reply or {}).get('items', [])
        channel = found[0] if found else None
        name = (channel or {}).get('snippet', {}).get('title')
        if reply is None:
            status = 'request_error'
        elif not channel:
            status = 'not_found'
        elif normalize_title(name) != normalize_title(item['expected_title']):
            status = 'title_mismatch'
        else:
            status = 'resolved_name_match'
            targets[channel['id']] = item['purpose']
        row = {
            'handle': item['handle'], 'expected_title': item['expected_title'],
            'returned_title': name, 'purpose': item['purpose'],
            'screenshot_indices': item.get('screenshots', []), 'status': status,
            'channel_id': channel.get('id') if channel else None,
            'api_reason': api.calls[-1].get('reason'),
        }
        resolved.append(row)
        print('reference handle', item['handle'], status, flush=True)
    return targets, resolved


def collect(api, targets):
    raw = api.batch('channels', targets, 'snippet,contentDetails,statistics')
    channels = {r['id']: compact_channel(r) for r in raw}
    samples = []
    ids = set()
    for cid, purpose in targets.items():
        channel = channels.get(cid)
        playlist = channel.get('uploads_playlist') if channel else None
        row = {'channel_id': cid, 'purpose': purpose, 'status': 'ok', 'pages': 0, 'ids': [], 'scanned_ids': 0}
        if not playlist:
            row['status'] = 'missing_channel_or_playlist'
            samples.append(row)
            continue
        token = None
        while row['pages'] < 4:
            params = {'part': 'snippet,contentDetails', 'playlistId': playlist, 'maxResults': 50}
            if token:
                params['pageToken'] = token
            response = api.get('playlistItems', **params)
            row['pages'] += 1
            if response is None:
                row['status'] = 'playlist_error'
                row['reason'] = api.calls[-1].get('reason')
                break
            for item in response.get('items', []):
                row['scanned_ids'] += 1
                details = item.get('contentDetails', {})
                vid = details.get('videoId')
                if vid and before_timestamp(details.get('videoPublishedAt'), PUBLICATION_END) and vid not in row['ids']:
                    row['ids'].append(vid)
            token = response.get('nextPageToken')
            if not token or len(row['ids']) >= 150:
                break
        row['playlist_has_more'] = bool(token)
        ids.update(row['ids'])
        samples.append(row)
        print('reference inventory', cid, row['status'], len(row['ids']), flush=True)
    raw_v = api.batch('videos', ids, 'snippet,contentDetails,statistics')
    videos = {}
    for item in raw_v:
        if before_timestamp(item.get('snippet', {}).get('publishedAt'), PUBLICATION_END):
            video = compact_video(item)
            videos[video['id']] = video
    for sample in samples:
        sample['format_samples'] = focus_samples(sample['ids'], videos)
    return {
        'schema': 1,
        'method': 'YouTube Data API: selected public reference handles and channel IDs. Up to four newest upload-playlist pages, stopping at 150 eligible IDs; up to 30 most-recent pre-maturity-cutoff observations per duration group. Nonrandom, not a census. No Studio metrics or video/audio playback.',
        'publication_end_exclusive': PUBLICATION_END,
        'trusted_session_end_exclusive': TRUSTED_END,
        'mature_end_exclusive': MATURE_END,
        'runner_reported_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'server_dates_distinct': sorted(set(api.server_dates)),
        'date_warning': 'Runner/API times differ from trusted 2026-11-05 session date; live counts and later reported publications are not verified as of the trusted date.',
        'channels': list(channels.values()), 'channel_samples': samples,
        'videos': list(videos.values()), 'api_call_receipts': api.calls,
    }


def main():
    key = os.getenv('YOUTUBE_API_KEY')
    if not key:
        raise SystemExit('No YouTube API key; no requests made.')
    config = json.loads((ROOT / 'reference_channels.json').read_text())
    targets, handles = validate_config(config)
    api = BoundedAPI(key)
    targets, resolved = resolve_handles(api, handles, targets)
    data = collect(api, targets)
    data['handle_resolutions'] = resolved
    output = Path(os.environ['RUNNER_TEMP']) / 'og-reference-channels.json'
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print('RESULT', len(data['channel_samples']), 'channel samples', len(data['videos']), 'video records', flush=True)


if __name__ == '__main__':
    main()
