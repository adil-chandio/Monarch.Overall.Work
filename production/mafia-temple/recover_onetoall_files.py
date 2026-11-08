#!/usr/bin/env python3
"""Recover only selected files, stopping pagination as soon as they are found.

The GPU job mistakenly ran a large ComfyUI checkout under /kaggle/working, so
`kaggle kernels output --file-pattern ...` still paginates thousands of unrelated
files before filtering client-side. This downloader never starts a GPU job.
"""
import json, os, pathlib, time
import requests
from kaggle.api.kaggle_api_extended import KaggleApi, ApiListKernelSessionOutputRequest

owner=os.environ['KAGGLE_USERNAME']; slug='monarch-onetoall-run-42511685428'
out=pathlib.Path('production/mafia-temple/onetoall-pilot-output');out.mkdir(exist_ok=True)
names={'onetoall-running-pilot.mp4','onetoall-receipt.json','pose-audit.json','pose-audit.jpg','warped-ref-audit.jpg','output-metadata.json'}
found=set();token=None; page=0; retries=0; page_size=100
api=KaggleApi();api.authenticate()
while True:
    try:
        with api.build_kaggle_client() as client:
            req=ApiListKernelSessionOutputRequest();req.user_name=owner;req.kernel_slug=slug;req.page_size=page_size
            if token: req.page_token=token
            response=client.kernels.kernels_api_client.list_kernel_session_output(req)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code==400 and page==0 and page_size>20:
            page_size=20
            print('Server rejected page size; retrying with the standard 20',flush=True)
            continue
        if exc.response is None or exc.response.status_code!=429 or retries>=8: raise
        delay=min(600,30*(2**retries));retries+=1
        print(f'Output-list rate limit; retrying the same page in {delay}s',flush=True);time.sleep(delay);continue
    retries=0; page+=1
    files=response.files or []
    print(f'Output page {page}: {len(files)} entries; found {sorted(found)}',flush=True)
    for item in files:
        # Reject nested ambiguities and never print the signed URL.
        file_name=item.file_name
        if file_name not in names or file_name in found: continue
        r=requests.get(item.url,stream=True,timeout=300);r.raise_for_status()
        target=out/file_name;temp=target.with_suffix(target.suffix+'.partial')
        with temp.open('wb') as f:
            for chunk in r.iter_content(1024*1024):
                if chunk: f.write(chunk)
        if temp.stat().st_size==0: raise RuntimeError('Downloaded empty file: '+file_name)
        temp.replace(target);found.add(file_name);print('Recovered',file_name,flush=True)
    if found==names: break
    token=response.next_page_token
    if not token: raise RuntimeError('Output listing ended; missing '+str(sorted(names-found)))
    if page>=300: raise RuntimeError('Aborting after 300 pages; missing '+str(sorted(names-found)))
    time.sleep(2)
r=json.loads((out/'onetoall-receipt.json').read_text())
if r.get('status')!='complete_research_only' or r.get('original_photo_used') is not False or r.get('output',{}).get('frames')!=49:
    raise RuntimeError('Receipt did not match this approved research output')
print('Recovered all six completed research outputs; no original photo was used.',flush=True)
