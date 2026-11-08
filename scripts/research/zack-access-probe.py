"""Bounded public-original access test. Research only: no film production.
Never use cookies, proxies, spoofed clients, PO tokens or access-control workarounds.
Full third-party files remain temporary; only identity/access/decode measurements
are returned to Git. Decoding is not a claim of perceptual inspection.
"""
import datetime, hashlib, json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/research/zack-original-access'
SEEDS = ['-GyaX8xWy58', 'yGw0nhlUtkQ', 'q01zpa6Dnfc', 'HF5zZn-zrwc',
         'S76QgNDIXEY', 'ttuKeS5k4Uo', '2aykpv3njYo']
QUERIES = ['How Fossilization Works', 'How Casts Work To Heal Broken Bones', 'How A Ballpoint Pen Works']
KEY = next((os.environ.get(k) for k in ['YOUTUBE_API_KEY','YTAP1','YTAPI1','YT_KEY','YT_API_KEY'] if os.environ.get(k)), None)

def api(endpoint, **params):
    params['key'] = KEY
    try:
        with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/' + endpoint + '?' + urllib.parse.urlencode(params), timeout=25) as r:
            return json.load(r)
    except Exception as e:
        # Do not serialize exceptions containing API request URLs/keys.
        raise RuntimeError('Data API request failed: ' + type(e).__name__) from None

def public_fields(item, owner):
    s = item['snippet']
    return dict(video_id=item['id'], title=s['title'], source_url='https://www.youtube.com/watch?v='+item['id'],
                channel_id=s['channelId'], channel_title=s['channelTitle'],
                original_channel_verified=s['channelId'] == owner,
                published_at=s.get('publishedAt'), duration_iso=item.get('contentDetails',{}).get('duration'),
                public_views=item.get('statistics',{}).get('viewCount'),
                full_frame_manual_review=False, continuous_audio_review=False)

def clean(text):
    text = re.sub(r'https?://\S+', '[URL]', str(text))
    if KEY:
        text = text.replace(KEY, '[REDACTED]')
    return text[-1800:]

