"""Bounded, language-native YouTube Data API research; never a platform census.

This collects public metadata only. Search language/region are relevance and
availability hints, not proof of spoken language or audience geography. The
trusted session date and publication cutoff are fixed independently of the
runner clock. No secrets, comments, individual viewers, captions, videos, or
private channel analytics are stored. All planned lanes receive a receipt,
including those deliberately not attempted after a backoff circuit opens.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'monarch_viral_audit'))
from collect_youtube import API, before_timestamp, compact_channel, compact_video

TRUSTED_DATE = '2026-11-05'
TRUSTED_END = '2026-11-06T00:00:00Z'
MATURE_END = '2026-10-23T00:00:00Z'
YEAR_START = '2025-11-05T00:00:00Z'
RECENT_START = '2026-08-07T00:00:00Z'

# The single shared bridge-pier question improves topical comparability but
# coverage remains very incomplete; punctuation/local query conventions vary.
# Each lane yields videoDuration=short and medium searches, then classify by
# actual duration offline. Shorts under 4 minutes are NOT necessarily Shorts.
LANES = [
    ('en', 'US', 'how are bridge pillars built underwater 3d animation'),
    ('hi', 'IN', 'पानी के नीचे पुल के खंभे कैसे बनाते हैं 3d'),
    ('es', 'MX', 'cómo construyen pilares puentes debajo del agua animación'),
    ('pt', 'BR', 'como constroem pilares de pontes debaixo d água animação'),
    ('ur', 'PK', 'پانی کے اندر پل کے ستون کیسے بنائے جاتے ہیں'),
    ('ar', 'EG', 'كيف يتم بناء أعمدة الجسور تحت الماء رسوم متحركة'),
    ('id', 'ID', 'bagaimana membangun pilar jembatan di bawah air animasi'),
    ('fr', 'FR', 'comment construit on les piliers de pont sous l eau animation'),
    ('de', 'DE', 'wie baut man brückenpfeiler unter wasser animation'),
    ('ja', 'JP', '水中 橋脚 どのように 作る アニメーション'),
    ('bn', 'BD', 'পানির নিচে সেতুর পিলার কিভাবে তৈরি হয়'),
    ('tr', 'TR', 'su altında köprü ayakları nasıl yapılır animasyon'),
    ('it', 'IT', 'come si costruiscono i piloni dei ponti sott acqua animazione'),
    ('zh', 'TW', '水下橋墩是怎麼建造的 3D 動畫'),
    ('ru', 'RU', 'как строят опоры мостов под водой анимация'),
    ('ko', 'KR', '물속 다리 교각 어떻게 건설 애니메이션'),
    ('ta', 'IN', 'தண்ணீருக்கு அடியில் பாலம் தூண்கள் எப்படி கட்டுகிறார்கள்'),
]
DATE_LANES = {'en', 'hi', 'es', 'pt', 'ur', 'id'}

# Deliberately nonrandom, selected from documented public discovery leads.
# A lead is a hypothesis about intended market/channel language, not proof
# of the spoken language of each individual video or audience region.
SEEDS = [
    {'handle':'@Lesics','lead':'en','why':'English engineering animation network'},
    {'handle':'@animagraffs','lead':'en','why':'English 3D explanatory long-form'},
    {'handle':'@jaredowen','lead':'en','why':'English 3D explanatory long-form'},
    {'handle':'@practicalengineeringchannel','lead':'en','why':'English civil engineering'},
    {'handle':'@discoverinsideworld','lead':'en','why':'3D mechanism Short candidate'},
    {'id':'UC77PEgjHoZkdfpxcR3_k89Q','lead':'hi/en','why':'3D Eye; mixed language metadata'},
    {'handle':'@EngineerExplaininhindi','lead':'hi','why':'Hindi-language channel named in selected high-view video'},
    {'handle':'@professorofhow','lead':'hi','why':'Hindi/Hinglish animated explainer'},
    {'handle':'@MECHANICALTECHHINDI','lead':'hi','why':'Hindi mechanical engineering'},
    {'handle':'@superfaststudyexperiment','lead':'hi','why':'Hindi industrial machinery'},
    {'handle':'@engineerkohat','lead':'ur/hi','why':'self-described Urdu/Hindi engineering'},
    {'id':'UC3JOLlK2PB27Lb6IORByTsQ','lead':'es','why':'Lesics Española source-linked channel'},
    {'id':'UCocs1MzsjT_RSJiJ8R-EI4Q','lead':'es','why':'JAES Spanish source-linked channel'},
    {'handle':'@destravaomundo3d','lead':'pt','why':'Portuguese 3D mechanisms'},
    {'handle':'@manualdomundo','lead':'pt','why':'Portuguese adjacent popular science'},
    {'handle':'@LesicsPOR','lead':'pt','why':'Lesics/JAES network, handle may be renamed'},
    {'id':'UCI3uq3kieIAq0M6QCe3DOdA','lead':'ar','why':'JAES Arabic source-linked channel'},
    {'id':'UCuJu3eXfUVCOYxS6AaDPJVg','lead':'id','why':'ZexBrain Indonesian short mechanism lead'},
    {'handle':'@kokbisa','lead':'id','why':'Indonesian adjacent animated science'},
    {'handle':'@LesicsIndo','lead':'id','why':'Lesics/JAES network, handle may be renamed'},
    {'handle':'@LesicsFR','lead':'fr','why':'Lesics French animation network'},
    {'handle':'@LesicsDE','lead':'de','why':'Lesics/JAES network, handle may be renamed'},
    {'handle':'@KurzgesagtDE','lead':'de','why':'German adjacent animated science'},
    {'handle':'@LesicsJPN','lead':'ja','why':'Lesics Japanese network'},
    {'id':'UCekAEOx_o6tmW8MiBJbtrjA','lead':'bn','why':'Bengali science education lead'},
    {'id':'UCkOftoe4jNU0Y_Nh4Knk8GQ','lead':'tr','why':'JAES Turkish source-linked channel'},
    {'handle':'@geopop','lead':'it','why':'Italian science and infrastructure lead'},
    {'id':'UCW8ZE5m7AjINN9EzpxNYGCA','lead':'own','why':'MONARCHs Edit, not an approved pivot'},
]

# Independently sourced, intentionally selected examples. Include a same-topic
# English/Spanish pair, one named Hindi short and direct Magdeburg controls.
SEED_VIDEOS = [
    'hopBzK6BOwo', 'BTUV6mq4VLQ', 'uj2p4fJ4cB4', 'oeBOgv9iU8s',
    'fMrGLuNe67U', 'BTTccTEjjyQ', 'e4lhVG25HIw', 'NArAKj4zbB8', 'qhBUAOIXvbY',
    'DxyOpu84-EE', 'tpYNddw-Tls', 'l1zhga0fi6g', 'tXfQ6cFf9Ek',
    'QAeAkiYhid8', 'fj0l4SC4FYE', 'nwEyyIh6IF8',
]


def format_bucket(seconds):
    if seconds is None or seconds <= 0:
        return 'unknown'
    if seconds <= 60:
        return 'short_candidate_le60s'
    if seconds < 240:
        return 'ambiguous_61_to_239s'
    return 'long_proxy_ge4min'


def search_plan():
    plan = []
    # Pair short and long for each language before moving to the next. The
    # recently-uploaded probes follow all view-sorted lanes, if quota permits.
    for order in ('viewCount', 'date'):
        for lang, region, query in LANES:
            if order == 'date' and lang not in DATE_LANES:
                continue
            for bucket, duration in [('short_candidate_le60s', 'short'), ('long_proxy_ge4min', 'medium')]:
                plan.append({'lane':lang, 'region_code':region, 'relevance_language':lang,
                             'query':query, 'order':order, 'duration_filter':duration,
                             'bucket_requested':bucket,
                             'published_after':RECENT_START if order == 'date' else YEAR_START,
                             'published_before':TRUSTED_END, 'max_results':30})
    return plan


def with_separate_language_fields(item):
    row = compact_video(item)
    snippet = item.get('snippet', {})
    row.pop('language', None)  # Never conflate metadata language fields.
    row['default_audio_language'] = snippet.get('defaultAudioLanguage')
    row['default_metadata_language'] = snippet.get('defaultLanguage')
    row['caption_flag'] = item.get('contentDetails', {}).get('caption')
    return row


class ResearchAPI(API):
    """Separate search backoff from cheap metadata inventory; never hammer."""
    def __init__(self, key, sleep=time.sleep):
        super().__init__(key)
        self.sleep = sleep
        self.consecutive_failed_searches = 0
        self.search_circuit_open = False

    def search(self, params):
        if self.search_circuit_open:
            return None, [], 'skipped_backoff_circuit'
        attempts = []
        result = None
        for delay in (0, 15, 30):
            self.sleep(delay if delay else 4)
            result = super().get('search', **params)
            attempts.append(dict(self.calls[-1]))
            reason = attempts[-1].get('reason')
            if result is not None or reason not in ('rateLimitExceeded', 'userRateLimitExceeded'):
                break
        self.consecutive_failed_searches = 0 if result is not None else self.consecutive_failed_searches + 1
        reason = attempts[-1].get('reason') if attempts else None
        if self.consecutive_failed_searches >= 3 or reason in ('quotaExceeded','dailyLimitExceeded'):
            self.search_circuit_open = True
        return result, attempts, None

    def get(self, resource, **params):
        # Only search needs an explicit rate circuit, but metadata is still paced.
        self.sleep(0.15)
        return super().get(resource, **params)


def get_seed_channels(api):
    targets = []
    resolution = []
    seen = set()
    for seed in SEEDS:
        handle, cid = seed.get('handle'), seed.get('id')
        if handle:
            response = api.get('channels', part='snippet,contentDetails,statistics', forHandle=handle, maxResults=1)
        else:
            response = api.get('channels', part='snippet,contentDetails,statistics', id=cid, maxResults=1)
        raw = (response or {}).get('items', [])
        raw = raw[0] if raw else None
        reason = api.calls[-1].get('reason')
        if response is None:
            status = 'request_error'
        elif raw is None:
            status = 'not_found'
        elif raw['id'] in seen:
            status = 'duplicate_channel'
        else:
            status = 'resolved'
            seen.add(raw['id'])
            targets.append({'id':raw['id'],'language_lead':seed['lead'],
                            'selection':'named_seed','why':seed['why'],'raw':raw})
        row = {'handle':handle, 'requested_id':cid, 'language_lead':seed['lead'],
               'why':seed['why'], 'status':status, 'api_reason':reason,
               'returned_id':raw.get('id') if raw else None,
               'returned_title':raw.get('snippet', {}).get('title') if raw else None}
        resolution.append(row)
        print('seed', handle or cid, status, flush=True)
    return targets, resolution


def collect(key):
    api = ResearchAPI(key)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    targets, resolution = get_seed_channels(api)
    channels = {t['id']:compact_channel(t['raw']) for t in targets}

    queries = []
    all_ids = set(SEED_VIDEOS)
    for spec in search_plan():
        args = dict(part='snippet', type='video', q=spec['query'], regionCode=spec['region_code'],
                    relevanceLanguage=spec['relevance_language'], safeSearch='moderate',
                    order=spec['order'], videoDuration=spec['duration_filter'],
                    publishedAfter=spec['published_after'], publishedBefore=spec['published_before'],
                    maxResults=spec['max_results'])
        payload, attempts, skipped = api.search(args)
        result_ids = [x.get('id', {}).get('videoId') for x in (payload or {}).get('items', [])]
        result_ids = [x for x in result_ids if x]
        all_ids.update(result_ids)
        status = skipped or ('ok' if payload is not None else 'error')
        row = dict(spec, status=status, attempts=attempts, video_ids=result_ids)
        queries.append(row)
        print('search',spec['lane'],spec['order'],spec['duration_filter'],status,len(result_ids),flush=True)

    raw_videos = api.batch('videos', all_ids, 'snippet,contentDetails,statistics')
    videos = {v['id']:with_separate_language_fields(v) for v in raw_videos
              if before_timestamp(v.get('snippet',{}).get('publishedAt'), TRUSTED_END)}
    found_channel_ids = {v['channel_id'] for v in videos.values() if v.get('channel_id')} - set(channels)
    for c in api.batch('channels', found_channel_ids, 'snippet,contentDetails,statistics'):
        channels[c['id']] = compact_channel(c)

    # Up to one winner-selected discovery per language, prioritized by query
    # order. Small known subscriber channels are not automatically 'growing'.
    seen = {t['id'] for t in targets}
    dynamic = []
    for lang, _, _ in LANES:
        candidates = []
        for query in queries:
            if query['lane'] != lang or query['order'] != 'viewCount' or query['status'] != 'ok':
                continue
            for vid in query['video_ids']:
                v = videos.get(vid)
                c = channels.get(v.get('channel_id')) if v else None
                if not v or not c or c['id'] in seen:
                    continue
                subs = c.get('public_subscribers')
                if subs is None or subs > 500000 or v.get('views') is None:
                    continue
                if format_bucket(v.get('duration_seconds')) != query['bucket_requested']:
                    continue
                candidates.append((v['views'],vid,c['id'],query['bucket_requested']))
        if candidates:
            _,vid,cid,bucket = max(candidates)
            seen.add(cid)
            entry = {'id':cid,'language_lead':lang,'selection':'winner_selected_discovery',
                     'why':'highest-view eligible result on a <=500k-subscriber channel, in this query sample',
                     'seed_video_id':vid,'seed_bucket':bucket}
            targets.append(entry);dynamic.append(dict(entry))

    samples=[]
    upload_ids=set()
    for target in targets:
        cid=target['id']
        c=channels.get(cid)
        playlist=(c or {}).get('uploads_playlist')
        row={'channel_id':cid,'language_lead':target['language_lead'],'selection':target['selection'],
             'why':target['why'],'status':'ok','pages':0,'scanned_ids':0,'ids':[],
             'playlist_has_more':False}
        if not playlist:
            row['status']='missing_channel_or_uploads_playlist';samples.append(row);continue
        token=None
        # Up to four returned pages, retaining only uploads before session end.
        while row['pages'] < 4:
            params={'part':'contentDetails','playlistId':playlist,'maxResults':50}
            if token:params['pageToken']=token
            obj=api.get('playlistItems', **params);row['pages']+=1
            if obj is None:
                row['status']='playlist_error';row['reason']=api.calls[-1].get('reason');break
            for item in obj.get('items',[]):
                row['scanned_ids']+=1
                d=item.get('contentDetails',{});vid=d.get('videoId')
                if vid and before_timestamp(d.get('videoPublishedAt'), TRUSTED_END) and vid not in row['ids']:
                    row['ids'].append(vid)
            token=obj.get('nextPageToken')
            if not token or len(row['ids']) >= 150:
                break
        row['playlist_has_more']=bool(token)
        upload_ids.update(row['ids']);samples.append(row)
        print('inventory',cid,target['language_lead'],row['status'],len(row['ids']),flush=True)
    for item in api.batch('videos', upload_ids-set(videos), 'snippet,contentDetails,statistics'):
        if before_timestamp(item.get('snippet',{}).get('publishedAt'), TRUSTED_END):
            videos[item['id']]=with_separate_language_fields(item)
    finished=dt.datetime.now(dt.timezone.utc).isoformat()
    return {
        'schema':1,
        'scope':'Bounded nonrandom native-keyword discovery and selected channel uploads. '
                'Short candidates <=60s, long proxy >=4min; not confirmed platform classifications. '
                'No scripts, captions, playback, retention, CTR, geographic audience, or revenue data.',
        'trusted_session_date':TRUSTED_DATE,'published_before':TRUSTED_END,
        'maturity_published_before':MATURE_END,'runner_reported_started_utc':started,
        'runner_reported_finished_utc':finished,'server_dates_distinct':sorted(set(api.server_dates)),
        'clock_warning':'Runner/API server dates differ from trusted session date; counters are runner-reported snapshots, not verified Nov 5 counts.',
        'query_plan_count':len(search_plan()),'queries':queries,'seed_resolution':resolution,
        'dynamic_winner_selections':dynamic,'upload_samples':samples,
        'videos':list(videos.values()),'channels':list(channels.values()),'api_call_receipts':api.calls,
    }


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    key=os.environ.get('YOUTUBE_API_KEY')
    if not key:raise SystemExit('No configured YouTube API key; no requests attempted.')
    data=collect(key);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('RESULT', Counter(q['status'] for q in data['queries']),
          'videos',len(data['videos']),'channels',len(data['channels']),
          'inventories',len(data['upload_samples']),flush=True)
    if not data['videos']:
        raise SystemExit('No usable videos returned; inspect sanitized receipts.')


if __name__=='__main__':main()
