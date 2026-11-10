"""Recreate the illustrative fragment from the unverified third-party reference.

This deliberately chooses a mesh component, not a documented archaeological
specimen. A fabricated setting, material and orientation are applied in scene.
"""
from pathlib import Path
import hashlib
import numpy as np
import trimesh
base=Path(__file__).resolve().parent
source=base.parent/'skeleton-reference/assets/woolly-mammoth-150k.obj'
out=base/'assets/reference-fragment.glb'
expected='be6dc1dddd27fa9f75a1fed1fa84b9d193b180ac51746fffc3acfafc984046e6'
if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise SystemExit('Reference source changed')
m=trimesh.load(source,force='mesh',process=False)
m.merge_vertices(merge_tex=True,merge_norm=True)
parts=sorted(m.split(only_watertight=False),key=lambda c:len(c.faces),reverse=True)
if len(parts)!=3 or len(parts[2].faces)!=2382 or len(parts[2].vertices)!=1191:raise SystemExit('Unexpected component topology')
part=parts[2]
if not np.allclose(part.bounds,[[-.2,.52,.63],[.32,1.13,1.04]],atol=.012):raise SystemExit('Unexpected component location')
part.apply_translation(-part.bounds.mean(axis=0));out.parent.mkdir(parents=True,exist_ok=True);part.export(out)
print('wrote',out,'sha256',hashlib.sha256(out.read_bytes()).hexdigest())
