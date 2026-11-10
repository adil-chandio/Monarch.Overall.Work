"""Compare local reference OBJ to a third-party copy of Smithsonian's glTF.

Pass a downloaded `scene.gltf` and `scene.bin`. This measures nearest vertex
spacing, not mesh surface identity, and does not authenticate the third-party
files against Smithsonian's master. Outputs are scaled to source coordinates.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
if len(sys.argv)!=3:raise SystemExit('usage: compare_smithsonian.py /path/to/scene.gltf /path/to/scene.bin')
gltf,raw=map(Path,sys.argv[1:]);base=Path(__file__).resolve().parent;obj=base/'assets/woolly-mammoth-150k.obj'
files=[gltf,raw,obj];expected=['eb054c6bd289c86c1bb651f2a59abca82ffe6137402b1b127051379c4694bf5d','9174930eb3995d8aa18c341bce13ac8f8be1d6894d522534b24a2eefb5c9c89c','be6dc1dddd27fa9f75a1fed1fa84b9d193b180ac51746fffc3acfafc984046e6']
if [hashlib.sha256(x.read_bytes()).hexdigest() for x in files]!=expected:raise SystemExit('Inputs do not match pinned copies')
j=json.loads(gltf.read_text());data=raw.read_bytes();parts=[]
for m in j['meshes']:
 for prim in m['primitives']:
  a=j['accessors'][prim['attributes']['POSITION']];v=j['bufferViews'][a['bufferView']]
  if a['componentType']!=5126 or a['type']!='VEC3' or v.get('byteStride',12)!=12:raise SystemExit('Unexpected glTF accessor')
  positions=np.frombuffer(data,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3)
  parts.append(positions.astype(np.float64)/1000)
smith=np.concatenate(parts);points=[]
with obj.open() as f:
 for line in f:
  if line.startswith('v '):points.append([float(x) for x in line.split()[1:4]])
reference=np.asarray(points,dtype=np.float64)
if len(smith)!=105215 or len(reference)!=49594:raise SystemExit('Unexpected vertex counts')
measure=[]
for a,b in ((reference,smith),(smith,reference)):
 d=cKDTree(b).query(a)[0];measure.append({'mean':float(d.mean()),'median':float(np.median(d)),'p95':float(np.quantile(d,.95)),'max':float(d.max())})
print(json.dumps({'status':'approximate shape corroboration only; not a direct master match or rights clearance','vertices':[len(reference),len(smith)],'bounds':[reference.min(0).tolist(),reference.max(0).tolist(),smith.min(0).tolist(),smith.max(0).tolist()],'nearest_vertex_distance_in_obj_units':measure,'sha256':expected},indent=2))
