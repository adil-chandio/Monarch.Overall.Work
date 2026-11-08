#!/usr/bin/env python3
"""Package only generated scenery in a private Kaggle depth experiment."""
import argparse,base64,json,pathlib,re
from io import BytesIO
from PIL import Image
root=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);a=p.parse_args()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);slug=re.sub('[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
images={}
for name,fn in [('aerial','shot-03.jpg'),('courtyard','courtyard-clean-vfx.jpg'),('street','street-clean-vfx.jpg'),('gate','shot-02.jpg')]:
 image=Image.open(root/'keyframes'/fn).convert('RGB'); image.thumbnail((1024,768),Image.Resampling.LANCZOS)
 data=BytesIO();image.save(data,format='JPEG',quality=76,optimize=True)
 images[name]=base64.b64encode(data.getvalue()).decode()
code=(root/'depth_scene_kernel.py').read_text().replace('__IMAGE_DATA__',repr(images))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb));(out/'kernel-metadata.json').write_text(json.dumps({'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'},indent=2))
print('Depth experiment packaged using generated scenery only')
