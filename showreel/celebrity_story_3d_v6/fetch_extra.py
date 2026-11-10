"""Second-tier avatars and furniture, pinned by blob id from public repos."""
from pathlib import Path
import hashlib, json, subprocess, sys, os, tempfile
P = Path(__file__).resolve().parent
out = Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/celebrity-lookdev-assets')
out.mkdir(parents=True, exist_ok=True)
for a in json.loads((P / 'extra_assets.json').read_text()):
    path = out / a['name']
    if path.is_file() and path.stat().st_size > 1000:
        print(a['name'], 'ok')
        continue
    subprocess.run(['gh', 'api', f"repos/{a['repo']}/git/blobs/{a['git_blob']}",
                    '-H', 'Accept: application/vnd.github.raw'],
                   stdout=open(path, 'wb'), check=True)
    print(a['name'], hashlib.sha256(path.read_bytes()).hexdigest()[:12])
