"""Cut two illustrative, open-edged props from an unverified 3D reference.
These spatial crops are NOT identified sequenced specimens or fracture evidence.
"""
from pathlib import Path
import hashlib
import numpy as np
import trimesh
base=Path(__file__).resolve().parent
src=base.parent/'skeleton-reference/assets/woolly-mammoth-150k.obj'
if hashlib.sha256(src.read_bytes()).hexdigest()!='be6dc1dddd27fa9f75a1fed1fa84b9d193b180ac51746fffc3acfafc984046e6':raise SystemExit('Unexpected source')
mesh=trimesh.load(src,force='mesh',process=False);mesh.merge_vertices(merge_tex=True,merge_norm=True)
specs=[('mainland-prop',[.1,-1.1,0],[.7,-.55,.5]),('island-prop',[.1,-1.1,-2.1],[.7,-.55,-1.35])]
for name,lo,hi in specs:
 inside=np.all((mesh.vertices>=lo)&(mesh.vertices<=hi),axis=1);faces=inside[mesh.faces].all(axis=1)
 subset=mesh.submesh([np.flatnonzero(faces)],append=True)
 pieces=sorted(subset.split(only_watertight=False),key=lambda p:len(p.faces),reverse=True)
 if not pieces or len(pieces[0].faces)<600:raise SystemExit('Unexpected crop topology')
 obj=pieces[0];obj.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,0,1]));obj.apply_translation(-obj.bounds.mean(axis=0))
 out=base/'assets'/f'{name}.glb';out.parent.mkdir(exist_ok=True);obj.export(out)
 print(name,len(obj.vertices),len(obj.faces),hashlib.sha256(out.read_bytes()).hexdigest())
