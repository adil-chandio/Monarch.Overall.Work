"""Publish a render as a git blob and record its identifier.

The repository keeps `deliverables/*.mp4` out of Git (they are large), so a
finished render is uploaded as a blob through the API and a small JSON file
next to it records the SHA and size. That gives a stable, fetchable handle on
the exact bytes without bloating the tree.

    python publish_blob.py deliverables/film.mp4 deliverables/film.json
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request


def publish(path: str, meta_path: str) -> dict:
    data = open(path, 'rb').read()
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GH_TOKEN']
    req = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/git/blobs',
        data=json.dumps({'content': base64.b64encode(data).decode(),
                         'encoding': 'base64'}).encode(),
        headers={'Authorization': 'Bearer ' + token,
                 'Accept': 'application/vnd.github+json',
                 'Content-Type': 'application/json'},
        method='POST')
    with urllib.request.urlopen(req, timeout=900) as resp:
        payload = json.load(resp)
    meta = {'blob': payload['sha'], 'size': len(data),
            'file': os.path.basename(path)}
    with open(meta_path, 'w') as fh:
        fh.write(json.dumps(meta) + '\n')
    print('BLOB', meta_path, meta['blob'], meta['size'])
    return meta


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: publish_blob.py <file> <meta.json>')
    publish(sys.argv[1], sys.argv[2])
