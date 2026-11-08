#!/usr/bin/env python3
"""Relay explicitly whitelisted pose and generated outputs as public Git blobs.

Git blobs are not private, even when no ref names them. Never include a user
original, 3D asset, or the stock video. The reference image is already public
and the user permits generated images/video; perform QA before delivery.
"""
import base64, json, os, pathlib, sys
import requests
out=pathlib.Path(sys.argv[1]);stage=sys.argv[2]
files=['onetoall-receipt.json','pose-audit.json','pose-audit.jpg','warped-ref-audit.jpg']+[f'pose-frames-{i:03d}.jpg' for i in range(0,49,7)]
if stage=='render':files+=['onetoall-running-pilot.mp4','output-metadata.json']
if stage not in ('preflight','render'):raise ValueError('Unknown stage')
receipt=json.loads((out/'onetoall-receipt.json').read_text())
status='complete_pose_preflight' if stage=='preflight' else 'complete_research_only'
if receipt.get('status')!=status or receipt.get('original_photo_used') is not False: raise ValueError('Receipt failed safety check')
headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'}
for name in files:
    data=(out/name).read_bytes()
    if not data or len(data)>20_000_000: raise ValueError('Unexpected output size '+name)
    r=requests.post(f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/git/blobs",json={'content':base64.b64encode(data).decode(),'encoding':'base64'},headers=headers,timeout=120);r.raise_for_status()
    print(f'::notice title=Real pilot {stage}::{name} {r.json()["sha"]}',flush=True)
