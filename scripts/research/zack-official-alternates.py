"""Bounded normal-public access to publisher-linked alternate platforms.
No authentication workarounds. Originals/edition equivalence require separate checks.
No production; downloaded third-party media is temporary and never committed.
"""
import datetime,json,os,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/research/zack-original-access';OUT.mkdir(parents=True,exist_ok=True)
CASES=[
 ('facebook','https://www.facebook.com/zackdfilms/videos/what-is-a-jerboa-/2330611454420496/',False),
 ('tiktok','https://www.tiktok.com/@thezackdfilms',True),
 ('instagram','https://www.instagram.com/zackdfilms/',True)]
if os.environ.get('ALTERNATE_X_URL'):CASES.append(('x',os.environ['ALTERNATE_X_URL'],False))
def clean(s):return re.sub(r'https?://\S+','[URL]',str(s))[-2200:]
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production_hold':True,
 'publisher_link_evidence':{'url':'https://linktr.ee/zackdfilmsofficial','observed_links':['https://www.facebook.com/zackdfilms','https://www.tiktok.com/@thezackdfilms','https://www.instagram.com/zackdfilms','https://www.youtube.com/@zackdfilms']},
 'limits':'Publisher-linked account, alternate-platform cut; not automatically a byte-identical YouTube edition or completed AV review. Display-name-only mirrors excluded.', 'cases':[]}
for platform,url,profile in CASES:
 if os.environ.get('ALTERNATE_PLATFORM') and platform!=os.environ['ALTERNATE_PLATFORM']:continue
 row={'platform':platform,'source_url':url,'account_linked_by_publisher_landing_page':platform!='x',
      'identity_note':'X account attribution corroborated by Wikitubia and matching current YouTube/X titles; not a Linktree cross-link' if platform=='x' else 'Publisher landing-page link',
      'full_video_manually_reviewed':False,'continuous_audio_reviewed':False}
 try:
  with tempfile.TemporaryDirectory() as tmp:
   args=[sys.executable,'-m','yt_dlp','--skip-download','--dump-single-json','--socket-timeout','15','--retries','0','--extractor-retries','0','--js-runtimes','node']
   if profile:args+=['--flat-playlist','--playlist-end','10']
   else:args+=['--no-playlist']
   p=subprocess.run(args+[url],capture_output=True,text=True,timeout=100)
   if p.returncode:row.update(status='public_metadata_access_failed',diagnostic=clean(p.stderr))
   else:
    info=json.loads(p.stdout)
    if profile:
     entries=[x for x in info.get('entries',[]) if x]
     row.update(status='public_profile_entries_resolved',entries=[{k:x.get(k) for k in ['id','title','url','webpage_url','uploader','uploader_id','channel_id']} for x in entries])
     entry=next((x for x in entries if x.get('url') or x.get('webpage_url')),None)
     target=(entry.get('webpage_url') or entry.get('url')) if entry else None
    else:
     row['available_format_descriptors']=[{k:f.get(k) for k in ['format_id','width','height','vcodec','acodec','protocol','has_drm']} for f in info.get('formats',[])]
     row['metadata']={k:info.get(k) for k in ['id','title','uploader','uploader_id','channel','channel_id','duration','webpage_url']};target=url
    if target:
     row['pilot_media_url']=target
     p=subprocess.run([sys.executable,'-m','yt_dlp','--no-playlist','--no-progress','--socket-timeout','15','--retries','0','--extractor-retries','0','--js-runtimes','node','--max-filesize','100M','-f','bestvideo[width<=?1080]+bestaudio/best[width<=?1080]','--merge-output-format','mp4','-o',tmp+'/source.%(ext)s',target],capture_output=True,text=True,timeout=120)
     if p.returncode:row.update(status='public_media_access_failed',diagnostic=clean(p.stderr))
     else:
      sources=[x for x in Path(tmp).glob('source.*') if x.suffix in ['.mp4','.webm','.mkv']]
      if len(sources)!=1:row['status']='no_unique_media_file'
      else:
       source=sources[0]
       probe=subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(source)],capture_output=True,text=True,timeout=90)
       row['probe_exit']=probe.returncode
       if probe.returncode:row.update(status='probe_failed',diagnostic=clean(probe.stderr))
       else:
        data=json.loads(probe.stdout);row['streams']=[{k:s.get(k) for k in ['codec_type','codec_name','width','height','avg_frame_rate','nb_read_frames','duration','sample_rate','channels']} for s in data.get('streams',[])]
        d=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(source),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,timeout=90)
        row.update(status='actual_av_downloaded_and_decoded' if d.returncode==0 else 'av_decode_failed',decode_exit=d.returncode,diagnostic=clean(d.stderr),bytes=source.stat().st_size)
        if d.returncode==0:
         # Derivative pack remains an Actions artifact, not published raw footage.
         evidence=ROOT/'.cache/zack-alternate-evidence'/platform;evidence.mkdir(parents=True,exist_ok=True)
         subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vf','fps=4,scale=216:-2,tile=5x5','-an',str(evidence/'samples-%03d.jpg')],check=True,timeout=90)
         (evidence/'identity-and-decode.json').write_text(json.dumps(row,indent=2)+'\n')
    elif profile:row['status']='no_public_profile_video_entries'
 except Exception as e:row.update(status='test_error',diagnostic=clean(type(e).__name__+': '+str(e)))
 report['cases'].append(row);print(platform,row['status'],flush=True)
 (OUT/os.environ.get('ALTERNATE_REPORT','official-alternate-probe.json')).write_text(json.dumps(report,indent=2)+'\n')
