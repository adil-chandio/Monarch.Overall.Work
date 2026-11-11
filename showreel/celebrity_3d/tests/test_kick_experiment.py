"""Integration test with the real CC0 armature; run with bpy Python."""
import sys, math
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from football_physics import Ball
from kick_experiment import bake, install_kick
from action_timeline import apply, Clip

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/human.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.location=(43.8,.1,0);rig.rotation_euler.z=math.pi
apply(rig,[Clip('Idle_Loop_Rig',16,24,.2,True)])
install_kick(rig)
initial=Ball((43.42,.39,.11));scene=bpy.context.scene
scene.frame_set(18*24);bpy.context.view_layer.update();before=rig.pose.bones['DEF-toe.R'].tail.copy()
scene.frame_set(round(19.15*24));bpy.context.view_layer.update();after=rig.pose.bones['DEF-toe.R'].tail.copy()
assert (before-after).length > .1, 'render-evaluated foot did not move'
scene.frame_set(23,subframe=.25)
states,hits=bake(scene,rig,initial)
assert scene.frame_current==23 and abs(scene.frame_subframe-.25)<1e-6, 'bake must restore the caller frame'
assert len(states)==8*24+1
assert len(hits)==1 and 18.7<hits[0]<19.2, hits
assert states[2*24].position==initial.position, 'ball moved before the foot arrived'
assert states[-1].position[1]>initial.position[1]+1, 'ball did not respond to contact'
assert all(s.position[2]>=.11 for s in states), 'ball penetrated ground'
again,more_hits=bake(scene,rig,initial)
assert again==states and more_hits==hits, 'simulation is not reproducible'
print('PASS: real rig contact, delayed ball movement, ground plane, deterministic bake, frame restore',hits)
