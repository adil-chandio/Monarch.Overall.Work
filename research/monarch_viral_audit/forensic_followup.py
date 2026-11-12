"""Follow-up API inventory and *unverified* Gemini YouTube-input descriptions.

Public thumbnails go in a review zip, not committed to this repository. The
workflow uploads that zip as a repository Git blob for review; provider retention
is not guaranteed to be short. Caption files, if any, stay in a local temporary
directory and are not included in the zip. No video is downloaded. Captions are
requested without authentication or bypassing access controls. Credentials are
never printed. Future comment receipts contain only aggregate counts, not text
or author identifiers.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
try:
    from .collect_youtube import API, before_cutoff, before_timestamp, compact_channel, compact_video
except ImportError:
    from collect_youtube import API, before_cutoff, before_timestamp, compact_channel, compact_video

ROOT=Path(__file__).resolve().parent
META_OUT=Path('/tmp/monarch-forensic-followup.json')
REVIEW_ZIP=Path('/tmp/monarch-research-review.zip')
CHANNELS={
    'UCfYdmsLO4Q8_IHklTyYieLg':'Monarch Cam: distinct existing user channel',
    'UC0Badcq36RBDHN-e3N1Papg':'Mischief Time: large football-parody benchmark',
    'UC77PEgjHoZkdfpxcR3_k89Q':'3D Eye: 3D explanatory benchmark',
    'UCPKVNqfbunZCkbvjBgf6CdA':'GeoGlobeTales: geography benchmark',
}
OWN_OLDER=['J5utnZFV1xE','cBuip12iVcs','SLpqoYCEPuk','dxhjYjkWZvY','l7N1U4wWyn8']
# The high/low pairs are deliberate examples, not statistically matched trials.
TARGETS=[
    ('aWHX5Awe_TI','DusanFC: high-view football POV'),
    ('kkG03vsJ97A','DusanFC: low-view recent upload'),
    ('8wtQAI_ZZlQ','LV Animation: high-view football animation'),
    ('h6xfK7V5WRI','LV Animation: same-title, lower-view upload'),
    ('GHT3RyE9wGI','Stick Stuff Happens: high-view snooze upload'),
    ('O68pHy2gRSw','Stick Stuff Happens: lower-view day-in-life upload'),
    ('W1WdY5OwOF4','Mischief Time: high-view football-parody upload'),
    ('fMrGLuNe67U','3D Eye: high-view bridge explainer'),
    ('F1rTsvWTbZc','The Green Grid: high-view geography upload'),
    ('5LJK6wFQUaY','The Green Grid: lower-view history upload'),
    ('8atK0pF4oJY','Day One Films: high-view animated film; three windows only'),
]
COMMENT_TARGETS=['aWHX5Awe_TI','8wtQAI_ZZlQ','GHT3RyE9wGI','W1WdY5OwOF4',
                 'fMrGLuNe67U','F1rTsvWTbZc','8atK0pF4oJY','O68pHy2gRSw']
CAPTION_TARGETS=['aWHX5Awe_TI','W1WdY5OwOF4','fMrGLuNe67U','GHT3RyE9wGI','k5s1cMNTmGs']
OVERLAP={'aWHX5Awe_TI','GHT3RyE9wGI','W1WdY5OwOF4','fMrGLuNe67U','F1rTsvWTbZc'}
MODEL='gemini-3.1-flash-lite-preview'
PROMPT=(
 'Examine only the supplied public video window. Provide four labeled sections: '
 '(1) visible subjects and setting; (2) broad sequence from beginning through end '
 'of this window, without inventing exact second-by-second timing; (3) apparent '
 'character/object motion, framing and any clear transitions; (4) unknowns. '
 'Describe only what is visibly supported, do not infer identities, production '
 'software, private audience response or why a video succeeded. Indicate if an '
 'object/action cannot be seen clearly. Do not infer or discuss audio. Do not '
 'transcribe or quote dialogue, captions or other copyrighted content. '
 'Acknowledge a static shot if that is what appears. Your description may be wrong.'
)


def choose_median(rows):
    """A typical 8–60 s item published strictly before the 14-day boundary."""
    eligible=[v for v in rows if v.get('views') is not None and v.get('duration_seconds') is not None
              and 8<=v['duration_seconds']<=60 and before_timestamp(v.get('published_at'), '2026-10-23T00:00:00Z')]
    if not eligible:
        eligible=[v for v in rows if v.get('views') is not None and v.get('duration_seconds') is not None
                  and 8<=v['duration_seconds']<=60]
    if not eligible:return None,0
    ordered=sorted(eligible,key=lambda v:(v['views'],v['id']))
    midpoint=statistics.median(v['views'] for v in ordered)
    return min(ordered,key=lambda v:(abs(v['views']-midpoint),v['id'])),len(ordered)


def summarize_comments(vid, payload):
    """Discard individual public comments/identifiers before any file output."""
    items = payload.get('items', [])
    mentions = 0
    for thread in items:
        snippet = thread.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
        text = (snippet.get('textDisplay') or '')[:500]
        mentions += 'thumbnail' in text.lower()
    return {'video_id': vid, 'status': 'ok', 'returned': len(items),
            'comment_text_not_committed': True, 'mentions_thumbnail_case_insensitive': mentions}


def get_channel_sample(api,cid,purpose):
    payload=api.get('channels',part='snippet,contentDetails,statistics',id=cid,maxResults=1)
    items=(payload or {}).get('items',[])
    out={'purpose':purpose,'status':'ok' if items else 'channel_error_or_missing','channel':compact_channel(items[0]) if items else None,
         'upload_ids':[],'pages':0}
    playlist=out['channel']['uploads_playlist'] if out['channel'] else None
    token=None
    while playlist and len(out['upload_ids'])<25 and out['pages']<3:
        params={'part':'snippet,contentDetails','playlistId':playlist,'maxResults':50}
        if token:params['pageToken']=token
        obj=api.get('playlistItems',**params);out['pages']+=1
        if obj is None:out['status']='playlist_error';out['reason']=api.calls[-1]['reason'];break
        for item in obj.get('items',[]):
            c=item.get('contentDetails',{});vid=c.get('videoId');pub=c.get('videoPublishedAt')
            if vid and before_cutoff(pub) and vid not in out['upload_ids']:out['upload_ids'].append(vid)
        token=obj.get('nextPageToken')
        if not token:break
    out['upload_ids']=out['upload_ids'][:25]
    return out


def gemini_window(key,vid,label,start,end,fps):
    r={'video_id':vid,'label':label,'requested_window_seconds':[start,end],'requested_fps':fps,
       'status':'not_attempted'}
    if not key:r['status']='gemini_key_missing';return r
    parts=[{'fileData':{'fileUri':'https://www.youtube.com/watch?v='+vid},
            'videoMetadata':{'startOffset':f'{start}s','endOffset':f'{end}s','fps':fps}}, {'text':PROMPT}]
    body={'contents':[{'parts':parts}],'generationConfig':{'maxOutputTokens':1400,'temperature':0.2}}
    req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/'+MODEL+':generateContent',
        data=json.dumps(body).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=120) as response: data=json.load(response);r['http_status']=response.status
        cand=(data.get('candidates') or [{}])[0]
        r['finish_reason']=cand.get('finishReason');r['usage']=data.get('usageMetadata',{})
        r['model_description']='\n'.join(p.get('text','') for p in cand.get('content',{}).get('parts',[]) if p.get('text') and not p.get('thought'))
        r['status']='ok' if r['model_description'] else 'empty'
    except urllib.error.HTTPError as exc:
        r['http_status']=exc.code;r['status']='http_error'
        try:r['error_status']=json.loads(exc.read()).get('error',{}).get('status')
        except Exception:pass
    except Exception as exc:r['status']='error';r['error_type']=type(exc).__name__
    return r


def captions_probe(vid,tmp):
    out={'video_id':vid,'method':'Unauthenticated yt-dlp subtitle request only; no video download or bot-challenge bypass.'}
    try:
        import importlib.metadata
        out['yt_dlp_version']=importlib.metadata.version('yt-dlp')
        result=subprocess.run(['yt-dlp','--skip-download','--no-playlist','--no-warnings',
           '--write-subs','--write-auto-subs','--sub-langs','en,en-US,en-GB','--sub-format','vtt',
           '-o',str(tmp/(vid+'.%(ext)s')),'https://www.youtube.com/watch?v='+vid],
           capture_output=True,text=True,timeout=55)
        combined=(result.stdout+'\n'+result.stderr).lower();out['exit_code']=result.returncode
        files=list(tmp.glob(vid+'.*.vtt'))
        if files:
            data=files[0].read_bytes();out.update({'status':'caption_file_obtained',
                'filename':files[0].name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        elif 'sign in to confirm' in combined or 'not a bot' in combined:
            out['status']='blocked_bot_verification'
        elif result.returncode!=0:out['status']='request_error'
        else:out['status']='no_matching_english_captions_obtained'
    except subprocess.TimeoutExpired:out['status']='timeout'
    except Exception as exc:out['status']='error';out['error_type']=type(exc).__name__
    return out


def main():
    key=os.getenv('YOUTUBE_API_KEY');gkey=os.getenv('GEMINI_API_KEY')
    if not key:raise SystemExit('YouTube API key missing; no API calls made.')
    api=API(key);base=json.loads((ROOT/'youtube_snapshot.json').read_text())
    videos={v['id']:v for v in base['videos']};samples=[]
    for cid,purpose in CHANNELS.items():
        s=get_channel_sample(api,cid,purpose);samples.append(s)
        print('inventory',cid,s['status'],len(s['upload_ids']),flush=True)
    to_resolve=set(OWN_OLDER)
    for s in samples:to_resolve.update(s['upload_ids'])
    raw=api.batch('videos',to_resolve,'snippet,contentDetails,statistics')
    for v in raw:
        if before_cutoff(v.get('snippet',{}).get('publishedAt')):videos[v['id']]=compact_video(v)
    targets=list(TARGETS);auto_choices=[]
    for s in samples:
        cid=s['channel']['id'] if s.get('channel') else None
        if cid in ('UC0Badcq36RBDHN-e3N1Papg','UC77PEgjHoZkdfpxcR3_k89Q'):
            v,n=choose_median([videos[i] for i in s['upload_ids'] if i in videos])
            if v:
                label=s['channel']['title']+': sampled ordinary upload selected by median'
                targets.append((v['id'],label));auto_choices.append({'channel_id':cid,'video_id':v['id'],
                   'eligible_count':n,'fallback_used':not before_timestamp(v.get('published_at'), '2026-10-23T00:00:00Z'), 'selection_rule':'nearest median views of sampled 8–60s uploads published before 2026-10-23; fallback any sampled 8–60s if none'})

    descriptions=[];thumbs=[];comment_rows=[];caption_rows=[]
    with tempfile.TemporaryDirectory(prefix='monarch-research-') as td:
        tmp=Path(td);(tmp/'thumbs').mkdir();(tmp/'subs').mkdir()
        for vid,label in targets:
            v=videos.get(vid)
            if not v or not v.get('duration_seconds'):
                descriptions.append({'video_id':vid,'label':label,'status':'missing_metadata_or_duration'});continue
            duration=v['duration_seconds']
            windows=[(0,duration,1,'entire requested duration')] if duration<=60 else [
               (0,15,1,'opening sample'),(max(0,duration//2-7),min(duration,duration//2+8),1,'middle sample'),
               (max(0,duration-15),duration,1,'ending sample')]
            if vid in OVERLAP:windows.append((0,min(5,duration),3,'independent overlapping opening'))
            for start,end,fps,windowlabel in windows:
                r=gemini_window(gkey,vid,label+' / '+windowlabel,start,end,fps)
                descriptions.append(r);print('visual',vid,windowlabel,r['status'],r.get('http_status',''),flush=True)
                time.sleep(2)
        for vid,label in targets:
            url='https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg';row={'video_id':vid,'url':url}
            try:
                with urllib.request.urlopen(url,timeout=20) as r:data=r.read();row['http_status']=r.status
                (tmp/'thumbs'/f'{vid}.jpg').write_bytes(data)
                row.update({'status':'ok','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            except urllib.error.HTTPError as exc:row.update({'status':'http_error','http_status':exc.code})
            except Exception as exc:row.update({'status':'error','error_type':type(exc).__name__})
            thumbs.append(row)
        for vid in COMMENT_TARGETS:
            obj=api.get('commentThreads',part='snippet',videoId=vid,textFormat='plainText',order='relevance',maxResults=15)
            if obj is None:
                comment_rows.append({'video_id':vid,'status':'error','http_status':api.calls[-1]['http_status'],'reason':api.calls[-1]['reason']})
            else:
                # Public comment text can identify a commenter indirectly; compute
                # aggregate counts in memory and never write individual text.
                comment_rows.append(summarize_comments(vid, obj))
        for vid in CAPTION_TARGETS:
            c=captions_probe(vid,tmp/'subs');caption_rows.append(c)
            print('captions',vid,c['status'],flush=True)
        with zipfile.ZipFile(REVIEW_ZIP,'w',compression=zipfile.ZIP_DEFLATED) as z:
            # Only thumbnails are transferable for visual review; do not copy
            # any downloaded caption files into the GitHub blob receipt.
            for p in sorted((tmp/'thumbs').glob('*')):
                if p.is_file():z.write(p,p.relative_to(tmp))

    follow={
      'method':'Public YouTube Data API metadata and deliberately selected channel samples; Gemini YouTube input generates visual descriptions of sampled windows. Descriptions are unverified model inferences, not decoded frames, not human playback, not exact cuts or scripts. API does not reveal retention, audience, RPM, or growth.',
      'trusted_session_date':'2026-11-05','trusted_publication_cutoff_exclusive':'2026-11-06T00:00:00Z',
      'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'server_dates_distinct':sorted(set(api.server_dates)),
      'channel_samples':samples,'videos':list({i:videos[i] for i in to_resolve if i in videos}.values()),
      'selected_targets':[{'video_id':v,'label':l} for v,l in targets],'automatic_choices':auto_choices,
      'visual_model':MODEL,'visual_descriptions':descriptions,'thumbnail_receipts':thumbs,
      'comments_sample':comment_rows,'caption_attempts':caption_rows,'api_call_receipts':api.calls,
      'review_zip_sha256':hashlib.sha256(REVIEW_ZIP.read_bytes()).hexdigest(),
    }
    META_OUT.write_text(json.dumps(follow,indent=2,ensure_ascii=False)+'\n')
    print('RESULT',len(samples),'inventories;',len(descriptions),'visual windows;',
          sum(d['status']=='ok' for d in descriptions),'visual success;',
          sum(t['status']=='ok' for t in thumbs),'thumbnails;',len(caption_rows),'caption attempts',flush=True)

if __name__=='__main__':main()
