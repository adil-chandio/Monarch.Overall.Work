"""Fetch only the four pinned and licensed assets used by this render."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
MANIFEST = HERE.parent / 'celebrity_lookdev' / 'assets.json'
NAMES = {'ryan.glb', 'emma.glb', 'marcus.glb', 'nightstand.glb'}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    assets = [entry for entry in json.loads(MANIFEST.read_text()) if entry['name'] in NAMES]
    if {a['name'] for a in assets} != NAMES:
        raise RuntimeError('asset manifest is incomplete')
    for entry in assets:
        dest = args.directory / entry['name']
        if dest.exists() and sha256(dest) == entry['sha256']:
            print('verified', dest, flush=True)
            continue
        with tempfile.NamedTemporaryFile(dir=args.directory, delete=False) as file:
            tmp = Path(file.name)
            try:
                subprocess.run(['gh', 'api', f"repos/{entry['repo']}/git/blobs/{entry['git_blob']}",
                                '-H', 'Accept: application/vnd.github.raw'], stdout=file, check=True)
            except BaseException:
                tmp.unlink(missing_ok=True)
                raise
        if sha256(tmp) != entry['sha256']:
            tmp.unlink(missing_ok=True)
            raise ValueError('checksum mismatch for ' + entry['name'])
        os.replace(tmp, dest)
        print('verified', dest, flush=True)


if __name__ == '__main__':
    main()
