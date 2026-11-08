#!/usr/bin/env python3
"""Build one private Kaggle research notebook from already-generated assets."""
import argparse, base64, json, pathlib, re

here=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True)
a=p.parse_args()
slug=re.sub('[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
if not slug: raise ValueError('Empty slug')
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
reference=(here/'keyframes/shot-04-identity-study-b.jpg').read_bytes()
driver=(here/'run-pilot-output/run-motion-pilot-tall-v6.mp4').read_bytes()
ns={};exec((here/'onetoall_graph.py').read_text(),ns);graph=ns['make_graph']()
code=(here/'onetoall_kaggle_kernel.py').read_text()
for name,value in {'__REFERENCE__':base64.b64encode(reference).decode(),'__DRIVER__':base64.b64encode(driver).decode(),'__NODES__':(here/'onetoall_private_nodes.py').read_text(),'__GRAPH__':graph}.items():
    if code.count(name)!=1: raise ValueError(f'Missing or duplicated placeholder {name}')
    code=code.replace(name,repr(value))
compile(code,'main.ipynb','exec')
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb))
(out/'kernel-metadata.json').write_text(json.dumps({'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'},indent=2))
print('Private T4 notebook prepared. Only existing generated reference and generated v6 driver included.')
