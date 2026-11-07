#!/usr/bin/env python3
"""Package native-frame WAN 2.2 scene renders in one private GPU notebook."""
import argparse,base64,json,pathlib,re
from io import BytesIO
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
slug=re.sub(r'[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
scenes=[
 {'id':'wan3-street','image':'shot-01.jpg','frames':97,'seed':524,'prompt':'A low-angle cinematic tracking shot follows a single man in a black tailored suit from behind as he walks away along a wet street at night toward a distant futuristic city. His feet lift and alternate taking multiple natural continuous steps; his arms swing rhythmically. The camera follows behind at his walking speed. Reflections and drifting mist; one realistic man only, no body deformation.'},
 {'id':'wan3-gate','image':'shot-02.jpg','frames':121,'seed':352,'prompt':'Locked off static wide shot of a large traditional Japanese temple gate at night. Thin low fog rolls steadily across the stone path and warm lanterns gently flicker. The camera and the architectural structures remain still, detailed, coherent and realistically lit. No people or animals.'},
 {'id':'wan3-aerial','image':'shot-03.jpg','frames':97,'seed':832,'prompt':'A continuous high-angle aerial drone shot of a Japanese temple compound at night. The drone smoothly descends and flies forward toward the courtyard and temple roofs, naturally increasing their size and revealing the grounds in perspective. One small man in a black suit is present on the central path. Realistic architecture, light mist, stable cinematic movement.'},
 {'id':'wan3-running','image':'shot-04.jpg','frames':73,'seed':950,'prompt':'A fast side tracking shot follows one man in a black tailored suit running swiftly to the right through a stone paved Japanese temple courtyard at night. He takes clear alternating running strides with correctly coordinated arms and legs. His feet contact the ground; the camera moves at the same speed and keeps his whole body in frame. Preserve the same natural face, dark hair, beard, suit and human anatomy.'},
 {'id':'wan3-face','image':'shot-05a.jpg','frames':97,'seed':615,'prompt':'In one continuous close-up in a dim Japanese temple, the dark haired bearded man in a black suit starts looking to his left. He turns his head naturally toward the camera, looking directly at the viewer with a threatening glare. His eyes glow vivid supernatural red and his mouth forms a small sinister smile. His facial identity, beard, hair, skin and clothing stay unchanged. Realistic skin texture, no cuts, static stable background.'},
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
(out/'receipts_wan3.json').write_text(json.dumps(receipts,indent=2))
if not any(x['status']=='ok' for x in receipts): raise RuntimeError('No scenes rendered successfully')
'''.replace('SCENE_DATA',repr(scenes)).replace('IMAGE_DATA',repr(images))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb));meta={'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'}
(out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2));print('Packaged five native-motion scene candidates')
