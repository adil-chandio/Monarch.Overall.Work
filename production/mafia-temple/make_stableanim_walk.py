#!/usr/bin/env python3
"""Package the private research-only walk test; never reads the original photo."""
import argparse,base64,json,pathlib,re,subprocess
from io import BytesIO
from PIL import Image
root=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);a=p.parse_args()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);slug=re.sub('[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
data=json.loads(subprocess.check_output(['gh','api','repos/konyshevgmbh/cmu-mocap/contents/data/007/07_05.bvh'],text=True));bvh=base64.b64decode(data['content']).decode('utf-8')
def jpeg(im):
    buf=BytesIO();im.save(buf,format='JPEG',quality=92);return base64.b64encode(buf.getvalue()).decode()
source=Image.open(root/'keyframes/shot-01.jpg').convert('RGB').crop((145,30,857,742)).resize((512,512),Image.Resampling.LANCZOS)
identity=Image.open(root/'keyframes/shot-05a.jpg').convert('RGB').resize((768,429),Image.Resampling.LANCZOS)
code=(root/'stableanim_walk_kernel.py').read_text()
for name,value in {'SOURCE_JPEG':jpeg(source),'IDENTITY_JPEG':jpeg(identity),'BVH_TEXT':bvh,'POSE_GENERATOR':(root/'walk_mocap_to_poses.py').read_text(),'BASE_POSE_HELPER':(root/'mocap_to_poses.py').read_text(),'FACE_OFFSETS':None}.items():
 code=code.replace('__'+name+'__',repr(value))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb));(out/'kernel-metadata.json').write_text(json.dumps({'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'},indent=2))
print('Prepared rear-view walking research test from approved generated frames')
