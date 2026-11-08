"""Private scene-depth research, not a measured 3D reconstruction.

Input is only approved/generated scenery. A monocular depth estimate is relative
and may invent geometry; it must not be represented as survey-grade or final.
"""
import base64, io, json, os, pathlib, subprocess, sys
IMAGES=__IMAGE_DATA__
os.environ['USE_TF']='0';os.environ['USE_FLAX']='0';os.environ['HF_HUB_DISABLE_XET']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
subprocess.run([sys.executable,'-m','pip','install','-q','numpy<2','transformers==4.49.0','huggingface_hub==0.27.1','safetensors'],check=True)
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
from huggingface_hub import snapshot_download
out=pathlib.Path('/kaggle/working/depth-pilot-output');out.mkdir(exist_ok=True)
model_id='depth-anything/Depth-Anything-V2-Small-hf'
local=snapshot_download(model_id,local_dir='/tmp/depth-v2-small',allow_patterns=['*.json','*.safetensors'],max_workers=1)
processor=AutoImageProcessor.from_pretrained(local)
model=AutoModelForDepthEstimation.from_pretrained(local).eval().to('cuda' if torch.cuda.is_available() else 'cpu')
results=[]
for name,data in IMAGES.items():
 img=Image.open(io.BytesIO(base64.b64decode(data))).convert('RGB')
 tensor=processor(images=img,return_tensors='pt').to(model.device)
 with torch.inference_mode():
  depth=model(**tensor).predicted_depth
  depth=torch.nn.functional.interpolate(depth.unsqueeze(1),size=(img.height,img.width),mode='bicubic',align_corners=False).squeeze().cpu().numpy()
 if not np.isfinite(depth).all():raise ValueError('Nonfinite depth')
 lo,hi=np.percentile(depth,[1,99]);norm=np.clip((depth-lo)/max(float(hi-lo),1e-6),0,1)
 Image.fromarray((norm*65535).astype('uint16')).save(out/f'{name}-relative-depth.png')
 results.append({'name':name,'size':[img.width,img.height],'percentile_1':float(lo),'percentile_99':float(hi)})
(out/'depth-receipt.json').write_text(json.dumps({'model':model_id,'kind':'relative monocular estimate; not metric','status':'research_only','results':results},indent=2))
