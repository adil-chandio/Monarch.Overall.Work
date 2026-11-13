"""Reproduce descriptive counts from a checksum-verified multilingual snapshot.

Every per-channel statistic is based on at most the newest 30 eligible returned
playlist videos within one duration bucket. Not audience-language evidence,
random sampling, a success rate, or a retrospective November 5 counter.
"""
from __future__ import annotations
import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import statistics

from multilingual_youtube import MATURE_END, TRUSTED_END, before_timestamp, format_bucket

ROOT = Path(__file__).resolve().parent


def video_brief(v):
    return {k:v.get(k) for k in ('id','url','title','published_at','duration_seconds','views',
                                  'default_audio_language','default_metadata_language')}


def sample_channel(sample, video_map, cap=30):
    buckets={'short_candidate_le60s':[], 'long_proxy_ge4min':[], 'ambiguous_61_to_239s':[]}
    seen=set()
    skipped=Counter()
    for vid in sample.get('ids',[]):
        if vid in seen:
            skipped['duplicate_ids']+=1
            continue
        seen.add(vid)
        v=video_map.get(vid)
        if not v:
            skipped['missing_metadata']+=1;continue
        if v.get('channel_id') != sample['channel_id']:
            skipped['channel_mismatch']+=1;continue
        if not before_timestamp(v.get('published_at'), MATURE_END):
            skipped['not_mature']+=1;continue
        if v.get('views') is None or not isinstance(v.get('views'),int) or v['views']<0:
            skipped['missing_or_invalid_views']+=1;continue
        bucket=format_bucket(v.get('duration_seconds'))
        if bucket not in buckets:
            skipped['unknown_format']+=1;continue
        buckets[bucket].append(v)
    result={}
    for bucket,items in buckets.items():
        # Explicitly sort by aware publication time rather than assuming an
        # uploads playlist's returned positions are perfectly chronological.
        items=sorted(items,key=lambda v:dt.datetime.fromisoformat(
            v['published_at'].replace('Z','+00:00')),reverse=True)[:cap]
        sorted_views=sorted(items,key=lambda x:(x['views'],x['id']))
        result[bucket]={
            'sample_n':len(items),
            'median_views':statistics.median(v['views'] for v in items) if items else None,
            'min_views':sorted_views[0]['views'] if sorted_views else None,
            'max_views':sorted_views[-1]['views'] if sorted_views else None,
            'million_plus':sum(v['views']>=1_000_000 for v in items),
            'sample_ids':[v['id'] for v in items],
            'lowest':[video_brief(v) for v in sorted_views[:3]],
            'highest':[video_brief(v) for v in reversed(sorted_views[-3:])],
            'ge20min_sample_ids':[v['id'] for v in items if v['duration_seconds']>=1200],
        }
    return result,dict(skipped)


def summarize(data, source_digest=None):
    videos={v['id']:v for v in data['videos']}
    channels={c['id']:c for c in data['channels']}
    queries=[]
    for q in data['queries']:
        kept=[videos[x] for x in dict.fromkeys(q['video_ids']) if x in videos]
        counts=Counter(format_bucket(v.get('duration_seconds')) for v in kept)
        row={k:q[k] for k in ('lane','region_code','query','order','duration_filter','bucket_requested','status')}
        row.update({'result_ids_n':len(q['video_ids']), 'resolved_pre_session_end_n':len(kept),
                    'format_counts':dict(counts), 'attempt_n':len(q['attempts']),
                    'last_reason':q['attempts'][-1].get('reason') if q['attempts'] else None})
        queries.append(row)
    samples=[]
    for s in data['upload_samples']:
        stats, skipped=sample_channel(s,videos)
        channel=channels.get(s['channel_id'],{})
        samples.append({'channel_id':s['channel_id'],'channel_url':channel.get('url'),
                        'title':channel.get('title'),'handle':channel.get('handle'),
                        'language_lead':s['language_lead'],'selection':s['selection'],
                        'why':s['why'],'status':s['status'],'reason':s.get('reason'),
                        'public_subscribers':channel.get('public_subscribers'),
                        'public_channel_views':channel.get('public_channel_views'),
                        'public_video_count':channel.get('public_video_count'),
                        'scanned_ids':s['scanned_ids'],'pages':s['pages'],
                        'retained_pre_session_end_ids':len(s['ids']),
                        'playlist_has_more':s['playlist_has_more'],'skipped':skipped,'buckets':stats})
    return {'schema':1,'source':'multilingual_snapshot.json','source_sha256':source_digest,
            'clock_warning':data['clock_warning'],'runner_reported_started_utc':data['runner_reported_started_utc'],
            'runner_reported_finished_utc':data['runner_reported_finished_utc'],
            'trusted_session_date':data['trusted_session_date'],
            'published_before':data['published_before'],'maturity_published_before':data['maturity_published_before'],
            'query_status_counts':dict(Counter(q['status'] for q in data['queries'])),
            'seed_status_counts':dict(Counter(q['status'] for q in data['seed_resolution'])),
            'video_count':len(videos),'channel_count':len(channels),'sample_count':len(samples),
            'query_coverage':queries,'channel_samples':samples}


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'multilingual_snapshot.json')
    p.add_argument('--output',type=Path,default=ROOT/'multilingual_summary.json');args=p.parse_args()
    raw=args.source.read_bytes();data=json.loads(raw)
    args.output.write_text(json.dumps(summarize(data,hashlib.sha256(raw).hexdigest()),ensure_ascii=False,indent=2)+'\n')
    print('summary written',args.output)

if __name__=='__main__':main()
