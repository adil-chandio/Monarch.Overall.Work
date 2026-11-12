"""Fetch licensed, hash-pinned people, materials and props outside the repository."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / 'celebrity_lookdev' / 'assets.json'
WANTED = {'ryan.glb', 'emma.glb', 'marcus.glb', 'nightstand.glb', 'armchair.glb'}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def entries():
    legacy = [e for e in json.loads(LEGACY.read_text()) if e['name'] in WANTED]
    if {e['name'] for e in legacy} != WANTED:
        raise ValueError('legacy asset manifest is incomplete')
    return legacy + json.loads((HERE / 'assets.json').read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    for asset in entries():
        dest = args.directory / asset['name']
        if dest.is_file() and sha256(dest) == asset['sha256']:
            print('verified', dest, flush=True)
            continue
        if 'git_blob' in asset:
            endpoint = f"repos/{asset['repo']}/git/blobs/{asset['git_blob']}"
            accept = 'application/vnd.github.raw'
        else:
            endpoint = f"repos/{asset['repo']}/releases/assets/{asset['release_asset']}"
            accept = 'application/octet-stream'
        with tempfile.NamedTemporaryFile(dir=args.directory, delete=False) as f:
            tmp = Path(f.name)
            try:
                subprocess.run(['gh', 'api', endpoint, '-H', 'Accept: ' + accept], stdout=f, check=True)
            except BaseException:
                tmp.unlink(missing_ok=True)
                raise
        if sha256(tmp) != asset['sha256']:
            tmp.unlink(missing_ok=True)
            raise ValueError('checksum mismatch for ' + asset['name'])
        os.replace(tmp, dest)
        print('verified', dest, flush=True)


if __name__ == '__main__':
    main()
