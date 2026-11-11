"""Run with Blender's bpy Python; tests the actual rig, not just timing math."""
import sys
from pathlib import Path
import bpy
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from action_timeline import Clip, apply, validate

for bad in ([Clip('x',1,1)], [Clip('x',0,1,1)], []):
    try: validate(bad)
    except ValueError: pass
    else: raise AssertionError('invalid clip accepted')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/human.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
clips=[Clip('Idle_Loop_Rig',0,2.25,.2,True),Clip('Jog_Fwd_Loop_Rig',2,4.25,.2,True),Clip('Interact_Rig',4,6,.2)]
apply(rig,clips)
def pose(frame):
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    return tuple(round(v,5) for row in rig.pose.bones['DEF-upper_arm.R'].matrix for v in row)
a,b,c=pose(25),pose(65),pose(115)
assert a!=b and b!=c, 'clips did not change the skeletal pose'
assert b==pose(65), 'out-of-order frame seeking changed the result'
print('PASS: clip validation, distinct skeletal poses, deterministic seeking')
