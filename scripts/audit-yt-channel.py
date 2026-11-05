#!/usr/bin/env python3
"""Fetch public channel inventory through the existing API client; no secrets in output."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yt_intel import client, http


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('channel')
    p.add_argument('--out', default='.cache/yt-intel/channel-audit')
    p.add_argument('--transcripts', action='store_true')
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'lane': client.lane(), 'channel_input': args.channel,
              'scope': 'Public API metadata; one page (up to 100) top-level comments per video, not all replies. '
                       'Optional public transcripts. No private Studio metrics or audiovisual viewing implied.'}
    if not client.API_KEY:
        report.update(status='error', detail='YOUTUBE_API_KEY is not available in this runtime')
    else:
        corpus = client.channel(args.channel)
        report['channel'] = corpus.to_dict()
        report['status'] = corpus.status
        report['videos'] = []
        for video in corpus.items:
            row = dict(video)
            row['url'] = 'https://www.youtube.com/watch?v=' + video['id']
            row['comment_sample'] = client.comments(video['id']).to_dict()
            if args.transcripts:
                try:
                    row['transcript'] = client.transcript(video['id'])
                except Exception as e:
                    row['transcript'] = {'status': 'error', 'detail': http.scrub(str(e))}
            report['videos'].append(row)
    # Scrub the entire diagnostic tree too, including errors raised by optional extractors.
    target = out / 'channel.json'
    target.write_text(http.scrub(json.dumps(report, ensure_ascii=False, indent=2)) + '\n')
    print(json.dumps({'status': report['status'], 'videos': len(report.get('videos', [])),
                      'report': str(target)}, indent=2))
    return 0 if report['status'] in ('ok', 'empty') else 1


if __name__ == '__main__':
    raise SystemExit(main())
