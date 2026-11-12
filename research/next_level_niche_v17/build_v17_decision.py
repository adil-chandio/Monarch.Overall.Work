#!/usr/bin/env python3
"""Derive a transparent, reproducible niche decision from the V17 real-API evidence.

No new API calls. Reads only the committed public-metadata evidence. Every
filter is numeric and printed; qualitative rejections are labelled as such.
"""
import json, os, re, collections, datetime

D = os.path.join(os.path.dirname(__file__), 'api_evidence')
def load(name): return json.load(open(os.path.join(D, name)))

run = load('run.json')
lanes = {x['slug']: x['metrics'] for x in load('lane_metrics_v17.json')['lanes']}
vd = load('video_details_v17.json')['videos']
byid = {v['id']: v for v in vd}
chs = load('channel_statistics_v17.json')['channels']
mil = load('million_view_videos_v17.json')['videos']
lanes_raw = load('lanes_v17.json')['lanes']
lane_of = collections.defaultdict(list)
for L in lanes_raw:
    for i in L['ids']:
        lane_of[i].append(L['slug'])

# newer-channel (created 2023+) million-view videos by lane
newer = {c['title'] for c in chs if c.get('newer_channel_created_since_2023')}
cluster = collections.Counter()
for v in mil:
    if v.get('channel') in newer:
        for l in lane_of.get(v['id'], []):
            cluster[l] += 1

# transparent filter funnel (numeric only)
all_lanes = [s for s in lanes if s.endswith('_all')]
recent_lanes = [s for s in lanes if s.endswith('_recent')]
def recent_of(all_slug): return all_slug[:-4] + '_recent'
funnel = []
for s in sorted(all_lanes):
    m, r = lanes[s], lanes.get(recent_of(s), {})
    c1 = m['million_count'] >= 10 and m['ten_million_count'] >= 1
    c2 = m['top3_share'] < 0.60
    c3 = m['winner_ratio'] < 100.0
    c5 = r.get('million_count', 0) >= 1
    funnel.append({
        'lane': s,
        'million_count': m['million_count'],
        'ten_million_count': m['ten_million_count'],
        'median_views': m['median_views'],
        'top3_share': m['top3_share'],
        'winner_ratio': m['winner_ratio'],
        'caption_rate': m['caption_rate'],
        'recent_million_count': r.get('million_count', 0),
        'C1_all_time_depth': bool(c1),
        'C2_not_winner_takes_all': bool(c2),
        'C3_reachable_median': bool(c3),
        'C5_fresh_million_view': bool(c5),
        'numeric_pass': bool(c1 and c2 and c3 and c5),
    })
numeric_winners = [x['lane'] for x in funnel if x['numeric_pass']]

# chosen theme evidence
chosen = {
    'theme': 'Map / geo-forensics explainers (evergreen map mysteries + recent-event map forensics)',
    'all_time_lane': lanes['map_animation_all'],
    'recent_lane': lanes['map_animation_recent'],
    'newer_channel_million_view_videos_by_lane': dict(cluster.most_common()),
    'evergreen_examples': [],
    'recent_event_examples': [],
}
for i in ['t1DECN9zS_8','TIP_4hrzLTk','lwglySYUuSY','cvZls9tcCTI','HA1hs67ThXc','DjhZuN0woDY','Gt2mYPwXyAc','HKdjIFjYZ40','libKVRa01L8','RSeWI6Ar-j0','ovyoQMhGsYU','tT-BzWbyqkw']:
    v = byid.get(i)
    if v:
        chosen['evergreen_examples'].append({k: v.get(k) for k in ['id','title','channel','views','duration_seconds','published','category_id','caption','default_language']})
for i in ['J_sNJjrN4J4','u5F175REX_U','RF5Nw4g7AxE','Vr209Lt6_cA','2tjiaBnx5fE']:
    v = byid.get(i)
    if v:
        chosen['recent_event_examples'].append({k: v.get(k) for k in ['id','title','channel','views','duration_seconds','published','category_id','caption']})