def media_test(row, folder):
    vid = row['video_id']
    p = subprocess.run([sys.executable, '-m', 'yt_dlp', '--no-playlist', '--no-progress',
        '--socket-timeout','15','--retries','0','--extractor-retries','0',
        '--max-filesize','100M','--write-info-json','--no-write-playlist-metafiles',
        '--format','bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '--merge-output-format','mp4','--output',str(folder / (vid+'.%(ext)s')),
        row['source_url']], capture_output=True, text=True, timeout=150)
    if p.returncode:
        row.update(media_status='retrieval_failed', diagnostic=clean(p.stderr))
        return
    infofile = folder / (vid+'.info.json')
    if not infofile.exists():
        row.update(media_status='no_download_identity_evidence'); return
    info = json.loads(infofile.read_text())
    row['download_channel_id'] = info.get('channel_id')
    row['download_identity_match'] = info.get('channel_id') == row.get('channel_id')
    if not row['download_identity_match']:
        row['media_status'] = 'download_identity_not_verified'; return
    candidates = [p for p in folder.glob(vid+'.*') if p.suffix in ['.mp4','.webm','.mkv'] and '.f' not in p.stem]
    if len(candidates) != 1:
        row['media_status'] = 'no_unique_complete_media'; return
    source = candidates[0]
    probe = subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(source)],capture_output=True,text=True,timeout=90)
    if probe.returncode:
        row.update(media_status='probe_failed', diagnostic=clean(probe.stderr)); return
    data=json.loads(probe.stdout)
    vs=next((s for s in data['streams'] if s['codec_type']=='video'), None)
    au=next((s for s in data['streams'] if s['codec_type']=='audio'), None)
    if not vs or not au:
        row['media_status']='missing_av_track'; return
    decode = subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(source),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,timeout=120)
    row.update(media_status='av_acquired_and_decoded' if decode.returncode==0 else 'decode_failed',
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bytes=source.stat().st_size,
        video={k:vs.get(k) for k in ['width','height','r_frame_rate','avg_frame_rate','duration','nb_read_frames','codec_name']},
        audio={k:au.get(k) for k in ['codec_name','sample_rate','channels','duration']},
        decode_exit=decode.returncode,diagnostic=clean(decode.stderr),
        retention='Temporary runner media only; no full competitor media published or used in production')
    # Retain a private-to-job review pack as an authenticated Actions artifact;
    # do not publish raw footage or a full reconstruction of frames to the public repo.
    if decode.returncode==0:
        evidence=ROOT/'.cache/zack-access-review'/vid; evidence.mkdir(parents=True, exist_ok=True)
        subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time,key_frame,pict_type','-of','csv',str(source)],stdout=(evidence/'frame-timestamps.csv').open('w'),check=True,timeout=90)
        subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vf','fps=4,scale=216:-2,tile=5x5','-an',str(evidence/'quarter-second-%03d.jpg')],check=True,timeout=90)
        (evidence/'identity-and-decode.json').write_text(json.dumps(row,indent=2)+'\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report=dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        purpose='Actual-original acquisition feasibility, NOT a completed 10-video forensic study',
        production_hold=True, requested_originals=10, public_originals=[],errors=[],
        limits=['Data API metadata is not media access','Every-frame decode is not manual visual inspection',
                'No recovered renderer, lens, rig, source frame rate, sound stems or proprietary settings claimed'])
    try:
        if not KEY: raise RuntimeError('No existing Data API key available to this workflow')
        channels=api('channels',part='id,snippet,contentDetails',forHandle='zackdfilms').get('items',[])
        if len(channels)!=1: raise RuntimeError('Canonical creator handle did not resolve uniquely')
        owner=channels[0]['id']; report['canonical_channel']={'handle':'@zackdfilms','channel_id':owner,'title':channels[0]['snippet']['title']}
        ids=list(SEEDS)
        for query in QUERIES:
            hits=api('search',part='snippet',channelId=owner,q=query,type='video',maxResults=5).get('items',[])
            match=next((h['id']['videoId'] for h in hits if h.get('id',{}).get('videoId') not in ids),None)
            if match: ids.append(match)
        items=api('videos',part='snippet,contentDetails,statistics,status',id=','.join(ids)).get('items',[])
        byid={x['id']:x for x in items}
        for vid in ids:
            if vid not in byid: continue
            row=public_fields(byid[vid],owner)
            duration=row['duration_iso'] or ''
            # Bound study to public short-form uploads, exclude unexpected long-form results.
            m=re.fullmatch(r'PT(?:(\d+)M)?(?:(\d+)S)?',duration)
            seconds=int(m.group(1) or 0)*60+int(m.group(2) or 0) if m else None
            row['duration_seconds']=seconds
            if not row['original_channel_verified'] or seconds is None or not 5<=seconds<=180:
                row['media_status']='excluded_identity_or_duration'; report['public_originals'].append(row);continue
            report['public_originals'].append(row)
        # Pilot once. Explicit bot/auth/rate-limit denial stops this route; no client/proxy/cookie bypass.
        denial=False
        with tempfile.TemporaryDirectory(prefix='zack-access-') as folder:
            for row in report['public_originals']:
                if 'media_status' in row: continue
                if denial:
                    row['media_status']='not_attempted_route_denied_on_pilot'; continue
                try: media_test(row,Path(folder))
                except Exception as e: row.update(media_status='test_error',diagnostic=clean(e))
                diagnostic=row.get('diagnostic','').lower()
                if any(s in diagnostic for s in ['not a bot','sign in','http error 429','http error 403','login required','private video']): denial=True
                print(row['video_id'],row['media_status'],flush=True)
                (OUT/'access-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    except Exception as e: report['errors'].append(clean(e))
    report['verified_original_metadata_count']=sum(r.get('original_channel_verified',False) for r in report['public_originals'])
    report['new_av_acquired_and_decoded_count']=sum(r.get('media_status')=='av_acquired_and_decoded' for r in report['public_originals'])
    (OUT/'access-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['verified_original_metadata_count','new_av_acquired_and_decoded_count','errors']}))

if __name__=='__main__': main()
