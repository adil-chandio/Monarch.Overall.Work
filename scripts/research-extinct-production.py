"""Public production-craft evidence. No cookies, DRM workarounds, or auth/geo bypass.
Publisher streams are temporary research inputs, never assets for our film.
Keep derived measurements and small critical-review contact sheets, NOT full videos/audio/scripts.
A decoded track is not a claim that a human watched or listened to it.
"""
import concurrent.futures,datetime,hashlib,json,os,re,subprocess,sys,tempfile,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
OUT=ROOT/'docs/research/extinct-production-study/evidence';OUT.mkdir(parents=True,exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
PBS=[('dna','Can We Get DNA From Fossils?','can-we-get-dna-from-fossils-zjwrun'),('whales','When Whales Walked','when-whales-walked-jjfimk'),('dodo','We Were Wrong About The Dodo','we-were-wrong-about-the-dodo-w98vvk'),('cousins','Our Most Mysterious Extinct Cousins','our-most-mysterious-extinct-cousins-jj1kmf'),('rainforests','When the Rainforests Collapsed','when-the-rainforests-collapsed-tholej'),('oxygen','That Time Oxygen Almost Killed Everything','that-time-oxygen-almost-killed-everything-cnzweg'),('reef','The Rise and Fall of an Ancient Reef','the-rise-and-fall-of-an-ancient-reef-twowy2'),('survivors','Who Survived the Great Dying','who-survived-the-great-dying-and-why-life-and-death-on-pangea-pzs3ev')]
def scrub(s):
 s=re.sub(r'https?://\S+','[URL]',str(s));return s[-1600:]
def run(args,timeout=160):return subprocess.run(args,capture_output=True,text=True,timeout=timeout)
def probe(case):
 key,title,slug=case;url='https://www.pbs.org/video/'+slug+'/'
 row={'key':key,'title':title,'source_url':url,'route':'normal public publisher extractor','status':'unavailable','human_full_video_watched':False,'human_audio_listened':False}
 with tempfile.TemporaryDirectory() as folder:
  tmp=Path(folder)
  try:
   p=run([sys.executable,'-m','yt_dlp','--skip-download','--dump-single-json','--no-playlist','--socket-timeout','15','--retries','0','--extractor-retries','0',url])
   if p.returncode:row['diagnostic']=scrub(p.stderr);return row
   info=json.loads(p.stdout);row['publisher_media_id']=info.get('id');row['duration_seconds']=info.get('duration');row['edition']='Publisher cut; not assumed identical to a YouTube upload'
   if info.get('is_live'):row['diagnostic']='Live media excluded';return row
   formats=[f for f in info.get('formats',[]) if f.get('url') and f.get('vcodec')!='none' and not f.get('has_drm') and (f.get('height') or 0)<=480]
   formats.sort(key=lambda f:(abs((f.get('height') or 360)-360),f.get('tbr') or 0))
   if not formats:row['diagnostic']='No non-DRM public review format exposed';return row
   f=formats[0];duration=float(info.get('duration') or 0)
   if not 120<=duration<=1900:row['diagnostic']='Unknown or out-of-bounds duration';return row
   media=tmp/'review.mp4'
   p=run([FF,'-y','-loglevel','error','-i',f['url'],'-t',str(duration),'-map','0:v:0','-map','0:a:0?','-vf','scale=480:-2','-c:v','libx264','-preset','veryfast','-crf','27','-c:a','aac','-b:a','64k',str(media)],timeout=360)
   if p.returncode:row['diagnostic']=scrub(p.stderr);return row
   p=run([FF,'-hide_banner','-i',str(media),'-vf',"select='gt(scene,0.27)',showinfo",'-an','-f','null','-'],timeout=120)
   if p.returncode:row['diagnostic']='Full visual decode failed: '+scrub(p.stderr);return row
   row.update(status='publisher_media_decoded',full_visual_decode_checked=True,review_resolution='480px wide temporary decode',scene_change_candidates=[float(x) for x in re.findall(r'pts_time:([\d.]+)',p.stderr)],measurement_limits='Scene-change threshold is not a manual cut count or visual quality score. Contact sheets are sparse review quotations, not continuous-motion playback.')
   times=sorted(set([.5,2,5,9,15,24,35,50]+[round(duration*x,2) for x in [.16,.24,.32,.40,.48,.56,.64,.72,.80,.88,.94]]))
   for block in range(0,len(times),12):
    selected=times[block:block+12];sheet=Image.new('RGB',(1280,3*206),(13,21,27));draw=ImageDraw.Draw(sheet)
    for j,t in enumerate(selected):
     target=tmp/'frame.jpg';p=run([FF,'-y','-v','error','-ss',str(t),'-i',str(media),'-frames:v','1','-vf','scale=320:180',str(target)])
     if p.returncode:continue
     x,y=(j%4)*320,(j//4)*206;sheet.paste(Image.open(target).convert('RGB'),(x,y));draw.text((x+6,y+184),f'{key} | {t:.2f}s',fill='white')
    sheet.save(OUT/f'{key}-review-{block//12+1}.jpg',quality=85)
   row['sampled_frame_times']=times
   # A dense early micro-sequence distinguishes a still from sampled subject/graphic motion.
   dense=[15+i*.2 for i in range(12)];sheet=Image.new('RGB',(1280,618),(13,21,27));draw=ImageDraw.Draw(sheet)
   for j,t in enumerate(dense):
    target=tmp/'motion.jpg';p=run([FF,'-y','-v','error','-ss',str(t),'-i',str(media),'-frames:v','1','-vf','scale=320:180',str(target)])
    if p.returncode:continue
    x,y=(j%4)*320,(j//4)*206;sheet.paste(Image.open(target).convert('RGB'),(x,y));draw.text((x+6,y+184),f'{t:.2f}s',fill='white')
   sheet.save(OUT/f'{key}-motion-15s.jpg',quality=85);row['dense_motion_times']=dense
   audio=run([FF,'-hide_banner','-i',str(media),'-vn','-af','ebur128=peak=true','-f','null','-'],timeout=120)
   audio_text=audio.stderr
   row['audio_measurement']={'decode_exit':audio.returncode,'summary':audio_text[audio_text.rfind('Summary:'):][-1700:] if 'Summary:' in audio_text else 'No EBU summary','limits':'Mixed-track measurement only. Does not separate voice, music or SFX; no human listening or subjective sound-quality claim.'}
   row['review_images']=[p.name for p in OUT.glob(key+'-*.jpg')]
  except Exception as e:row['diagnostic']=scrub(e)
 return row

def metadata():
 from yt_intel import client
 out={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'public metrics, not playback or private retention','videos':[],'searches':[],'errors':[]}
 ids=['nAWpLtG-kNs','SDs41Ke3v4Q','qrfhhZ-Wvmk','eWu92oXtxsw','fKizW6NlnoA','G2qpBEmUOYk','5QExdZCvdgE','B5Lmnh_BHOU','uFk0mgljtns']
 if not client.API_KEY:out['status']='no_api_key';return out
 for q in ['Kurzgesagt dinosaur asteroid extinction','Kurzgesagt immune system animation','Vox Why this black hole photo is such a big deal','TED Ed ancient DNA extinction animation']:
  try:
   d=client._api('search',{'part':'snippet','q':q,'type':'video','maxResults':5,'relevanceLanguage':'en'},'search');hits=[{'id':r['id']['videoId'],'title':r['snippet']['title'],'channel':r['snippet']['channelTitle']} for r in d.get('items',[]) if r.get('id',{}).get('videoId')];out['searches'].append({'query':q,'hits':hits});ids.extend(h['id'] for h in hits)
  except Exception as e:out['errors'].append(scrub(e))
 try:out['videos']=client.videos(list(dict.fromkeys(ids))).items
 except Exception as e:out['errors'].append(scrub(e))
 out['status']='retrieved' if out['videos'] else 'unavailable';return out
if __name__=='__main__':
 (OUT/'metadata.json').write_text(json.dumps(metadata(),indent=2)+'\n')
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Eight purposively chosen publisher editions plus bounded YouTube metadata discovery; not an exhaustive viral AV study','copyright':'Temporary media deleted after derivative measurements; review images are critical-study quotations, never film assets','cases':[]}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for row in pool.map(probe,PBS):
   report['cases'].append(row);print(row['key'],row['status'],flush=True);(OUT/'retrieval.json').write_text(json.dumps(report,indent=2)+'\n')
 # One new ordinary YouTube retrieval attempt for the creator's process explainer, not the already-blocked four niche videos.
 try:
  p=run([sys.executable,'-m','yt_dlp','--skip-download','--dump-single-json','--no-playlist','--socket-timeout','12','--retries','0','--extractor-retries','0','https://www.youtube.com/watch?v=uFk0mgljtns'],timeout=75)
  r={'source_url':'https://www.youtube.com/watch?v=uFk0mgljtns','route':'ordinary public extractor, no cookies','playback_reviewed':False,'status':'metadata_resolved' if p.returncode==0 else 'unavailable','diagnostic':scrub(p.stderr) if p.returncode else 'Resolution alone is not visual/audio inspection'}
 except Exception as e:r={'status':'unavailable','diagnostic':scrub(e),'playback_reviewed':False}
 (OUT/'youtube-access.json').write_text(json.dumps(r,indent=2)+'\n')
