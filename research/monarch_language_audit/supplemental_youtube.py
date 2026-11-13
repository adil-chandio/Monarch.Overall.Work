"""Follow renamed language channels and explicit web leads without search API.

Selected public inventories and videos only, after search rate limits. It does
not replace the failed native-search sample or prove an upload's audio language.
Counters reflect the runner's reported clock, not backdated historical views.
"""
from __future__ import annotations
from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import sys

from multilingual_youtube import (ResearchAPI, TRUSTED_DATE, TRUSTED_END, MATURE_END,
                                  before_timestamp, compact_channel, with_separate_language_fields)

SEEDS = [
    {'id':'UCqZQJ4600a9wIfMPbYc60OQ','lead':'en','why':'Sabin Civil, renamed from the unresolved Lesics handle'},
    {'id':'UC7XvuBMRYoBdjKPIBOxt6XQ','lead':'fr','why':'Sabin Génie Civil; previously unresolved LesicsFR handle'},
    {'id':'UCoDboBE4RdYxZESjI__z7zQ','lead':'ja','why':'Sabin Japanese channel; previously unresolved LesicsJPN handle'},
    {'handle':'@Sabinz','lead':'ko','why':'Korean-language title/Hoover Dam network lead'},
    {'id':'UCJIm5LTOaqHK1axWi5x7_Ag','lead':'hi','why':'Hindi network channel discovered independently'},
    {'id':'UCTG1nHXvrY7xlUT-jV0gQsA','lead':'ta','why':'Tamil-language civil-engineering channel self-description'},
    {'handle':'@brightside5192','lead':'zh','why':'Traditional-Chinese adjacent infotainment; includes water-bridge-foundation lead'},
]
# Native-language public web leads, and closely related network translations.
# This is a convenience list, not a search result ranking or complete sample.
VIDEOS = [
    'KTku_oPAJpE','EYEC58EbeNI','9owj2L8MNkY','6B5VPlvJC1w',
    'HJ09UckQFn4','h-Lbhhgb9RA','WwlLrKLdU5E','_3GQRDV1XdU',
    'eB7FeQoYqFM','m8c_9InGxNM','pXx5Q9OY68Q','uj2p4fJ4cB4',
    'jh79YSCC8mM','RM9BeNFGuls','67H2LEar7vM','BFzpswX9iRg','wp_-bJ5uzLw',
    'f64XMJq2tYw','h_PanSLvu_s','N2Q71GTZ4Vc',
    'oeBOgv9iU8s','cW8fVC4my1g','dpUUb32Q0KI','fMrGLuNe67U',
    'hopBzK6BOwo','BTUV6mq4VLQ',
]


def collect(key):
    api=ResearchAPI(key)
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    targets=[];seed_resolution=[];seen=set();channels={}
    for seed in SEEDS:
        if seed.get('id'):
            payload=api.get('channels',part='snippet,contentDetails,statistics',id=seed['id'],maxResults=1)
        else:
            payload=api.get('channels',part='snippet,contentDetails,statistics',forHandle=seed['handle'],maxResults=1)
        raw=(payload or {}).get('items',[]);raw=raw[0] if raw else None
        status=('request_error' if payload is None else 'not_found' if raw is None else
                'duplicate_channel' if raw['id'] in seen else 'resolved')
        seed_resolution.append({'requested_id':seed.get('id'),'handle':seed.get('handle'),
                                'language_lead':seed['lead'],'why':seed['why'],'status':status,
                                'api_reason':api.calls[-1].get('reason'),
                                'returned_id':raw['id'] if raw else None,
                                'returned_title':raw.get('snippet',{}).get('title') if raw else None})
        if status=='resolved':
            seen.add(raw['id']); channels[raw['id']]=compact_channel(raw)
            targets.append({'id':raw['id'],'lead':seed['lead'],'why':seed['why']})
        print('seed',seed.get('id') or seed.get('handle'),status,flush=True)
    samples=[];all_ids=set(VIDEOS)
    for target in targets:
        channel=channels[target['id']];playlist=channel.get('uploads_playlist');token=None
        row={'channel_id':target['id'],'language_lead':target['lead'],'selection':'named_supplemental_seed',
             'why':target['why'],'status':'ok','pages':0,'scanned_ids':0,'ids':[],
             'playlist_has_more':False}
        if not playlist:
            row['status']='missing_uploads_playlist';samples.append(row);continue
        while row['pages']<4:
            args={'part':'contentDetails','playlistId':playlist,'maxResults':50}
            if token:args['pageToken']=token
            obj=api.get('playlistItems',**args);row['pages']+=1
            if obj is None:
                row['status']='playlist_error';row['reason']=api.calls[-1].get('reason');break
            for item in obj.get('items',[]):
                row['scanned_ids']+=1
                content=item.get('contentDetails',{});vid=content.get('videoId')
                if vid and before_timestamp(content.get('videoPublishedAt'),TRUSTED_END) and vid not in row['ids']:
                    row['ids'].append(vid)
            token=obj.get('nextPageToken')
            if not token or len(row['ids'])>=150:break
        row['playlist_has_more']=bool(token);samples.append(row);all_ids.update(row['ids'])
        print('inventory',target['lead'],row['status'],len(row['ids']),flush=True)
    raw_videos=api.batch('videos',all_ids,'snippet,contentDetails,statistics')
    videos=[with_separate_language_fields(v) for v in raw_videos
            if before_timestamp(v.get('snippet',{}).get('publishedAt'),TRUSTED_END)]
    seed_ids={v['id'] for v in videos}
    channel_ids={v['channel_id'] for v in videos if v.get('channel_id')}-set(channels)
    for c in api.batch('channels',channel_ids,'snippet,contentDetails,statistics'):
        channels[c['id']]=compact_channel(c)
    return {'schema':1,
            'scope':'Convenience sample of explicitly named channels and selected web-discovered videos; no search API calls. '
                    'Neither matched experiment nor evidence of spoken language or audience geography.',
            'trusted_session_date':TRUSTED_DATE,'published_before':TRUSTED_END,
            'maturity_published_before':MATURE_END,'runner_reported_started_utc':started,
            'runner_reported_finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'server_dates_distinct':sorted(set(api.server_dates)),
            'clock_warning':'Runner/API server dates differ from trusted session date; counters are runner-reported snapshots, not verified Nov 5 counts.',
            'query_plan_count':0,'queries':[],'seed_resolution':seed_resolution,
            'explicit_video_leads':[{'id':v,'status':'resolved_pre_session_end' if v in seed_ids else 'not_returned_or_after_cutoff'} for v in VIDEOS],
            'upload_samples':samples,'videos':videos,'channels':list(channels.values()),'api_call_receipts':api.calls}


def main():
    key=os.environ.get('YOUTUBE_API_KEY')
    if not key:raise SystemExit('No configured YouTube API key; no requests attempted.')
    root=Path(os.environ['RUNNER_TEMP']);data=collect(key)
    (root/'language-supplement.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('RESULT',Counter(x['status'] for x in data['seed_resolution']),
          'videos',len(data['videos']),'inventories',len(data['upload_samples']),flush=True)
    if not data['videos']:raise SystemExit('No public metadata returned; inspect sanitized receipts.')

if __name__=='__main__':main()
