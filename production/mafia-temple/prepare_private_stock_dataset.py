#!/usr/bin/env python3
"""Stage one public stock clip as a *private* Kaggle dataset; no user photo."""
import hashlib,json,os,pathlib,subprocess,sys
import requests
slug=sys.argv[1];owner=os.environ['KAGGLE_USERNAME']
if not slug.startswith('monarch-motion-driver-'):raise ValueError('Unexpected dataset slug')
root=pathlib.Path('/tmp')/slug;root.mkdir(exist_ok=False)
url='https://videos.pexels.com/video-files/32740423/13958018_1440_2560_30fps.mp4'
expected='fef029f40687ee924f0eaef6e3da932485441db4b9a3c992780121b12507e28d'
h=hashlib.sha256();size=0
with requests.get(url,stream=True,timeout=(30,120)) as response:
 response.raise_for_status()
 with (root/'driver.mp4').open('wb') as f:
  for chunk in response.iter_content(1024*1024):
   if chunk:
    size+=len(chunk)
    if size>50_000_000:raise ValueError('Unexpected source size')
    h.update(chunk);f.write(chunk)
if h.hexdigest()!=expected:raise ValueError('Stock source checksum mismatch')
meta={'title':f'Monarch motion driver {slug[-11:]}','id':f'{owner}/{slug}','licenses':[{'name':'other'}], 'description':'Private pose research only. Source: Eduardo Holanda, Pexels video 32740423. Pexels License: https://www.pexels.com/license/. No user photograph or character asset.'}
(root/'dataset-metadata.json').write_text(json.dumps(meta))
# Kaggle API's default is private. Never add -u/--public.
subprocess.run(['kaggle','datasets','create','-p',str(root),'--quiet'],check=True)
print(f'::notice title=Private motion dataset::{owner}/{slug}',flush=True)
