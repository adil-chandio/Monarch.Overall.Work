"""Compare the two decoded rest-position point clouds after uniform normalization.
This is geometric corroboration, never source-master or licence verification.
Run compare_reference.mjs first; requires numpy and scipy in the project venv.
"""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
root=Path(__file__).resolve().parents[5]
base=Path(__file__).resolve().parent
rig=base/'assets/SDPM-Mammoth-Experimental-Rig.glb'
ref=base/'reference/museum-rigged-derivative.glb'
expected=['f7744f5ebba06954e4d9262d4c555f90393a3af43e285963a679f397b3a8718f','623a62621f1c6f2955fd3fe6442be8dfd34cdc94064e1bbb0c5e43e8970a1ece']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if [sha(rig),sha(ref)]!=expected:raise SystemExit('Reference files changed; re-evaluate comparison')
data=json.loads((root/'.cache/mammoth-rig-review/reference-point-clouds.json').read_text())
if data['source_sha256']!=expected:raise SystemExit('Point clouds do not match current inputs; rerun extractor')
cloud=[]
for meshes in data['clouds']:
 if len(meshes)!=1 or meshes[0]['triangles']!=56994:raise SystemExit('Unexpected topology')
 points=np.array(meshes[0]['positions'],dtype=np.float64).reshape(-1,3)
 if len(points)!=29818 or not np.isfinite(points).all():raise SystemExit('Unexpected vertices')
 lo=points.min(axis=0);hi=points.max(axis=0);cloud.append((points-(lo+hi)/2)/(hi-lo).max())
stats=[]
for a,b in ((cloud[0],cloud[1]),(cloud[1],cloud[0])):
 d=cKDTree(b).query(a)[0]
 stats.append({'mean':float(d.mean()),'median':float(np.median(d)),'p95':float(np.quantile(d,.95)),'max':float(d.max())})
if max(s['max'] for s in stats)>.0001:raise SystemExit('Normalized geometry differs beyond threshold')
print(json.dumps({'status':'geometric corroboration only; no direct source-master match or rights clearance',
 'vertices_each':29818,'triangles_each':56994,'distance_units':'fraction of longest bounding-box dimension',
 'nearest_neighbor_both_directions':stats,'sha256':expected},indent=2))
