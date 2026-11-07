"""Locked full English master: composed licensed score + material foley + verified native shards."""
import hashlib,json,re,subprocess,sys,urllib.request,wave
from pathlib import Path
import numpy as np
import imageio_ffmpeg
B=Path(__file__).resolve().parent;ROOT=B.parents[2];C=ROOT/'.cache/extinct-v9';C.mkdir(parents=True,exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000
m=json.loads((B/'schedule.json').read_text());N=m['total_frames']*1600;D=m['total_frames']/30
lic=json.loads((B/'MUSIC-LICENSE.json').read_text());credit='\n'.join(t['required_credit'] for t in lic['tracks'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
 try:return subprocess.run([FF,'-y','-hide_banner','-loglevel','info',*map(str,args)],capture_output=True,text=True,check=True)
 except subprocess.CalledProcessError as e:print(e.stderr[-8000:],file=sys.stderr);raise

def wav(p,a):
 with wave.open(str(p),'wb') as w:
  w.setnchannels(a.shape[1] if a.ndim>1 else 1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-.999,.999)*32767).astype('<i2').tobytes())
def pcm(p,channels=1,limit=None,floating=False):
 if floating:
  q=C/'decode.f32';run(['-i',p,*( ['-t',limit] if limit is not None else []),'-f','f32le','-ar',SR,'-ac',channels,q]);a=np.fromfile(q,dtype='<f4');q.unlink();return a.reshape(-1,channels) if channels>1 else a
 q=C/'decode.wav';run(['-i',p,*(['-t',limit] if limit is not None else []),'-ar',SR,'-ac',channels,q])
 with wave.open(str(q)) as w:a=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 return a.reshape(-1,channels) if channels>1 else a

def levels(p):
 q=run(['-i',p,'-vn','-af','loudnorm=I=-16:TP=-2.5:LRA=9:print_format=json','-f','null','-']);return json.loads(q.stderr[q.stderr.rfind('{'):q.stderr.rfind('}')+1])

def audio():
 from full_sound import design,audit,smooth,REVISION
 voice=[]
 for c in m['chapters']:
  assert sha(ROOT/c['voice'])==c['voice_sha256'],('Approved voice asset changed',c['id'])
  a=pcm(ROOT/c['voice']);length=c['frames']*1600
  assert len(a)<=length,('Narration no longer fits locked timing: never silently speed it up',c['id'],len(a),length)
  voice.append(np.pad(a,(0,length-len(a))))
 v=np.concatenate(voice);assert len(v)==N;del voice
 wav(C/'voice.wav',v)
 if '--voice-only' in sys.argv:
  wav(C/'proof.wav',v);print('Full approved narration-only work preview; not scored final audio');return
 sources=[];tracks=[]
 for entry in lic['tracks']:
  p=C/Path(entry['official_download']).name
  if not p.exists():
   req=urllib.request.Request(entry['official_download'],headers={'User-Agent':'Monarch full documentary / attributed CC-BY use'})
   with urllib.request.urlopen(req,timeout=90) as r:
    data=r.read(35*1024*1024+1);assert len(data)<=35*1024*1024,'Unexpectedly large primary-source music response';p.write_bytes(data)
  source=pcm(p,2,floating=True);rms=float(np.sqrt(np.mean(source*source)));source_peak=float(np.max(np.abs(source)));source_gain=min(.075/max(rms,1e-7),.85/max(source_peak,1e-7));source*=source_gain;sources.append(source)
  tracks.append({'track':entry['track'],'official_download':entry['official_download'],'sha256':sha(p),'duration_seconds':len(source)/SR,'source_start_seconds':0,'float_decode_unclipped_peak':source_peak,'level_matching_gain':source_gain,'peak_after_matching':float(np.max(np.abs(source))),'license':entry['license'],'required_credit':entry['required_credit']})
 split=max(D-len(sources[1])/SR+1.05,min(218.666667,len(sources[0])/SR-1.05))
 assert split+1<=len(sources[0])/SR and D-split+1<=len(sources[1])/SR,'Licensed music too short: no unapproved looping or procedural substitute'
 t=np.arange(N,dtype=np.float32)/SR;first_end=min(N,round((split+1)*SR));second_start=max(0,round((split-1)*SR));cross=smooth((t-(split-1))/2)
 score=np.zeros((N,2),np.float32);score[:first_end]+=sources[0][:first_end]*np.cos(np.pi*.5*cross[:first_end])[:,None];score[second_start:]+=sources[1][:N-second_start]*np.sin(np.pi*.5*cross[second_start:])[:,None]
 tracks[0].update(timeline_start_seconds=0,source_excerpt_end_seconds=first_end/SR);tracks[1].update(timeline_start_seconds=second_start/SR,source_excerpt_end_seconds=(N-second_start)/SR)
 del sources,source,cross
 score_peak=float(np.max(np.abs(score)));score_safety=min(1.,.90/max(score_peak,1e-7));score*=score_safety
 cues=json.loads((B.parent/'film-v6-motion/action-cues.json').read_text());foley,env,report=design(v,m,cues)
 wav(C/'foley-unfiltered.wav',foley);del foley
 run(['-i',C/'foley-unfiltered.wav','-af','highpass=f=70,lowpass=f=4200,equalizer=f=3200:t=q:w=0.7:g=-3',C/'foley-shaped.wav'])
 foley=pcm(C/'foley-shaped.wav',2);assert len(foley)==N
 edge=480;fade=smooth(np.linspace(0,1,edge));foley[:edge]*=fade[:,None];foley[-edge:]*=fade[::-1,None]
 pre=audit(foley,v);gain=1.
 if pre['voiced_region_foley_relative_db'] is not None and pre['voiced_region_foley_relative_db'] < -30:gain=min(8.,10**((-28-pre['voiced_region_foley_relative_db'])/20),.08/max(1e-9,float(np.max(np.abs(foley)))))
 foley*=gain;report['bus_gain']=gain;report['measured']=audit(foley,v);check=report['measured']
 assert check['peak_dbfs']<=-18 and check['maximum_sample_step']<.01 and check['energy_fraction_above_6khz']<.001 and check['endpoints_zero'],check
 if check['voiced_region_foley_relative_db'] is not None:assert check['voiced_region_foley_relative_db']<=-16,check
 wav(C/'score-source.wav',score);del score
 run(['-i',C/'score-source.wav','-af','highpass=f=40,lowpass=f=14500,equalizer=f=2500:t=q:w=0.8:g=-1.5',C/'score-shaped.wav'])
 score=pcm(C/'score-shaped.wav',2);assert len(score)==N
 score*=.14*(1-.45*smooth(env/.065))[:,None]*(smooth(t/2.5)*smooth((D-t)/3.4))[:,None]
 mix=v[:,None]+score+foley;peak=float(np.max(np.abs(mix)));safety=min(1.,.95/max(1e-12,peak));mix*=safety
 report.update(premaster_peak_before_safety=peak,premaster_safety_gain=safety,music_sources=tracks,music_crossfade_seconds=2,music_source_audio_looped=False,music_before_eq_peak=score_peak,music_pre_eq_safety_gain=score_safety,full_master_frames=m['total_frames'],script_sha256=m['script_sha256'],voice_assets_sha256={c['id']:sha(ROOT/c['voice']) for c in m['chapters']})
 (B/'SOUND-QC.json').write_text(json.dumps(report,indent=2)+'\n');wav(C/'score-excerpt.wav',score);wav(C/'foley.wav',foley);wav(C/'mix.wav',mix)
 a=levels(C/'mix.wav');norm='loudnorm=I=-16:TP=-2.5:LRA=9:linear=true:'+':'.join(f'{k}={a[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')]);norm+=',aresample=192000,alimiter=limit=0.70:level=false:attack=5:release=80:latency=1,aresample=48000'
 run(['-i',C/'mix.wav','-af',norm,C/'proof.wav'])
 (B/'CREDITS.md').write_text('# Full-film music and scope credits\n\n'+credit+'\n\n'+'\n'.join(t['official_track_page'] for t in lic['tracks'])+'\n\nLicense: https://creativecommons.org/licenses/by/4.0/\n\nTwo non-repeating composed cue excerpts, level matching, two-second crossfade, gentle EQ, narration ducking, end fades and normalization. No endorsement or claim-free guarantee. If eventually uploaded to YouTube, both credits must appear in the description; this delivery is GitHub only.\n\nApproved full English script and voice timing unchanged. Original synthesized material foley, not recorded field audio or verified binaural ASMR. Full master candidate, not proof of ear comfort, expert anatomy or owner creative acceptance.\n')
 print('Full-master composed score and soft-material sound prepared; no human listening approval implied',flush=True)