# channel proxies (NOT a verified growth ranking)
chan_proxy = []
for title in ['GeoGlobeTales','Geo All Day','Howtown','Rainlit Village','W Sound','Street Dog Revival','Dr. Healthcare','Health Manager','Nature Global','Tarazai','Story Arc Paws']:
    c = next((x for x in chs if x['title'] == title), None)
    if not c: continue
    age = c.get('channel_age_days') or 0
    views = c.get('channel_views') or 0
    nvid = c.get('channel_video_count') or 0
    chan_proxy.append({
        'channel': title,
        'created': c.get('published','')[:10],
        'age_days': age,
        'subscribers': c.get('subscribers'),
        'channel_views': views,
        'channel_video_count': nvid,
        'views_per_channel_day': round(views/max(1,age), 2),
        'views_per_video': round(views/max(1,nvid), 2),
        'newer_channel_created_since_2023': c.get('newer_channel_created_since_2023'),
        'recent_upload_median_views': c.get('recent_upload_median_views'),
        'note': 'public cumulative/age proxy only, NOT verified subscriber growth',
    })

# script-structure evidence: creator-published description beat counts + chapter markers
chapter_re = re.compile(r'(?m)^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s*[^\n]{0,120}')
chapters = {}
for i in ['u5F175REX_U','ZTimVStLZh0','xT10kTnYLDQ','d-CuF6dlqLg']:
    v = byid.get(i)
    if v:
        chapters[i] = {
            'title': v['title'], 'views': v['views'], 'duration_seconds': v['duration_seconds'],
            'chapter_markers': chapter_re.findall(v.get('description') or '')[:20],
        }

# transcript access evidence
t1 = load('reverse_teardowns_v17.json')
t2 = load('transcript_fallback_run_v17.json')
transcripts = {
    'first_pass_attempts': t1['count'],
    'first_pass_errors': sum(1 for x in t1['items'] if x['teardown'].get('transcript_status',{}).get('status') == 'error'),
    'second_pass_targets': t2['targets'],
    'second_pass_usable': t2['usable_transcripts'],
    'second_pass_errors': t2['errors'],
    'reason': 'YouTube datacenter sign-in bot-check / RequestBlocked',
    'claimed': 'no verbatim competitor transcript from YouTube captions was obtained',
}

out = {
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'source': 'committed V17 YouTube Data API evidence, run.json ' + run['generated_utc'],
    'api_run_counts': {k: run[k] for k in ['lane_reports','lane_rows','unique_videos','channels_resolved','most_popular_regions','video_categories','million_view_videos','ten_million_videos','candidate_videos_after_title_safety','comments_videos','teardowns','thumbnail_stats','quota_used_approx']},
    'secret_value_printed_or_stored': run['secret_value_printed_or_stored'],
    'filter_definitions': {
        'C1_all_time_depth': 'all-time lane has >=10 videos with >=1M views and >=1 with >=10M views',
        'C2_not_winner_takes_all': 'top3_share < 0.60',
        'C3_reachable_median': 'winner_ratio < 100',
        'C5_fresh_million_view': 'matching recent lane has >=1 video with >=1M views',
        'C4_C6_qualitative': '100% ownable original assets, no third-party clip dependency, no repetitive-template risk',
    },
    'filter_funnel': funnel,
    'numeric_winners': numeric_winners,
    'qualitative_rejections': {
        'animal_rescue_all': 'needs third-party animal/rescue footage (rights + reused-content risk); user set caught-on-camera aside',
        'microdrama_all': 'needs serialized cast/dubbing and has 20.0% fresh-30d share; higher repetition/template risk',
        'satisfying_all': 'fresh lane 0 million-view videos; physical restoration footage not 100% ownable at low cost',
        'science_humor_all': 'fresh lane 0 million-view videos; 56.7% top3 share',
        'ai_tutorial_all': 'fresh lane median 5 views, 0 million-view videos',
        'viral_breakdown_recent': '71.3% top3 share; top hits are trend/dance clips, not an ownable series',
    },
    'chosen': chosen,
    'channel_public_proxies': chan_proxy,
    'creator_published_chapter_beats': chapters,
    'transcript_access': transcripts,
    'boundary': run['boundary'],
}
with open(os.path.join(os.path.dirname(__file__), 'DECISION_V17.json'), 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print('WROTE DECISION_V17.json')
print('numeric winners:', numeric_winners)
print('newer-channel million-view cluster:', dict(cluster.most_common()))
print('transcript access:', transcripts['first_pass_errors'], '/', transcripts['first_pass_attempts'], 'and', transcripts['second_pass_usable'], '/', transcripts['second_pass_targets'])
