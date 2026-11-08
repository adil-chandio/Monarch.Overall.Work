#!/usr/bin/env python3
"""Package the research-only portrait pilot without the original reference."""
import argparse, base64, json, pathlib, re
root=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(); p.add_argument('--user',required=True); p.add_argument('--slug',required=True); p.add_argument('--out',required=True); p.add_argument('--turn-test',action='store_true'); p.add_argument('--front-turn',action='store_true'); a=p.parse_args()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
slug=re.sub(r'[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
keyframes=root/'production/mafia-temple/keyframes'
images={name:base64.b64encode((keyframes/fn).read_bytes()).decode() for name,fn in [('side','shot-05a.jpg'),('front','shot-05b.jpg')]}
if a.front_turn:
 images['front-neutral']=base64.b64encode((keyframes/'shot-05-neutral-generated.jpg').read_bytes()).decode()
kernel = 'liveportrait_front_turn_kernel.py' if a.front_turn else ('liveportrait_turn_kernel.py' if a.turn_test else 'liveportrait_kernel.py')
code=(root/'production/mafia-temple'/kernel).read_text().replace('__IMAGE_DATA__',repr(images))
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb))
meta={'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'}
(out/'kernel-metadata.json').write_text(json.dumps(meta,indent=2))
print('Packaged approved generated images only; no original references.')
