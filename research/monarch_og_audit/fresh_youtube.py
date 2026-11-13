"""Fresh, reproducible, public YouTube API sample for Shorts and long videos.

Search results are discovery samples, not a platform census. No keys, comments,
private analytics, downloaded videos or individual viewer data are written.
The >=4-minute group is a long-video proxy; the <=60-second group contains
Shorts candidates, not API-confirmed Shorts. The older report and its cutoff
are deliberately left untouched.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'monarch_viral_audit'))
from collect_youtube import API, before_timestamp, compact_channel, compact_video

# The trusted session UTC date is Nov 5. The runtime reports Nov 13. The
# refreshed dataset uses an explicitly later, runner-reported cutoff to avoid
# silently repeating the old pre-Nov-6 discovery sample, while recording the
# discrepancy. It does NOT prove which post-Nov-5 records existed as of the
# trusted date. Mature comparisons are anchored before the trusted cutoff.
TRUSTED_END = '2026-11-06T00:00:00Z'
PUBLICATION_END = '2026-11-14T00:00:00Z'
MATURE_END = '2026-10-23T00:00:00Z'
YEAR_START = '2025-11-05T00:00:00Z'
RECENT_START = '2026-08-07T00:00:00Z'

# Non-random keyword discovery; neither English nor US describes the audience.
LANES = [
    ('engineering', 'how it works 3d animation', '3d engineering animated documentary'),
    ('science', 'science explained 3d animation', 'science animation explained documentary'),
    ('geography', 'geography map animation explained', 'geography map animation documentary'),
    ('history', 'history animation explained', 'history animated documentary'),
    ('animated_story', 'animated story unexpected ending', 'animated short film story documentary'),
    ('stickman', 'stickman animation story', 'stickman animation story explained'),
    ('football', 'football 3d animation pov', 'football story animated documentary'),
    ('wildlife', 'wildlife camera animal story explained', 'wildlife animal survival documentary'),
    ('mystery', 'mystery explained animation', 'mystery explained animation documentary'),
]
# Public IDs previously resolved in repository research; supplemented from the
# user's archive where public identifiers can be confirmed.
BASE_CHANNELS = {
    'UCW8ZE5m7AjINN9EzpxNYGCA': 'user channel: MONARCHs Edit',
    'UCfYdmsLO4Q8_IHklTyYieLg': 'user channel: Monarch Cam, separate',
    'UCdcJDQafWwwCyDiaYcehm0w': 'football POV benchmark',
    'UCqLSt_CKF-D6UQF8Npu94ZA': 'football animation benchmark',
    'UCucoJ5yVEEQlUnGHfiQIPQA': 'small animated stories benchmark',
    'UCLgzNX8OGekeI53OOBI2R9g': 'small visual explainer benchmark',
    'UC0Badcq36RBDHN-e3N1Papg': 'large football parody benchmark',
    'UC77PEgjHoZkdfpxcR3_k89Q': '3D explainers benchmark',
    'UCPKVNqfbunZCkbvjBgf6CdA': 'geography benchmark',
    'UC4y2-bKOsnbO36ZPbQnHIBg': 'maps benchmark',
    'UCUWG17RpxXBZ4avKIqPX6CQ': 'animated films benchmark',
    'UChFs0d8syPIK6x8q4C6BrJw': 'established animation benchmark',
    'UC510QYlOlKNyhy_zdQxnGYw': 'animated history long-form benchmark',
}


def format_bucket(seconds):
    if seconds is None or seconds <= 0:
        return 'unknown'
    if seconds <= 60:
        return 'short_candidate_le60s'
    if seconds < 240:
        return 'ambiguous_61_to_239s'
    return 'long_proxy_ge4min'


def within_window(published, start, end):
    if not before_timestamp(published, end):
        return False
    try:
        value = dt.datetime.fromisoformat(published.replace('Z', '+00:00'))
        lower = dt.datetime.fromisoformat(start.replace('Z', '+00:00'))
        return value.tzinfo is not None and value >= lower
    except (AttributeError, TypeError, ValueError):
        return False


def focus_samples(uploads, videos, cutoff=MATURE_END, cap=30):
    """Most recent eligible videos in each bucket; never manufacture a median.

    Uploads must already be playlist-ordered by publication date. Mature means
    published before the cutoff, not evidence of a particular reach plateau.
    """
    result = {'short_candidate_le60s': [], 'long_proxy_ge4min': [], 'ambiguous_61_to_239s': []}
    for vid in uploads:
        row = videos.get(vid)
        if not row or row.get('views') is None or not before_timestamp(row.get('published_at'), cutoff):
            continue
        bucket = format_bucket(row.get('duration_seconds'))
        if bucket in result and len(result[bucket]) < cap:
            result[bucket].append(vid)
    return result


def search_plan():
    out=[]
    for lane, short_query, long_query in LANES:
        for bucket, query, duration in [('short_candidate_le60s', short_query, 'short'),
                                        ('long_proxy_ge4min', long_query, 'medium')]:
            for order in ('viewCount', 'date'):
                out.append({'lane':lane, 'bucket':bucket, 'query':query, 'order':order,
                            'duration_filter':duration,
                            'published_after':RECENT_START if order == 'date' else YEAR_START,
                            'published_before':PUBLICATION_END})
    for lane, query in [('science_long20', 'science animated documentary'),
                        ('history_long20', 'history animated documentary'),
                        ('wildlife_long20', 'wildlife animal survival documentary')]:
        out.append({'lane':lane,'bucket':'long_proxy_ge4min','query':query,'order':'viewCount',
                    'duration_filter':'long','published_after':YEAR_START,'published_before':PUBLICATION_END})
    return out


def collect(key, extra_channels):
    api=API(key)
    queries=[];all_ids=set()
    for plan in search_plan():
        obj=api.get('search',part='snippet',type='video',q=plan['query'],regionCode='US',
                    relevanceLanguage='en',safeSearch='moderate',order=plan['order'],
                    videoDuration=plan['duration_filter'],publishedAfter=plan['published_after'],
                    publishedBefore=plan['published_before'],maxResults=40)
        ids=[x.get('id',{}).get('videoId') for x in (obj or {}).get('items',[])]
        ids=[i for i in ids if i];all_ids.update(ids)
        last=api.calls[-1]
        queries.append(dict(plan,status='ok' if obj is not None else 'error',
                            http_status=last['http_status'],reason=last['reason'],video_ids=ids))
        print('search',plan['lane'],plan['bucket'],plan['order'],last['http_status'],len(ids),flush=True)
        if obj is None and last.get('reason') in ('quotaExceeded','dailyLimitExceeded'):
            break
    raw=api.batch('videos',all_ids,'snippet,contentDetails,statistics')
    rows=[compact_video(v) for v in raw if before_timestamp(v.get('snippet',{}).get('publishedAt'),PUBLICATION_END)]
    videos={v['id']:v for v in rows}
    channel_ids={v['channel_id'] for v in videos.values() if v.get('channel_id')}
    focus=dict(BASE_CHANNELS)
    focus.update(extra_channels)
    channel_ids.update(focus)
    channel_data=api.batch('channels',channel_ids,'snippet,contentDetails,statistics')
    channels={v['id']:compact_channel(v) for v in channel_data}

    # One best-viewed <=500k-subscriber channel per lane and format. Explicitly
    # winner-selected: do not generalize these to a probability of success.
    picked=[]
    for lane,_,_ in LANES:
        for bucket in ('short_candidate_le60s','long_proxy_ge4min'):
            ids={i for q in queries if q['lane']==lane and q['bucket']==bucket and q['order']=='viewCount' for i in q['video_ids']}
            possible=[]
            for vid in ids:
                v=videos.get(vid);c=channels.get(v.get('channel_id')) if v else None
                if v and c and format_bucket(v.get('duration_seconds'))==bucket and v.get('views') is not None and c.get('public_subscribers') is not None and c['public_subscribers']<=500000:
                    possible.append((v['views'],v['id'],c['id']))
            for _,vid,cid in sorted(possible,reverse=True):
                if cid not in focus:
                    focus[cid]='winner-selected channel: '+lane+'/'+bucket
                    picked.append({'lane':lane,'bucket':bucket,'seed_video_id':vid,'channel_id':cid})
                    break

    samples=[];upload_ids=set()
    for cid,purpose in focus.items():
        channel=channels.get(cid); playlist=channel.get('uploads_playlist') if channel else None
        record={'channel_id':cid,'purpose':purpose,'status':'ok','pages':0,'ids':[],'scanned_ids':0}
        if not playlist:
            record['status']='missing_channel_or_uploads_playlist';samples.append(record);continue
        next_page=None
        # At most 4 pages = 200 most recent returned playlist entries. Scan a
        # bounded playlist, then calculate format-specific samples offline.
        while record['pages']<4:
            params={'part':'contentDetails,snippet','playlistId':playlist,'maxResults':50}
            if next_page:params['pageToken']=next_page
            obj=api.get('playlistItems',**params);record['pages']+=1
            if obj is None:
                record['status']='playlist_error';record['reason']=api.calls[-1]['reason'];break
            for item in obj.get('items',[]):
                record['scanned_ids']+=1
                d=item.get('contentDetails',{});vid=d.get('videoId')
                if vid and before_timestamp(d.get('videoPublishedAt'),PUBLICATION_END) and vid not in record['ids']:
                    record['ids'].append(vid)
            next_page=obj.get('nextPageToken')
            if not next_page or len(record['ids'])>=150:break
        record['playlist_has_more']=bool(next_page)
        upload_ids.update(record['ids']);samples.append(record)
        print('inventory',cid,record['status'],len(record['ids']),'pages',record['pages'],flush=True)
    for item in api.batch('videos',upload_ids-set(videos),'snippet,contentDetails,statistics'):
        if before_timestamp(item.get('snippet',{}).get('publishedAt'),PUBLICATION_END):
            row=compact_video(item);videos[row['id']]=row
    for s in samples:
        s['format_samples']=focus_samples(s['ids'],videos)
    return {
        'schema':1,'method':'Live public YouTube Data API v3; deliberately non-random discovery and channel samples. Search order, region and language bias apply. No retention, CTR, audience geography, watch time, exact subscriber gains, footage, or audio are supplied by this API.',
        'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'server_dates_distinct':sorted(set(api.server_dates)),
        'publication_end_exclusive':PUBLICATION_END,'trusted_session_end_exclusive':TRUSTED_END,'mature_end_exclusive':MATURE_END,
        'date_warning':'The trusted session date is 2026-11-05 UTC, but the runtime reports 2026-11-13. This refreshed search uses a later runtime-based cutoff to show what the API reports, but records after the trusted date and all live counts cannot be verified as of that date. The mismatch remains unresolved.',
        'region_code':'US','relevance_language_hint':'en',
        'queries':queries,'discovered_small_winners':picked,
        'channels':list(channels.values()),'videos':list(videos.values()),
        'channel_samples':samples,'api_call_receipts':api.calls,
    }


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--extra-channels',type=Path)
    args=p.parse_args();key=os.getenv('YOUTUBE_API_KEY')
    if not key:raise SystemExit('YouTube API key unavailable; no requests made.')
    extra=json.loads(args.extra_channels.read_text()) if args.extra_channels else {}
    if not isinstance(extra,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in extra.items()):
        raise SystemExit('Extra channel JSON must be an object mapping verified IDs to purpose labels.')
    report=collect(key,extra);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    count=sum(q['status']=='ok' for q in report['queries'])
    print('RESULT',count,'/',len(report['queries']),'searches;',len(report['videos']),'videos;',
          len(report['channels']),'channels;',len(report['channel_samples']),'inventories',flush=True)
    if not count or not report['videos']:raise SystemExit('No usable public API evidence obtained.')


if __name__=='__main__':main()
