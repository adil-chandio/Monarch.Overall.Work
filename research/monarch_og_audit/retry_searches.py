"""Retry only rate-limited searches from the original refreshed snapshot.

Every request and status is retained. Requests are deliberately rate-spaced;
repeated rate-limit responses back off and eventually stop rather than hammer
an API. Original snapshot stays intact for transparency.
"""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'monarch_viral_audit'))
from collect_youtube import API, before_timestamp, compact_channel, compact_video
from fresh_youtube import PUBLICATION_END

ROOT=Path(__file__).resolve().parent


def main():
    key=os.getenv('YOUTUBE_API_KEY')
    if not key:raise SystemExit('YouTube key missing; no requests made.')
    source=json.loads((ROOT/'youtube_refresh.json').read_text())
    pending=[q for q in source['queries'] if q['status']=='error' and q['reason']=='rateLimitExceeded']
    api=API(key);queries=[];ids=set();consecutive_abandoned=0
    for index,q in enumerate(pending):
        time.sleep(6 if index else 1)
        obj=None;attempt_count=0
        for delay in (0,15,30,60):
            if delay:time.sleep(delay)
            obj=api.get('search',part='snippet',type='video',q=q['query'],regionCode='US',
                        relevanceLanguage='en',safeSearch='moderate',order=q['order'],
                        videoDuration=q['duration_filter'],publishedAfter=q['published_after'],
                        publishedBefore=q['published_before'],maxResults=40)
            attempt_count+=1
            if obj is not None or api.calls[-1].get('reason')!='rateLimitExceeded':break
        result=[v.get('id',{}).get('videoId') for v in (obj or {}).get('items',[])]
        result=[v for v in result if v];ids.update(result)
        receipt=dict(q,status='ok' if obj is not None else 'error',
                     http_status=api.calls[-1]['http_status'],reason=api.calls[-1]['reason'],
                     video_ids=result,attempts=attempt_count)
        queries.append(receipt)
        consecutive_abandoned=0 if obj is not None else consecutive_abandoned+1
        print('retry',index+1,'/',len(pending),q['lane'],q['bucket'],q['order'],receipt['status'],len(result),'attempts',attempt_count,flush=True)
        if api.calls[-1].get('reason') in ('quotaExceeded','dailyLimitExceeded') or consecutive_abandoned>=3:
            print('Stopping after quota exhaustion or repeated persistent errors.',flush=True);break
    video_items=api.batch('videos',ids,'snippet,contentDetails,statistics')
    videos=[compact_video(v) for v in video_items if before_timestamp(v.get('snippet',{}).get('publishedAt'),PUBLICATION_END)]
    channel_ids={v['channel_id'] for v in videos if v.get('channel_id')}
    channels=[compact_channel(c) for c in api.batch('channels',channel_ids,'snippet,contentDetails,statistics')]
    data={'schema':1,'method':'Only failed rate-limited searches retried with throttling and bounded exponential backoff; original snapshot is unchanged. Nonrandom discovery, not a census.',
          'original_snapshot':'youtube_refresh.json',
          'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
          'server_dates_distinct':sorted(set(api.server_dates)),
          'pending_count':len(pending),'attempted_queries':len(queries),'queries':queries,
          'videos':videos,'channels':channels,'api_call_receipts':api.calls}
    dest=Path(os.environ['RUNNER_TEMP'])/'og-search-retry.json'
    dest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print('RESULT successful',sum(q['status']=='ok' for q in queries),'/',len(queries),'videos',len(videos),flush=True)


if __name__=='__main__':main()
