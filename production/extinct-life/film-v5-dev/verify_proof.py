"""Verify/package the development excerpt. No claim of subjective quality or listening."""
import hashlib,json,re,subprocess,textwrap,zipfile
from pathlib import Path
from make_proof import B,OUT,STYLE,FF,START,END,N,manifest,graphic,beats
VIDEO=OUT/'Extinct_Life_V5_Graphics_Motion_Development.mp4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=subprocess.run([FF,'-hide_banner','-i',str(VIDEO),'-map','0:v:0','-an','-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
counts=re.findall(r'frame=(\d+)',p.stdout);assert counts and int(counts[-1])==N,(counts,N)
a=subprocess.run([FF,'-hide_banner','-i',str(VIDEO),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True);summary=a.stderr[a.stderr.rfind('Summary:'):]
i=float(re.search(r'I:\s+(-?[\d.]+) LUFS',summary)[1]);peak=float(re.search(r'Peak:\s+(-?[\d.]+)',summary)[1]);assert -17<=i<=-15 and peak<=-1.5,(i,peak)
for ident in ['V5-19','V5-22','V5-24','V5-26']:
 r=next(r for r in beats if r['id']==ident);f=r['start_frame']+20;a=graphic(f);assert a.tobytes()==graphic(f).tobytes();assert a.tobytes()!=graphic(min(r['end_frame']-1,f+70)).tobytes()
q=json.loads((B/'PROOF-QC.json').read_text());q.update(encoded_integrated_lufs=i,encoded_true_peak_dbfs=peak,encoded_audio_check_passed=True,decoded_native_frames=N,motion_seek_checks='four representative tasks nonstatic and deterministic',visual_inspection='Six style frames, representative motion states and encoded frames; not full continuous playback',visual_corrections=['Reference connectors moved out of label/card paths','Receiving extraction tube is open; no delivery through a closed cap'],first_render_issue='Initial selected-range boundary lookup failed; guard fixed and complete proof rerendered',video_sha256=sha(VIDEO),video_bytes=VIDEO.stat().st_size);(B/'PROOF-QC.json').write_text(json.dumps(q,indent=2)+'\n')
selected=['01-living-world-designed.jpg','02-location.jpg','03-mineral.jpg','04-reference.jpg','05-community-designed.jpg','06-record-designed.jpg']
from PIL import Image
for name in selected:assert Image.open(STYLE/name).size==(1920,1080),name
assets=[]
for name in ['01-living-world.png','05-community.png','06-record.png','mineral-material.png']:
 assets.append({'file':'style/'+name,'origin':'AI-generated original concept asset via image generation tool in this session','external_reference_images':False,'source_pixel_size':list(Image.open(STYLE/name).size),'sha256':sha(STYLE/name),'limitations':'Illustrative concept, not observed scientific footage, recovered exact appearance or a rigged/moving character; service terms apply; no exclusivity claim'})
ledger={'assets':assets,'geography':{'file':'geography.json','source':json.loads((B/'geography.json').read_text())['source'],'license':'Natural Earth public domain','locator':'Approximate formation-area locator, not a survey marker'},'fonts':{'family':'DejaVu Sans / DejaVu Serif, installed system fonts','license_reference':'https://dejavu-fonts.github.io/License.html'},'motion_graphics':'Original Pillow/NumPy shapes and timelines in make_proof.py','voice':[{'file':'../film-v3/voice/'+c+'.flac','sha256':sha(B.parent/'film-v3/voice'/f'{c}.flac'),'origin':'Existing owner-approved voice-02 production'} for c in ['B03','B04']],'music_sfx':'Original temporary procedural tone/contact sketches; not licensed final score or recorded foley','competitor_assets_used':False,'old_film_mp4_used':False,'purchases':[]};(B/'SOURCE-LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n')
def tc(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
subs=[]
for c in manifest['chapters']:
 for k,s in enumerate(c['sentences']):
  first=c['start_frame']/30+s['start'];end=c['start_frame']/30+(c['sentences'][k+1]['start'] if k+1<len(c['sentences']) else c['frames']/30)
  if end<=START/30 or first>=END/30:continue
  start=max(0,first-START/30);finish=min(N/30,end-START/30);subs.append(f'{len(subs)+1}\n{tc(start)} --> {tc(finish)}\n'+textwrap.fill(s['text'],width=52)+'\n')
srt=B/'English-development.srt';srt.write_text('\n'.join(subs))
with zipfile.ZipFile(OUT/'Extinct_Life_V5_Six_Style_Frames.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in selected:z.write(STYLE/name,name)
 for name in ['README.md','PROOF-QC.json','SOURCE-LEDGER.json']:z.write(B/name,name)
print(json.dumps({'frames':N,'lufs':i,'true_peak':peak,'style_frames':len(selected),'subtitles':len(subs),'sha256':sha(VIDEO)},indent=2))
