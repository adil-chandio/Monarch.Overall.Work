#!/usr/bin/env python3
"""Construct a private Kaggle notebook. No original reference image is used."""
import argparse, base64, json, pathlib, re, subprocess
from io import BytesIO
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);p.add_argument('--hands',action='store_true');a=p.parse_args()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);slug=re.sub('[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
# CMU mocap 09_01 is downloaded at runtime, not committed or redistributed as a source asset.
data=json.loads(subprocess.check_output(['gh','api','repos/konyshevgmbh/cmu-mocap/contents/data/009/09_01.bvh'],text=True))
bvh=base64.b64decode(data['content']).decode('utf-8')
image=Image.open(root/'production/mafia-temple/keyframes/shot-04.jpg').convert('RGB').crop((345,30,1057,742)).resize((512,512),Image.Resampling.LANCZOS)
buf=BytesIO();image.save(buf,format='JPEG',quality=92)
base=root/'production/mafia-temple'
kernel='stableanim_hands_kernel.py' if a.hands else 'stableanim_kernel.py'
pose='run_hand_mocap_to_poses.py' if a.hands else 'mocap_to_poses.py'
code=(base/kernel).read_text().replace('__SOURCE_JPEG__',repr(base64.b64encode(buf.getvalue()).decode())).replace('__BVH_TEXT__',repr(bvh)).replace('__POSE_GENERATOR__',repr((base/pose).read_text())).replace('__FACE_OFFSETS__',repr(json.loads((base/'generated-keyframe-face68.json').read_text())))
if a.hands:
 code=code.replace('__HAND_OFFSETS__',repr(json.loads((base/'generated-keyframe-hand21.json').read_text())))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb)); (out/'kernel-metadata.json').write_text(json.dumps({'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'},indent=2))
print('Prepared controlled-motion research test, without original reference')
