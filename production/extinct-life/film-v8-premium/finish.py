"""Native shard typography, unchanged approved voice, attributed score, soft event mix and encoded QC."""
import json,sys,re,subprocess,wave,hashlib,urllib.request,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
R=Path.cwd();B=R/'production/extinct-life/film-v8-premium';C=R/'.cache/extinct-v8';C.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();SR=48000;N=61*SR
m=json.loads((B.parent/'film-v7-full/schedule.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run(args):
 p=subprocess.run([FF,'-hide_banner','-y',*map(str,args)],capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-6000:])
 return p

def pcm(p):
 r=run(['-i',p,'-f','f32le','-ar',SR,'-ac',2,'pipe:1']);return np.frombuffer(r.stdout,'<f4').reshape(-1,2).copy()

def wav(p,x):
 with wave.open(str(p),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-.999,.999)*32767).astype('<i2').tobytes())

def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
LABELS=[(0,183,'A LOST WORLD','Illustrative reconstruction'),(183,403,'INCOMPLETE FRAGMENTS','Conceptual molecular view • not to scale'),(403,772,'NORTHERN GREENLAND','Present-day environment • illustrative'),(772,1112,'AN ANCIENT DEPOSIT','Kap København Formation • schematic exposure'),(1112,1393,'TRACES, NOT WHOLE GENOMES','Conceptual molecular view • not to scale'),(1393,1600,'FROM SEDIMENT TO EVIDENCE','Illustrative laboratory scene'),(1600,1830,'LIFE LEAVES MATERIAL BEHIND','Illustrative reconstruction • no literal shedding rates')]

def captions():
 rows=[]
 for c in m['chapters'][:2]:
  for s in c['sentences']:
   st=c['start_frame']/30+s['start'];en=c['start_frame']/30+s['end']
   if st>=61:continue
   # Preserve exact approved wording; split at word boundaries only for legibility.
   words=s['text'].split();groups=[words[i:i+11] for i in range(0,len(words),11)]
   aligned=[w for w in c['word_alignment'] if w['start']>=s['start']-.025 and w['start']<s['end']]
   norm=lambda x:re.sub(r"[^a-z0-9']",'',x.lower())
   if [norm(w['word']) for w in aligned]==[norm(w) for w in words]:
    for j,g in enumerate(groups):
     first=j*11;last=first+len(g)-1
     rows.append((c['start_frame']/30+aligned[first]['start'],min(61,c['start_frame']/30+aligned[last]['end']),' '.join(g)))
   else:
    # Prefer faithful complete-sentence timing over inventing word timings.
    rows.append((st,min(61,en),s['text']))
 return rows
CAPTIONS=captions()

def typography(p,frame):
 im=Image.open(p).convert('RGBA');W,H=im.size;layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);scale=W/1920;f=lambda size:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',round(size*scale));bold=lambda size:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',round(size*scale));t=frame/30
 start,end,title,sub=next(x for x in LABELS if x[0]<=frame<x[1]);opacity=round(255*smooth((frame-start)/12));x=round(86*scale);y=round(74*scale);shift=round(8*scale*(1-smooth((frame-start)/12)))
 d.rounded_rectangle((x-20*scale,y-18*scale,W*.68,y+94*scale),radius=10*scale,fill=(10,20,24,round(opacity*.58)));d.rectangle((x-20*scale,y-18*scale,x-16*scale,y+94*scale),fill=(214,174,104,opacity));d.text((x,y+shift),title,font=bold(32),fill=(244,239,224,opacity));d.text((x,y+48*scale+shift),sub,font=f(25),fill=(211,218,214,opacity))
 for st,en,text in CAPTIONS:
  if st<=t<en:
   font=f(40);lines=[];line=''
   for w in text.split():
    candidate=(line+' '+w).strip()
    if d.textlength(candidate,font=font)>W*.79 and line:lines.append(line);line=w
    else:line=candidate
   if line:lines.append(line)
   yy=H-round(100*scale)-len(lines)*round(49*scale)
   for line in lines:
    width=d.textlength(line,font=font);xx=(W-width)/2;d.rounded_rectangle((xx-20*scale,yy-8*scale,xx+width+20*scale,yy+51*scale),radius=7*scale,fill=(7,14,19,175));d.text((xx,yy),line,font=font,fill=(248,247,239,255),stroke_width=max(1,round(scale)),stroke_fill=(0,0,0,170));yy+=round(49*scale)
 im=Image.alpha_composite(im,layer).convert('RGB');im.save(p)

