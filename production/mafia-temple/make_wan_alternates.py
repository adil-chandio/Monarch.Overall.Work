#!/usr/bin/env python3
"""Package native-frame WAN 2.2 scene renders in one private GPU notebook."""
import argparse,base64,json,pathlib,re
from io import BytesIO
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
slug=re.sub(r'[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
scenes=[
 {'id':'wan4-street-a','image':'shot-01.jpg','frames':97,'seed':8321,'prompt':'A well-exposed cinematic night shot from a low tracking camera following one man in a black suit walking steadily away down a wet Japanese street towards the bright futuristic city. The camera stays behind him at matching speed. He takes a sequence of clearly visible regular steps, left leg then right leg and gently swings his arms. Bright cold blue city lights silhouette his body and illuminate the pavement; realistic scene, one man.'},
 {'id':'wan4-street-b','image':'shot-01.jpg','frames':97,'seed':1367,'prompt':'Low camera tracking behind a black-suited man who walks forward away down a rainy street. He takes several continuous natural steps; his feet lift and land alternately on the wet road, arms swing opposite his legs. Maintain full body framing throughout, steady tracking and bright detailed futuristic skyline at night. Cinematic lighting with clear visible silhouette.'},
 {'id':'wan4-gate','image':'shot-02.jpg','frames':121,'seed':4280,'prompt':'A locked-off wide composition shows the large traditional Japanese temple gate at night, illuminated clearly by warm lanterns and moonlight. Mist slowly rolls over the stone courtyard. The gate remains stable, the camera remains still. An atmospheric cinematic shot with detailed visible architecture, no people.'},
 {'id':'wan4-aerial','image':'shot-03.jpg','frames':97,'seed':2113,'prompt':'Cinematic continuous drone camera moves forward and descends smoothly over the Japanese temple compound at night toward a central stone courtyard. The temple gradually grows larger and the surrounding rooftops move naturally with parallax. A tiny lone man in a black suit stands on the central path throughout. Stable architecture and realistic moonlight, subtle night fog.'},
 {'id':'wan4-running-a','image':'shot-04.jpg','frames':73,'seed':6314,'prompt':'A fast side tracking camera follows one dark haired bearded man wearing a black tailored suit running naturally to the right across a stone paved Japanese temple courtyard at night. His entire body including both feet stays fully visible within frame. His legs alternate as he runs, arms swing in opposition and the camera moves at his exact speed. One person only, realistic coherent anatomy, no body changes.'},
 {'id':'wan4-running-b','image':'shot-04.jpg','frames':73,'seed':1498,'prompt':'Cinematic smooth side-on tracking shot of the black suited dark haired man running to the right through a Japanese temple courtyard. Camera tracks at the same speed as him and keeps his whole body from head to feet visible at all times. He runs with natural alternating strides and opposite arm swings. Realistic anatomy, coherent face and clothing.'},
 {'id':'wan4-face-a','image':'shot-05a.jpg','frames':97,'seed':829,'prompt':'One continuous close-up: the dark haired bearded man in a black suit looks to his left, then slowly and naturally turns his head to face the camera, and his lips curl into a restrained menacing smile. Preserve his exact facial identity, beard, eyes, hairstyle, proportions and black clothing. Realistic continuous human movement with a stable dark Japanese temple background and locked camera.'},
 {'id':'wan4-face-b','image':'shot-05a.jpg','frames':97,'seed':2102,'prompt':'The same black suited man with dark hair and a beard stands in the dark Japanese temple. In a single close-up he slowly turns his head from a left-facing three-quarter profile to look directly into the lens, and gives an understated sinister smile. Keep the same man and the same exact facial features and the same camera framing throughout. Natural smooth head movement, no sudden changes.'}
]
images={}
for scene in scenes:
 b=BytesIO();Image.open(root/'production/mafia-temple/keyframes'/scene['image']).convert('RGB').resize((512,288),Image.Resampling.LANCZOS).save(b,format='JPEG',quality=85);images[scene['id']]=base64.b64encode(b.getvalue()).decode()
code='''import os, pathlib, subprocess, sys, time, json, gc, base64
os.environ["TOKENIZERS_PARALLELISM"]="false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"]="expandable_segments:True"
os.environ["HF_HOME"]="/tmp/monarch-hf-cache"
SCENES=SCENE_DATA
IMAGES=IMAGE_DATA
r=subprocess.run([sys.executable,"-m","pip","install","-q","diffusers>=0.35.2","transformers>=4.49,<5","accelerate","sentencepiece","ftfy","imageio-ffmpeg","safetensors"],capture_output=True,text=True)
if r.returncode: raise RuntimeError("pip install failed")
import torch
from PIL import Image,ImageOps
from io import BytesIO
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
from diffusers.utils import export_to_video
if not torch.cuda.is_available(): raise RuntimeError("NO_GPU_ALLOCATED")
model_id="Wan-AI/Wan2.2-TI2V-5B-Diffusers"
negative="face identity change, face morphing, disfigured, deformity, duplicate people, extra limbs, wrong anatomy, jitter, flicker, visual glitches, blur, cartoon, text, subtitles, watermark"
print("STAGE 1: text conditioning",flush=True)
enc=WanImageToVideoPipeline.from_pretrained(model_id,transformer=None,vae=None,torch_dtype=torch.float16,expand_timesteps=True)
enc.to("cuda")
emb={}
with torch.inference_mode():
 for s in SCENES:
  a,b=enc.encode_prompt(prompt=s['prompt'],negative_prompt=negative,do_classifier_free_guidance=True,device=torch.device('cuda'),dtype=torch.float16)
  if not torch.isfinite(a).all() or not torch.isfinite(b).all(): raise RuntimeError('Non-finite prompt embeddings')
  emb[s['id']]=(a.cpu(),b.cpu());print('encoded',s['id'],flush=True)
del enc;gc.collect();torch.cuda.empty_cache()
print("STAGE 2: loading video model",flush=True)
vae=AutoencoderKLWan.from_pretrained(model_id,subfolder="vae",torch_dtype=torch.float32)
pipe=WanImageToVideoPipeline.from_pretrained(model_id,vae=vae,text_encoder=None,tokenizer=None,torch_dtype=torch.float16,expand_timesteps=True)
pipe.enable_model_cpu_offload();pipe.vae.enable_tiling();pipe.set_progress_bar_config(disable=True)
out=pathlib.Path('/kaggle/working/clips');out.mkdir(exist_ok=True)
receipts=[]
for s in SCENES:
 name=s['id'];t=time.time()
 try:
  print('Generating',name,flush=True)
  img=ImageOps.fit(Image.open(BytesIO(base64.b64decode(IMAGES[name]))).convert('RGB'),(512,288),method=Image.Resampling.LANCZOS)
  a,b=emb[name]
  with torch.inference_mode():
   frames=pipe(image=img,prompt_embeds=a.to('cuda'),negative_prompt_embeds=b.to('cuda'),height=288,width=512,num_frames=s['frames'],num_inference_steps=20,guidance_scale=4.0,generator=torch.Generator('cpu').manual_seed(s['seed'])).frames[0]
  export_to_video(frames,str(out/(name+'.mp4')),fps=24)
  receipts.append({'id':name,'frames':len(frames),'width':512,'height':288,'seconds_elapsed':round(time.time()-t,1),'status':'ok'})
  del frames,img;gc.collect();torch.cuda.empty_cache();print('COMPLETED',name,flush=True)
 except Exception as e:
  receipts.append({'id':name,'status':'failed','error_class':type(e).__name__})
  print('FAILED',name,type(e).__name__,flush=True);gc.collect();torch.cuda.empty_cache()
(out/'receipts_wan4.json').write_text(json.dumps(receipts,indent=2))
if not any(x['status']=='ok' for x in receipts): raise RuntimeError('No scenes rendered successfully')
'''.replace('SCENE_DATA',repr(scenes)).replace('IMAGE_DATA',repr(images))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb));meta={'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'}
(out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2));print('Packaged eight alternate native-motion scene candidates')
