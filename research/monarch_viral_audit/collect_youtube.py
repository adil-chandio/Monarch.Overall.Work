"""Small, reproducible YouTube Data API v3 snapshot for an editorial decision.

No credentials are printed or written. Search results are discovery samples,
not a census; public counters are not private YouTube Studio analytics.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TRUSTED_END = '2026-11-06T00:00:00Z'  # fixed session date, inclusive through November 5
YEAR_START = '2025-11-05T00:00:00Z'
RECENT_START = '2026-08-07T00:00:00Z'

# A deliberate, non-random set. 'short' is the API's <4-min duration filter,
# not proof that each item is a vertical Short. Region is availability only.
SEARCH_PLAN = [
    ('exact_celebrity', 'celebrity day in the life pov animation', 'viewCount', 'short'),
    ('exact_celebrity', 'pov wake up as ronaldo animation', 'viewCount', 'short'),
    ('football_pov', 'pov you are a football player', 'viewCount', 'short'),
    ('football_pov', 'pov you are a football player', 'date', 'short'),
    ('football_animation', 'football 3d animation', 'viewCount', 'short'),
    ('football_animation', 'football 3d animation', 'date', 'short'),
    ('animated_life', 'day in the life animated short story', 'viewCount', 'short'),
    ('animated_life', 'day in the life animated short story', 'date', 'short'),
    ('science_explainer', '3d science facts explained animation', 'viewCount', 'short'),
    ('science_explainer', '3d science facts explained animation', 'date', 'short'),
    ('geography_explainer', 'geography map animation explained', 'viewCount', 'short'),
    ('geography_explainer', 'geography map animation explained', 'date', 'short'),
    ('ai_tutorial', 'ai tools build project tutorial', 'viewCount', 'medium'),
    ('motivation', 'motivation personal growth animation', 'viewCount', 'short'),
    ('wildlife', 'wildlife caught on camera explained', 'viewCount', 'medium'),
    ('wildlife', 'wildlife caught on camera explained', 'date', 'medium'),
]

# IDs sourced from existing versioned public-data research. They are selected
# comparators, not a claim that the channels have grown during this session.
FOCUS_CHANNELS = {
    'UCW8ZE5m7AjINN9EzpxNYGCA': 'existing MONARCHs Edit channel',
    'UCdcJDQafWwwCyDiaYcehm0w': 'football POV adjacent',
    'UCqLSt_CKF-D6UQF8Npu94ZA': 'football animation adjacent',
    'UCc9J-nAU57iFkurEFcNmamQ': 'relatable animation adjacent',
    'UCucoJ5yVEEQlUnGHfiQIPQA': 'small animation comparison',
    'UCLgzNX8OGekeI53OOBI2R9g': 'small explainer comparison',
    'UCPjqXCK0WGx0u3O6fU8FtkA': 'football explainer comparison',
    'UCIq0O28uxho0HPrIQgQdP5Q': 'football animation comparison',
    'UChFs0d8syPIK6x8q4C6BrJw': 'established animation benchmark',
    'UCbKWv2x9t6u8yZoB3KcPtnw': 'established animation benchmark',
}
KNOWN_VIDEOS = [
    'aWHX5Awe_TI', 'jhC85CjxF4E', '5vmyWV9-hXg',
    '8wtQAI_ZZlQ', 'wsPiYEnHS2U', 'nrXj8rlwzsI', 'GHT3RyE9wGI',
    'WB9P8WZtUA4', 'VE4GMIi39uQ', 'Tgopx8TcaiM', 'ZTKh3IDAkTg',
    '60rbnH1eUF0', 'C637UcpHfNY', 'jfUU24gaqNg',
]


def duration_seconds(value: str) -> int | float | None:
    # YouTube uses ISO 8601 durations. A whole-day duration may omit the T
    # component; PT and P alone are not valid durations.
    match = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?', value or '')
    if not match or (value or '').endswith('T') or not any(part is not None for part in match.groups()):
        return None
    day, hour, minute, second = match.groups()
    total = int(day or 0)*86400 + int(hour or 0)*3600 + int(minute or 0)*60 + float(second or 0)
    return int(total) if total.is_integer() else total


def before_timestamp(published: str | None, exclusive_end: str) -> bool:
    # String comparison mishandles timestamps exactly at a boundary when one
    # includes fractional seconds. Parse offsets and reject naive timestamps.
    if not isinstance(published, str) or not isinstance(exclusive_end, str) or not published:
        return False
    try:
        value = dt.datetime.fromisoformat(published.replace('Z', '+00:00'))
        cutoff = dt.datetime.fromisoformat(exclusive_end.replace('Z', '+00:00'))
        return value.tzinfo is not None and cutoff.tzinfo is not None and value < cutoff
    except (TypeError, ValueError):
        return False


def before_cutoff(published: str | None) -> bool:
    return before_timestamp(published, TRUSTED_END)


def chunks(values, count=50):
    values = list(values)
    for i in range(0, len(values), count):
        yield values[i:i+count]


def compact_video(v):
    s = v.get('snippet', {}); c = v.get('contentDetails', {}); a = v.get('statistics', {})
    return {
        'id': v['id'], 'url': 'https://www.youtube.com/watch?v=' + v['id'],
        'title': s.get('title'), 'channel_id': s.get('channelId'),
        'channel_title': s.get('channelTitle'), 'published_at': s.get('publishedAt'),
        'duration_iso': c.get('duration'), 'duration_seconds': duration_seconds(c.get('duration')),
        'views': int(a['viewCount']) if 'viewCount' in a else None,
        'likes': int(a['likeCount']) if 'likeCount' in a else None,
        'comments': int(a['commentCount']) if 'commentCount' in a else None,
        'language': s.get('defaultAudioLanguage') or s.get('defaultLanguage'),
        'category_id': s.get('categoryId'),
        'thumbnail_url': (s.get('thumbnails',{}).get('high',{}) or s.get('thumbnails',{}).get('medium',{})).get('url'),
    }


def compact_channel(c):
    s=c.get('snippet',{});a=c.get('statistics',{});r=c.get('contentDetails',{}).get('relatedPlaylists',{})
    return {
        'id': c['id'], 'url': 'https://www.youtube.com/channel/'+c['id'],
        'title': s.get('title'), 'handle': s.get('customUrl'), 'created_at': s.get('publishedAt'),
        'public_subscribers': int(a['subscriberCount']) if 'subscriberCount' in a and not a.get('hiddenSubscriberCount') else None,
        'hidden_subscribers': bool(a.get('hiddenSubscriberCount')), 'public_video_count': int(a['videoCount']) if 'videoCount' in a else None,
        'public_channel_views': int(a['viewCount']) if 'viewCount' in a else None,
        'uploads_playlist': r.get('uploads'),
    }


class API:
    def __init__(self, key):
        self.key=key; self.calls=[]; self.server_dates=[]

    def get(self, resource, **params):
        # We never log URLs or exception strings, which can contain query keys.
        params['key']=self.key
        url='https://www.googleapis.com/youtube/v3/'+resource+'?'+urllib.parse.urlencode(params)
        status=None; reason=None
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                status=response.status
                if response.headers.get('Date'): self.server_dates.append(response.headers['Date'])
                result=json.load(response)
        except urllib.error.HTTPError as exc:
            status=exc.code
            try:
                error=json.loads(exc.read()).get('error',{})
                reason=(error.get('errors') or [{}])[0].get('reason') or error.get('status')
            except Exception:
                reason='http_error'
            result=None
        except Exception as exc:
            reason=type(exc).__name__; result=None
        self.calls.append({'resource': resource, 'http_status':status, 'reason':reason})
        return result

    def batch(self, resource, ids, part):
        result=[]
        for ids_part in chunks(sorted(set(ids))):
            payload=self.get(resource, part=part, id=','.join(ids_part), maxResults=50)
            if payload is not None:
                result.extend(payload.get('items',[]))
        return result


def collect(key):
    api=API(key); queries=[]; video_ids=set(KNOWN_VIDEOS)
    for group, query, order, duration in SEARCH_PLAN:
        payload=api.get('search', part='snippet', q=query, type='video', regionCode='US',
                        relevanceLanguage='en', safeSearch='moderate', order=order,
                        videoDuration=duration, publishedAfter=RECENT_START if order=='date' else YEAR_START,
                        publishedBefore=TRUSTED_END, maxResults=30)
        ids=[x.get('id',{}).get('videoId') for x in (payload or {}).get('items',[])]
        ids=[x for x in ids if x];video_ids.update(ids)
        last=api.calls[-1]
        queries.append({'group':group,'query':query,'order':order,'duration_filter':duration,
                        'published_after':RECENT_START if order=='date' else YEAR_START,
                        'published_before':TRUSTED_END,'status':'ok' if payload is not None else 'error',
                        'http_status':last['http_status'],'reason':last['reason'],'video_ids':ids})
        print('search',group,order,'status',last['http_status'],'returned',len(ids),flush=True)
        if payload is None and last.get('reason') in ('quotaExceeded','dailyLimitExceeded'):
            break

    seed_videos=api.batch('videos',video_ids,'snippet,contentDetails,statistics')
    seed_videos=[v for v in seed_videos if before_cutoff(v.get('snippet',{}).get('publishedAt'))]
    channel_ids={v.get('snippet',{}).get('channelId') for v in seed_videos};channel_ids.discard(None)
    channel_ids.update(FOCUS_CHANNELS)
    channel_records=api.batch('channels',channel_ids,'snippet,contentDetails,statistics')
    channel_map={c['id']:compact_channel(c) for c in channel_records}
    videos={v['id']:compact_video(v) for v in seed_videos}

    # Add a few small-channel winners from different search lanes. These are
    # deliberately selected outliers, not evidence of growth or success rates.
    focus=dict(FOCUS_CHANNELS)
    dynamic=[]
    for group in ('exact_celebrity','football_pov','football_animation','animated_life','science_explainer','geography_explainer','wildlife'):
        ids={i for q in queries if q['group']==group and q['order']=='viewCount' for i in q['video_ids']}
        candidates=[]
        for vid in ids:
            v=videos.get(vid);c=channel_map.get(v['channel_id']) if v else None
            if v and c and v['views'] is not None and c['public_subscribers'] is not None and c['public_subscribers']<=150000:
                candidates.append((v['views'],c['id']))
        for _,cid in sorted(candidates,reverse=True):
            if cid not in focus and cid not in dynamic:
                dynamic.append(cid);focus[cid]='query-selected small-channel candidate: '+group;break

    uploads=[]; upload_video_ids=set()
    for cid, purpose in focus.items():
        c=channel_map.get(cid); playlist=c.get('uploads_playlist') if c else None
        row={'channel_id':cid,'purpose':purpose,'ids':[],'pages':0,'status':'ok'}
        if not playlist:
            row['status']='missing_channel_or_playlist';uploads.append(row);continue
        token=None
        while len(row['ids'])<25 and row['pages']<3:
            params={'part':'contentDetails,snippet','playlistId':playlist,'maxResults':50}
            if token: params['pageToken']=token
            payload=api.get('playlistItems',**params);row['pages']+=1
            if payload is None:
                row['status']='error';row['reason']=api.calls[-1]['reason'];break
            for item in payload.get('items',[]):
                details=item.get('contentDetails',{}); vid=details.get('videoId'); pub=details.get('videoPublishedAt')
                if vid and before_cutoff(pub) and vid not in row['ids']:
                    row['ids'].append(vid)
            token=payload.get('nextPageToken')
            if not token:break
        row['ids']=row['ids'][:25];upload_video_ids.update(row['ids']);uploads.append(row)
        print('channel',cid,'upload_ids',len(row['ids']),'pages',row['pages'],'status',row['status'],flush=True)

    for v in api.batch('videos',upload_video_ids-set(videos),'snippet,contentDetails,statistics'):
        if before_cutoff(v.get('snippet',{}).get('publishedAt')):videos[v['id']]=compact_video(v)
    report={
        'schema':1,
        'scope':'Non-random YouTube Data API v3 keyword discovery, selected channel uploads and public cumulative counts. Short filter means under 4 minutes, not confirmed Shorts. No watch time, retention, country-audience, revenue, verified growth, scripts, frames or sound are available from this API.',
        'trusted_session_date':'2026-11-05','runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'server_dates_distinct':sorted(set(api.server_dates)),
        'cutoff_published_before':TRUSTED_END,'region_code':'US','relevance_language':'en',
        'query_plan_count':len(SEARCH_PLAN),'queries':queries,'videos':list(videos.values()),
        'channels':list(channel_map.values()),'upload_samples':uploads,'call_receipts':api.calls,
    }
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    key=os.environ.get('YOUTUBE_API_KEY')
    if not key:sys.exit('No configured YouTube Data API key in the runner; no network request attempted.')
    data=collect(key);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    ok=sum(q['status']=='ok' for q in data['queries'])
    print('RESULT searches',ok,'/',len(data['queries']),'videos',len(data['videos']),
          'channels',len(data['channels']),'uploads',len(data['upload_samples']),flush=True)
    if not data['videos'] or not ok:
        raise SystemExit('No usable public YouTube API data obtained; inspect sanitized receipts.')


if __name__=='__main__':main()