def shard(part):
 start=part*30;end=start+30
 for n in range(start,end):
  p=C/'frames'/f'{n:05}.png';assert p.exists(),p;typography(p,n)
 run(['-v','warning','-framerate',30,'-start_number',start,'-i',C/'frames/%05d.png','-frames:v',30,'-an','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709','-c:v','libx264','-preset','medium','-crf',16,'-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',C/f'part-{part:02}.mp4'])

def levels(p):
 z=run(['-i',p,'-vn','-af','loudnorm=I=-16:TP=-2.5:LRA=9:print_format=json','-f','null','-']).stderr.decode();return json.loads(z[z.rfind('{'):z.rfind('}')+1])

def audio():
 chunks=[]
 for c in m['chapters'][:2]:
  p=R/c['voice'];assert sha(p)==c['voice_sha256'];v=pcm(p);size=c['frames']*1600;assert len(v)<=size;chunks.append(np.pad(v,((0,size-len(v)),(0,0))))
 voice=np.concatenate(chunks)[:N];assert len(voice)==N;wav(C/'voice-unchanged.wav',voice)
 music=C/'sb_hiraeth.mp3'
 if not music.exists():
  req=urllib.request.Request('https://www.scottbuckley.com.au/library/wp-content/uploads/2020/06/sb_hiraeth.mp3',headers={'User-Agent':'Monarch attributed documentary production'})
  with urllib.request.urlopen(req,timeout=120) as r:music.write_bytes(r.read(30*1024*1024))
 run(['-v','warning','-i',music,'-t',61,'-af','highpass=f=40,lowpass=f=11500,equalizer=f=2500:t=q:w=0.8:g=-1.5','-ar',SR,C/'score-shaped.wav']);score=pcm(C/'score-shaped.wav');assert len(score)==N
 # Narration-priority envelope, smoothed in non-overlapping 20 ms windows and interpolated.
 t=np.arange(N)/SR;env=np.sqrt(np.mean(voice.reshape(-1,960,2)**2,axis=(1,2)));env=np.convolve(env,np.ones(9)/9,'same');env=np.interp(t,np.arange(len(env))*.02,env);duck=1-.72*smooth(env/.09);score*=.022/max(1e-7,float(np.sqrt(np.mean(score**2))));score*=duck[:,None]*(smooth(t/2)*smooth((61-t)/2.1))[:,None]
 rng=np.random.default_rng(81042);foley=np.zeros((N,2),np.float32);cues=[]
 def event(when,duration,level,kind):
  n=round(duration*SR);tt=np.arange(n)/SR;noise=rng.normal(0,1,n);kernel=np.ones(91)/91;soft=np.convolve(noise,kernel,'same');soft/=max(.001,np.max(np.abs(soft)));en=smooth(tt/.08)*smooth((duration-tt)/.22)
  if kind=='soil':soft=.6*soft+.4*np.sin(math.tau*68*tt)*np.exp(-tt*7)
  soft*=en*level;at=round(when*SR);stop=min(N,at+n);pan=.12*math.sin(when);foley[at:stop,0]+=soft[:stop-at]*(1-pan);foley[at:stop,1]+=soft[:stop-at]*(1+pan);cues.append({'time':when,'duration':duration,'kind':kind,'synthetic_not_field_recording':True})
 event(2.4,.9,.022,'soil');event(7.1,2,.012,'mineral');event(10.5,1.4,.009,'mineral');event(13.45,11.6,.009,'wind');event(27,3.2,.009,'carriage');event(38,4,.009,'mineral');event(47.1,3.9,.009,'receiver');event(56.4,3.5,.012,'leaf-water')
 wav(C/'foley-unshaped.wav',foley);run(['-v','warning','-i',C/'foley-unshaped.wav','-af','highpass=f=65,lowpass=f=3500',C/'foley.wav']);foley=pcm(C/'foley.wav');foley*=smooth(t/.15)[:,None]*smooth((61-t)/.2)[:,None];mix=voice+score+foley;mix*=min(1,.85/max(1e-8,float(np.max(np.abs(mix)))));wav(C/'premaster.wav',mix)
 q=levels(C/'premaster.wav');filt=f"loudnorm=I=-16:TP=-2.5:LRA=9:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}:linear=true:print_format=json"
 run(['-v','warning','-i',C/'premaster.wav','-af',filt,'-ar',SR,C/'mix.wav'])
 return {'voice_speed_changed':False,'voice_assets':[{'path':c['voice'],'sha256':c['voice_sha256']} for c in m['chapters'][:2]],'music_source_sha256':sha(music),'synthetic_foley_cues':cues,'foley_peak_dbfs':float(20*np.log10(max(1e-9,np.max(np.abs(foley))))),'human_comfort_certified':False,'mix_sha256':sha(C/'mix.wav')}

