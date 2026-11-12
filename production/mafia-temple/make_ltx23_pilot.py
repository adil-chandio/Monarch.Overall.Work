#!/usr/bin/env python3
"""Package one private Kaggle GPU benchmark; do not include private media."""
import argparse,json,pathlib,re
p=argparse.ArgumentParser();p.add_argument('--user',required=True);p.add_argument('--slug',required=True);p.add_argument('--out',required=True);a=p.parse_args()
if not re.fullmatch('[a-z0-9][a-z0-9_-]*',a.user) or not re.fullmatch('[a-z0-9][a-z0-9-]*',a.slug): raise ValueError('Bad handle or slug')
path=pathlib.Path(a.out);path.mkdir(parents=True,exist_ok=True)
code=(pathlib.Path(__file__).parent/'ltx23_kernel.py').read_text();compile(code,'main.ipynb','exec')
nb={'cells':[{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}], 'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
(path/'main.ipynb').write_text(json.dumps(nb))
(path/'kernel-metadata.json').write_text(json.dumps({'id':f'{a.user}/{a.slug}','title':a.slug,'code_file':'main.ipynb','language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':True,'enable_internet':True,'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[],'machine_shape':'NvidiaTeslaT4'},indent=2))
