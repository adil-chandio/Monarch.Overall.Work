"""Restore the recorded narration takes from Git blobs so CI can rebuild audio."""
from pathlib import Path
import hashlib, json, subprocess
P = Path(__file__).resolve().parent
out = P / 'audio'
out.mkdir(parents=True, exist_ok=True)
for a in json.loads((P / 'audio_blobs.json').read_text()):
    path = out / a['name']
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == a['sha256']:
        print(a['name'], 'ok')
        continue
    subprocess.run(['gh', 'api', f"repos/{a['repo']}/git/blobs/{a['blob']}",
                    '-H', 'Accept: application/vnd.github.raw'],
                   stdout=open(path, 'wb'), check=True)
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != a['sha256']:
        raise SystemExit(f'checksum mismatch for {a["name"]}')
    print(a['name'], 'fetched')
