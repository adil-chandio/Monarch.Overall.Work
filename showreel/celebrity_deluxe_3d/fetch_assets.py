"""Fetch SHA-256-pinned, credited visual or sound assets outside Git."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(directory, group='all'):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    assets = json.loads((HERE/'assets.json').read_text())
    for entry in assets:
        if group != 'all' and entry['group'] != group:
            continue
        dest = directory/entry['name']
        if dest.is_file() and sha256(dest) == entry['sha256']:
            print('verified', dest, flush=True)
            continue
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as f:
            temp = Path(f.name)
            try:
                subprocess.run(['gh','api',f"repos/{entry['repo']}/git/blobs/{entry['git_blob']}",
                                '-H','Accept: application/vnd.github.raw'], stdout=f, check=True)
            except BaseException:
                temp.unlink(missing_ok=True)
                raise
        if sha256(temp) != entry['sha256']:
            temp.unlink(missing_ok=True)
            raise ValueError('checksum mismatch: '+entry['name'])
        os.replace(temp, dest)
        print('verified', dest, flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('directory', type=Path)
    p.add_argument('--group', choices=('all','visual','audio'), default='all')
    a=p.parse_args()
    fetch(a.directory, a.group)


if __name__ == '__main__':
    main()