def assemble():
 report=json.loads((B/'SOUND-QC.json').read_text());seek=json.loads((C/'seek-QC.json').read_text())
 assert report['full_master_frames']==m['total_frames'] and seek['deterministic_seek'] and seek['subject_moves_with_frozen_camera'] and not seek['page_errors']
 assert len({s['sequence'] for s in seek['samples']})==len(m['sequences']),'Every full-film stage must be natively sampled'
 reports=sorted([json.loads(p.read_text()) for p in C.glob('render-*.json')],key=lambda r:r['from']);cursor=0;parts=[]
 for r in reports:
  assert r['from']==cursor and r['frames']==r['to']-r['from'] and not r['page_errors'],r
  cursor=r['to'];p=C/f'part-{r["from"]}-{r["to"]}.mp4';assert p.exists();parts.append(p)
 assert cursor==m['total_frames'],(cursor,m['total_frames'])
 lst=C/'concat.txt';lst.write_text(''.join("file '"+str(p)+"'\n" for p in parts));out=C/'Extinct_Life_V9_Full_English_1080p.mp4'
 run(['-f','concat','-safe','0','-i',lst,'-i',C/'proof.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar',SR,'-metadata','title=Extinct Life — The Lost World Inside a Handful of Dirt','-metadata','comment='+credit+' | https://creativecommons.org/licenses/by/4.0/','-t',f'{D:.9f}','-movflags','+faststart',out])
 encoded=levels(out);assert abs(float(encoded['input_i'])+16)<1.1 and float(encoded['input_tp'])<=-1.5,encoded
 q=run(['-i',out,'-map','0:v:0','-progress','pipe:1','-nostats','-f','null','-']);decoded=int(re.findall(r'^frame=(\d+)',q.stdout,re.M)[-1]);assert decoded==m['total_frames'] and '1920x1080' in q.stderr
 qc={'status':'FULL ENGLISH MASTER RENDERED — OWNER CREATIVE REVIEW PENDING','width':1920,'height':1080,'fps':30,'native_frames':decoded,'duration_seconds':D,'script_sha256':m['script_sha256'],'voice_speed_changed':False,'new_voice_generated':False,'selected_excerpt':False,'generated_scene_images_used':False,'old_rendered_movie_used':False,'large_caption_panels':False,'scene_linked_animated_text':True,'text_rendering':'Crisp object-projected labels, no upper caption cards','engine':'Three.js native geometry and original Blender-authored GLB sculpts','continuous_3d_stages':len(m['sequences']),'coverage_map':json.loads((B/'coverage.json').read_text()),'composed_music':lic,'music_downloads':report['music_sources'],'sound_revision':report['revision'],'sound_audit':report['measured'],'foley':'Soft synthesized material-specific non-tonal sound; not recorded field sound or verified binaural ASMR','encoded_audio':encoded,'sha256':sha(out),'bytes':out.stat().st_size,'full_decode':True,'full_film_complete':True,'full_film_creative_acceptance':False,'human_full_watch_listen_claimed':False,'biological_accuracy_expert_validated':False,'owner_creative_approval':False,'limitations':['Stylized procedural 3D; no expert anatomical validation, field footage or fluid simulation.','Science setups are conceptual, not actual reads, calibrated molecular motion or specimen counts.','Technical and sampled visual QC is not uninterrupted human watching/listening or a promise of ASMR/enjoyment.']}
 inspect=B/'encoded-inspection';inspect.mkdir(exist_ok=True);selected=[95,300,600,980,1490,2100,2800,3400,4200,5200,6500,7600,8800,9900,11000,12000,13000]
 filt="select='"+'+'.join(f'eq(n,{n})' for n in selected)+"'"
 run(['-i',out,'-vf',filt,'-vsync',0,'-q:v',2,inspect/'%02d.jpg'])
 qc['encoded_inspection_frames']=selected
 (B/'QC.json').write_text(json.dumps(qc,indent=2)+'\n');print(json.dumps(qc,indent=2))
if __name__=='__main__':
 if '--assemble-only' not in sys.argv:audio()
 if '--voice-only' not in sys.argv and '--audio-only' not in sys.argv:assemble()
