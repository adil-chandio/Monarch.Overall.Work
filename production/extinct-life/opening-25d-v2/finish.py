"""Mux unchanged approved-direction 2.5D audio into the polish revision; decode and audit."""
from pathlib import Path
import subprocess,json,re
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;C=Path('.cache/extinct-opening-25d-v2');ff=imageio_ffmpeg.get_ffmpeg_exe()
old=Path('deliverables/Extinct_Life_Opening_25D_Amber_Atlas_45s_1080p.mp4')
out=Path('deliverables/Extinct_Life_Opening_25D_Cinema_Polish_45s_1080p.mp4')
assert old.exists() and (C/'picture.mp4').exists()
subprocess.run([ff,'-y','-v','warning','-i',str(C/'picture.mp4'),'-i',str(old),'-map','0:v:0','-map','1:a:0','-c','copy','-t','45','-movflags','+faststart',str(out)],check=True)
def audio_hash(p):
 r=subprocess.run([ff,'-v','error','-i',str(p),'-map','0:a:0','-t','45','-c:a','pcm_s16le','-f','hash','-hash','sha256','-'],capture_output=True,text=True,check=True)
 return r.stdout.strip()
old_hash=audio_hash(old);new_hash=audio_hash(out);assert old_hash==new_hash,'Audio must be unchanged for visual A/B comparison'
scan=subprocess.run([ff,'-hide_banner','-i',str(out),'-vn','-af','loudnorm=I=-16:TP=-2:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
levels=json.loads(re.search(r'\{\s*"input_i".*?\}',scan.stderr,re.S).group())
r=subprocess.run([ff,'-hide_banner','-i',str(out),'-an','-vf','freezedetect=n=-60dB:d=0.6,blackdetect=d=0.3:pix_th=0.02:pic_th=0.99','-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
frames=[int(x) for x in re.findall(r'^frame=(\d+)$',r.stdout,re.M)];assert frames[-1]==1350
assert '1920x1080' in r.stderr and '30 fps' in r.stderr
issues=[x for x in r.stderr.splitlines() if 'freeze_' in x or 'black_start:' in x]
motion=subprocess.run([ff,'-v','error','-i',str(out),'-vf','fps=2,scale=320:180','-an','-f','framemd5','-'],capture_output=True,text=True,check=True)
hashes=[x.split(',')[-1].strip() for x in motion.stdout.splitlines() if not x.startswith('#') and x.strip()]
times=[1,4.5,8.5,14.5,21,25,29,33,38,42]
sheet=Image.new('RGB',(1920,520),(8,29,35));d=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for i,t in enumerate(times):
 p=C/f'final_{i:02d}.jpg';subprocess.run([ff,'-y','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1',str(p)],check=True)
 x=i%5*384;y=i//5*260;sheet.paste(Image.open(p).resize((384,216)),(x,y));d.text((x+10,y+229),f'{t:04.1f}s / CINEMA POLISH',font=font,fill='#dfbb7e')
sheet.save(C/'final_contact_sheet.jpg',quality=92)
qc={'file':str(out),'theme':'Amber Atlas — Cinema Polish v2','scope':'45-second visual style comparison, not the full 6–8-minute episode','native_resolution':[1920,1080],'fps':30,'decoded_frames':frames[-1],'duration_seconds':45,'bytes':out.stat().st_size,'audio_reference':str(old),'decoded_45s_audio_sha256':new_hash,'audio_identical_to_previous_25d':old_hash==new_hash,'measured_encoded_audio':levels,'black_or_freeze_events':issues,'review_limits':'Ten final frames sampled; not a full creative watch, anatomical validation or competitor benchmark. No word-aligned subtitles claimed.','half_second_motion_samples':{'count':len(hashes),'unique_decoded_frames':len(set(hashes))},'diagnostic_interpretation':'Freeze detector includes low-motion cartography, settled diagrams and explanatory holds; not a creative score. Full decode and sampled frame hashes are separate checks.','owner_style_approval':'pending'}
qc['native_render_checks']=json.loads((C/'render.json').read_text())
qc['changes']=['Refined ink/teal/amber palette and lens edge falloff','Blended leg shading and hip occlusion, cleaner body silhouette','C1 Hermite camera rail and shot-specific dolly easing','Short two-scene dissolves with amber evidence carriers','Staggered reference matching and title reveals','Quieter editorial hierarchy and limits disclosures']
assert not any('black_start:' in x for x in issues), 'Unexpected black interval'
(P/'QC.json').write_text(json.dumps(qc,indent=2)+'\n');print(json.dumps(qc,indent=2))
