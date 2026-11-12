#!/usr/bin/env python3
"""Relay only public CC0 dataset screening sheets via Git's blob API.

No commits or repository refs are created. GitHub's Actions artifact host is
not reachable from our sandbox. Git objects on a public repo are not private;
never put original user photos or private assets through this relay.
"""
import base64, json, os, pathlib
import requests
root=pathlib.Path('/tmp/scout')
files=sorted([*root.glob('clips-*.jpg'),root/'index.json'])
if len(files)<2 or not files[-1].exists(): raise RuntimeError('Missing scout output')
repo=os.environ['GH_REPO']
s=requests.Session();s.headers.update({'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
for p in files:
    content=base64.b64encode(p.read_bytes()).decode('ascii')
    r=s.post(f'https://api.github.com/repos/{repo}/git/blobs',json={'content':content,'encoding':'base64'},timeout=120)
    r.raise_for_status();sha=r.json()['sha']
    print(f'::notice title=Scout blob::{p.name} {sha}',flush=True)
