"""Measure a generic IK gait's evaluated shoe mesh; no final-quality claim.

Runs in Blender Python after build_ik_walk_test.py. Measures each rigid shoe's
lowest point vs. the studio plane during keyed stance, ankle-target residual,
and stance control drift. It does not validate knee anatomy, visual realism,
identity, every sole vertex, collision with pants, or a different scene floor.
"""
import json, math, os
from pathlib import Path
import bpy

root=Path(os.environ.get('PILOT_OUTPUT','/tmp/monarch-3d-probe'))
bpy.ops.wm.open_mainfile(filepath=str(root/'ik-walk-test.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['Human.rig'];shoe=next(o for o in bpy.data.objects if 'shoes01' in o.name)
report={'floor_z':-.02,'frames':72,'note':'Studio-only numeric screen; inspect entire rendered animation and mesh for quality.', 'sides':{}}
for side,sign,offset in [('Left',1,0),('Right',-1,.5)]:
 clearances=[];errors=[];drifts=[];previous=None
 for frame in range(1,73):
  scene.frame_set(frame);dep=bpy.context.evaluated_depsgraph_get();r=rig.evaluated_get(dep);o=shoe.evaluated_get(dep);mesh=o.to_mesh()
  z=[(o.matrix_world@v.co).z for v in mesh.vertices if sign*(o.matrix_world@v.co).x>0];o.to_mesh_clear()
  if not z:raise ValueError('Could not separate shoes')
  foot=r.pose.bones['mixamorig:'+side+'Foot'];ankle=r.matrix_world@foot.head;target=bpy.data.objects[side+' ankle IK target'].matrix_world.translation.copy()
  phase=((frame-1)/24+offset)%1; is_stance=phase<.64
  if is_stance:
   clearances.append(min(z)+.02);errors.append((ankle-target).length)
   if previous and previous[0]==frame-1 and previous[1]:drifts.append((target-previous[2]).length)
  previous=(frame,is_stance,target)
 report['sides'][side]={'stance_frames':len(clearances),'min_clearance_m':round(min(clearances),5),'max_clearance_m':round(max(clearances),5),'max_ankle_target_error_m':round(max(errors),5),'max_consecutive_stance_control_drift_m':round(max(drifts),5)}
print(json.dumps(report,indent=2),flush=True)
os._exit(0)
