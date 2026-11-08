#!/usr/bin/env python3
"""Build a private pose preflight or single One-to-All research render.

No original user image, 3D texture, or source stock pixels are output. The
public stock video is used only to detect poses inside the Kaggle runtime.
"""
import argparse, hashlib, json, pathlib, re
here=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);p.add_argument('--stage',required=True,choices=['preflight','render']);a=p.parse_args()
slug=re.sub('[^a-z0-9]+','-',a.slug.lower()).strip('-')[:48]
if not slug: raise ValueError('Empty slug')
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
reference=(here/'keyframes/shot-04-identity-study-b.jpg').read_bytes()
assets={'reference':{'url':'https://raw.githubusercontent.com/adil-chandio/Monarch.Overall.Work/4204ebe/production/mafia-temple/keyframes/shot-04-identity-study-b.jpg','sha256':hashlib.sha256(reference).hexdigest()},'driver':{'url':'https://videos.pexels.com/video-files/32740423/13958018_1440_2560_30fps.mp4','sha256':'fef029f40687ee924f0eaef6e3da932485441db4b9a3c992780121b12507e28d'}}
ns={};exec((here/'onetoall_graph.py').read_text(),ns);graph=ns['make_graph']()
# This preserves the complete generated reference; motion is transformed to it.
# Output pose still requires visual validation, including limbs near boundaries.
graph['3']['inputs']['align_to']='ref'
# Do not use the stock performer's facial landmarks as a guide.
graph['3']['inputs']['draw_face_points']='none'
if a.stage=='preflight':
    graph={k:graph[k] for k in ('1','2','3','4')}
    graph['15']={'class_type':'PrivateAuditSink','inputs':{'images':['4',0]}}
code=(here/'onetoall_real_kernel.py').read_text()
for name,value in {'__ASSETS__':assets,'__NODES__':(here/'onetoall_real_nodes.py').read_text(),'__GRAPH__':graph,'__STAGE__':a.stage}.items():
    if code.count(name)!=1: raise ValueError(f'Missing or duplicated placeholder {name}')
    code=code.replace(name,repr(value))
compile(code,'main.ipynb','exec')
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(out/'main.ipynb').write_text(json.dumps(nb))
(out/'kernel-metadata.json').write_text(json.dumps({'id':f'{a.user}/{slug}','title':slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'},indent=2))
print(f'Private {a.stage} notebook prepared. Original user photo and 3D assets are not used.')
