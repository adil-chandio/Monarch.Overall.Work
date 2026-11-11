"""Download pinned, independently-licensed GLBs via GitHub CLI and verify sha256."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,tempfile
P=Path(__file__).resolve().parent
out=Path(sys.argv[1] if len(sys.argv)>1 else '/home/user/celebrity-lookdev-assets');out.mkdir(parents=True,exist_ok=True)
for a in json.loads((P/'assets.json').read_text()):
 path=out/a['name']
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=a['sha256']:
  with tempfile.NamedTemporaryFile(dir=out,delete=False) as fp:
   tmp=Path(fp.name)
   try:
    subprocess.run(['gh','api',f"repos/{a['repo']}/git/blobs/{a['git_blob']}",'-H','Accept: application/vnd.github.raw+json'],stdout=fp,check=True)
   except BaseException:
    tmp.unlink(missing_ok=True);raise
  if hashlib.sha256(tmp.read_bytes()).hexdigest()!=a['sha256']:
   tmp.unlink(missing_ok=True);raise ValueError('checksum mismatch: '+a['name'])
  os.replace(tmp,path)
 print(a['name'],a['sha256'])
