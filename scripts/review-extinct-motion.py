#!/usr/bin/env python3
"""Public opening-media inspection. Never equate metadata with playback.
Private temporary excerpts are not committed or reused in production.
"""
import datetime,json,os,pathlib,subprocess,tempfile
from PIL import Image,ImageDraw
OUT=pathlib.Path('docs/research/data/extinct-motion-review');OUT.mkdir(parents=True,exist_ok=True)
CASES=[('Fossil','nAWpLtG-kNs'),('BlackWater','SDs41Ke3v4Q'),('BeyondTheBlue','qrfhhZ-Wvmk'),('Vividen','td2GgN6lrWE')]
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Purposive English shortlist from previous API sample; try first 35 seconds only. Not a full-film review, not geography/retention evidence. Images here are review quotations, not production assets.','cases':[]}
for channel,vid in CASES:
 r={'channel':channel,'video_id':vid,'url':f'https://www.youtube.com/watch?v={vid}','status':'unavailable'}
 with tempfile.TemporaryDirectory() as tmp:
  cmd=['yt-dlp','--no-playlist','--socket-timeout','15','--retries','0','--extractor-retries','0','--js-runtimes','node','--write-info-json','--no-write-thumbnail','-f','worst[ext=mp4]/worst','--download-sections','*0-35','--force-keyframes-at-cuts','-o',tmp+'/sample.%(ext)s',r['url']]
  try:
   p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
   r['extractor_exit']=p.returncode
   # No cookies/credentials are used. Store only public diagnostic messages, no signed media URLs.
   r['diagnostic']='\n'.join(x for x in p.stderr.splitlines() if 'ERROR:' in x or 'WARNING:' in x)[-1800:]
   videos=[x for x in pathlib.Path(tmp).glob('sample.*') if x.suffix in ['.mp4','.webm','.mkv']]
   if videos:
    clip=videos[0]
    dec=subprocess.run(['ffmpeg','-v','error','-i',str(clip),'-f','null','-'],capture_output=True,text=True)
    if dec.returncode:raise RuntimeError('sample decode failed')
    times=[0.5,2,4,7,10,14,19,24,29,33]
    sheet=Image.new('RGB',(1600,2*244),(9,15,19));d=ImageDraw.Draw(sheet);frames=[]
    for i,t in enumerate(times):
     f=pathlib.Path(tmp)/f'{i}.jpg'
     subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(clip),'-frames:v','1','-vf','scale=320:180',str(f)],check=True)
     if f.exists():
      sheet.paste(Image.open(f),(i%5*320,i//5*244));d.text((i%5*320+8,i//5*244+190),f'{channel} | {t:.1f}s',fill='white');frames.append(t)
    sheet.save(OUT/f'{vid}-opening-review.jpg',quality=88)
    scene=subprocess.run(['ffmpeg','-hide_banner','-i',str(clip),'-vf',"select='gt(scene,0.30)',showinfo",'-an','-f','null','-'],capture_output=True,text=True)
    import re
    r.update(status='media_sample_decoded',sample_seconds=35,sampled_frame_times=frames,scene_change_candidate_times=[float(x) for x in re.findall(r'pts_time:([\d.]+)',scene.stderr)],limits='Scene detector candidates are not manual shot boundaries. Frames do not establish audio quality, continuous movement, or complete-film pacing.')
  except Exception as e:r['error']=str(e)[:600]
 report['cases'].append(r)
 print(channel,r['status'],flush=True)
 (OUT/'report.json').write_text(json.dumps(report,indent=2))
# Capability presence only: no secret values ever written.
(OUT/'runtime-capabilities.json').write_text(json.dumps({'kaggle_token_configured':bool(os.environ.get('KAGGLE_API_TOKEN')),'kaggle_legacy_key_configured':bool(os.environ.get('KAGGLE_KEY')),'kaggle_compali_slot_configured':bool(os.environ.get('KAGGLE_COMPALI')),'note':'Presence is not a successful login, active GPU allocation, free quota, or usable model licence.'},indent=2))