def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def assemble():
 parts=[C/f'part-{n:02}.mp4' for n in range(61)];assert all(p.exists() for p in parts);(C/'concat.txt').write_text(''.join(f"file '{p.name}'\n" for p in parts));run(['-v','warning','-f','concat','-safe',0,'-i',C/'concat.txt','-c','copy',C/'picture.mp4']);aq=json.loads((C/'audio-QC.json').read_text()) if (C/'audio-QC.json').exists() else audio();assert sha(C/'mix.wav')==aq['mix_sha256'];out=C/'Extinct_Life_V8_Premium_Opening_English_1080p.mp4'
 run(['-v','warning','-i',C/'picture.mp4','-i',C/'mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar',SR,'-t',61,'-movflags','+faststart','-metadata',"comment=Illustrative reconstruction and conceptual science models. Hiraeth by Scott Buckley, CC-BY 4.0, www.scottbuckley.com.au",out])
 measured=levels(out);assert float(measured['input_tp'])<-2,measured
 check=run(['-v','info','-i',out,'-map','0:v:0','-vf','showinfo','-an','-f','null','-']).stderr.decode();ns=re.findall(r'Parsed_showinfo_\d+.*?n:\s*(\d+).*?s:(\d+x\d+)',check);assert len(ns)==1830,(len(ns),check[-1000:]);assert all(size=='1920x1080' for _,size in ns)
 q={'status':'Fresh native development film; owner creative review pending','engine':'Blender 4.2 Cycles CPU','samples':24,'width':1920,'height':1080,'fps':30,'frames':1830,'seconds':61,'why_61_not_60':'The approved sentence “Living things shed biological material” ends at ~60.74 s. No word is cut or sped up.','sha256':sha(out),'bytes':out.stat().st_size,'full_decode':True,'old_movie_frames_used':False,'generated_image_plates_used':False,'reference_assets_copied':False,'full_film_replacement':False,'encoded_audio':measured,'audio':aq,'script_sha256':m['script_sha256'],'not_expert_validated_anatomy':True,'not_actual_field_or_molecular_footage':True,'continuous_human_watch_listen_claimed':False}
 inspect=B/'encoded-inspection';inspect.mkdir(exist_ok=True);selected=[95,300,600,980,1250,1490,1740]
 filt='select='+ '+'.join(f'eq(n\\,{n})' for n in selected)
 run(['-v','warning','-i',out,'-vf',filt,'-vsync',0,'-q:v',2,inspect/'%02d.jpg'])
 q['encoded_inspection_frames']=selected
 (B/'QC.json').write_text(json.dumps(q,indent=2)+'\n');(B/'English-v8.srt').write_text('\n'.join(f'{i}\n{stamp(st)} --> {stamp(en)}\n{text}\n' for i,(st,en,text) in enumerate(CAPTIONS,1)));print(json.dumps(q,indent=2))
if __name__=='__main__':
 if any(s.startswith('--shard=') for s in sys.argv):shard(int(next(s.split('=')[1] for s in sys.argv if s.startswith('--shard='))))
 elif '--audio-only' in sys.argv:
  q=audio();q['mix_levels']=levels(C/'mix.wav');(C/'audio-QC.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
 elif '--assemble' in sys.argv:assemble()
