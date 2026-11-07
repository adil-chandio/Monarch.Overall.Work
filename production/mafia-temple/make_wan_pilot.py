#!/usr/bin/env python3
"""Build a private single-GPU WAN 2.2 image-conditioned motion pilot.
The packed image is a user-approved AI keyframe, not the reference photo.
"""
import argparse,base64,json,pathlib,re
from io import BytesIO
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
slug=re.sub(r'[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
buf=BytesIO()
Image.open(root/'production/mafia-temple/keyframes/v2-close-start.png').convert('RGB').resize((1024,576),Image.Resampling.LANCZOS).save(buf,format='JPEG',quality=94)
img=base64.b64encode(buf.getvalue()).decode()
code='''import base64, os, pathlib, subprocess, sys, time, json
os.environ["TOKENIZERS_PARALLELISM"]="false"
os.environ["HF_HOME"]="/tmp/monarch-hf-cache"
os.environ["PYTORCH_CUDA_ALLOC_CONF"]="expandable_segments:True"
image_file=pathlib.Path("/kaggle/working/start.png")
image_file.write_bytes(base64.b64decode(IMAGE_PAYLOAD))
r=subprocess.run([sys.executable,"-m","pip","install","-q","diffusers>=0.35.2","transformers>=4.49,<5","accelerate","sentencepiece","ftfy","imageio-ffmpeg","safetensors","bitsandbytes>=0.45.0"],capture_output=True,text=True)
if r.returncode: raise RuntimeError("pip install failed: "+r.stderr[-500:])
import torch
from PIL import Image,ImageOps
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline, BitsAndBytesConfig as DiffusersBitsAndBytesConfig
from diffusers.quantizers import PipelineQuantizationConfig
import gc
from diffusers.utils import export_to_video
if not torch.cuda.is_available(): raise RuntimeError("NO_GPU_ALLOCATED")
print("GPU",torch.cuda.get_device_name(0),flush=True)
model_id="Wan-AI/Wan2.2-TI2V-5B-Diffusers"
prompt="Cinematic close-up. The dark haired bearded man in a black tailored suit in a dim Japanese temple slowly turns his head to look directly at the camera, preserving the same face, beard, hairstyle and clothing. His eyes glow red as his lips form a subtle sinister smile. Natural continuous movement, realistic anatomy and lighting, stable shot."
negative="face changing, identity change, extra people, distorted facial features, unnatural eyes, deformed body, flickering, jitter, low quality, blur, text, subtitles, cartoon, cuts"
print("STAGE 1 text embeddings only",flush=True)
enc=WanImageToVideoPipeline.from_pretrained(model_id,transformer=None,vae=None,torch_dtype=torch.float16,expand_timesteps=True)
enc.to("cuda")
with torch.inference_mode():
 pos,neg=enc.encode_prompt(prompt=prompt,negative_prompt=negative,do_classifier_free_guidance=True,device=torch.device("cuda"),dtype=torch.float16)
 if not torch.isfinite(pos).all() or not torch.isfinite(neg).all(): raise RuntimeError("Non-finite prompt embeddings")
 pos,neg=pos.cpu(),neg.cpu()
del enc
gc.collect();torch.cuda.empty_cache()
print("STAGE 2 transformer and VAE",flush=True)
vae=AutoencoderKLWan.from_pretrained(model_id,subfolder="vae",torch_dtype=torch.float32)
quant=PipelineQuantizationConfig(quant_mapping={"transformer": DiffusersBitsAndBytesConfig(load_in_8bit=True)})
pipe=WanImageToVideoPipeline.from_pretrained(model_id,vae=vae,text_encoder=None,tokenizer=None,torch_dtype=torch.float16,expand_timesteps=True,quantization_config=quant)
pipe.enable_model_cpu_offload()
pipe.vae.enable_tiling()
pipe.set_progress_bar_config(disable=True)
img=ImageOps.fit(Image.open(image_file).convert("RGB"),(640,352),method=Image.Resampling.LANCZOS)
t=time.time()
print("STAGE 3 video generation",flush=True)
with torch.inference_mode():
 frames=pipe(image=img,prompt_embeds=pos,negative_prompt_embeds=neg,height=352,width=640,num_frames=65,num_inference_steps=20,guidance_scale=4.0,generator=torch.Generator("cpu").manual_seed(3451)).frames[0]
out=pathlib.Path("/kaggle/working/clips");out.mkdir(exist_ok=True)
export_to_video(frames,str(out/"wan-face-pilot.mp4"),fps=24)
(out/"receipts_wan-face-pilot.json").write_text(json.dumps({"backend":model_id,"frames":len(frames),"width":640,"height":352,"seconds_elapsed":round(time.time()-t,1)},indent=2))
print("PILOT COMPLETE",len(frames),flush=True)
'''.replace('IMAGE_PAYLOAD',repr(img))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb));meta={'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'}
(out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2));print('Packaged private GPU pilot')
