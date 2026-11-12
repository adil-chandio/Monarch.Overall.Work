"""Experimental Blender 3D IK gait, not an identity-matched final.

Starts from the generic MPFB rig_probe.blend. Fitted generic shoes, a two-bone
IK chain and world-space stance targets test the *mechanism* of foot planting.
A planted control is not proof that the shoe mesh contacts the floor: inspect
rendered motion, deformation, knee direction and mesh clearance separately.
See 3d-pilot/README.md for dependencies and asset-license caveats.
"""
import math
import os
from pathlib import Path
import bpy
from mathutils import Vector

root=Path(os.environ.get('PILOT_OUTPUT','/tmp/monarch-3d-probe'))
os.makedirs(root,exist_ok=True)
user_dir=os.environ.get('MPFB_USER_DIR','/tmp/mafia-mpfb-user')
bpy.utils.extension_path_user=lambda *args,**kwargs:user_dir
bpy.ops.preferences.addon_enable(module='mpfb')
from mpfb.services.humanservice import HumanService

bpy.ops.wm.open_mainfile(filepath=str(root/'rig-probe.blend'))
rig=bpy.data.objects['Human.rig']; human=bpy.data.objects['Human']
shoe_asset=Path(os.environ['MAKEHUMAN_ASSETS'])/'clothes/shoes01/shoes01.mhclo'
shoe=HumanService.add_mhclo_asset(str(shoe_asset),human,asset_type='Clothes',material_type='NONE',subdiv_levels=0)
mat=bpy.data.materials.new('Untextured black shoe');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.012,.009,.008,1);bsdf.inputs['Roughness'].default_value=.42
shoe.data.materials.clear();shoe.data.materials.append(mat)
# Experimental rigid shoes: a shoe is a solid prop, not stretchy clothing.
# Assign each half of this symmetric shoe asset entirely to its foot bone.
# This prevents toe-bone skinning from bending the leather, but ankle fit and
# ground penetration still need explicit frame-by-frame mesh inspection.
shoe.vertex_groups.clear()
for side,sign in [('Left',1),('Right',-1)]:
 group=shoe.vertex_groups.new(name='mixamorig:'+side+'Foot')
 indices=[v.index for v in shoe.data.vertices if sign*v.co.x>0]
 if not indices: raise ValueError('Shoe mesh did not split across the rig center')
 group.add(indices,1.0,'REPLACE')

scene=bpy.context.scene; scene.render.fps=24;scene.frame_start=1;scene.frame_end=72
speed=.85; period=24; stance=.64; height=.12

def empty(name):
 ob=bpy.data.objects.new(name,None);scene.collection.objects.link(ob);ob.empty_display_type='SPHERE';ob.empty_display_size=.05;return ob

def walk(frame,offset):
 # Controls are fixed in world coordinates throughout stance; on swing they
 # travel smoothly to the following step. This is not full-body dynamics.
 x=(frame-1)/period+offset; cycle=math.floor(x);phase=x-cycle
 touchdown=(cycle-offset)*period/24
 y0=-speed*touchdown-speed*(period/24)*.27
 if phase<stance:return y0,0.0
 u=(phase-stance)/(1-stance);smooth=u*u*(3-2*u)
 return y0-speed*(period/24)*smooth,height*math.sin(math.pi*u)

for side in ('Left','Right'):
 leg=rig.pose.bones['mixamorig:'+side+'Leg']; foot=rig.pose.bones['mixamorig:'+side+'Foot']
 target=empty(side+' ankle IK target');pole=empty(side+' knee pole');rotation=empty(side+' foot level')
 target['note']='stance control only; evaluate actual mesh clearance before claiming contact'
 ik=leg.constraints.new('IK');ik.target=target;ik.pole_target=pole;ik.chain_count=2;ik.pole_angle=0
 rest=rig.data.bones[foot.name].matrix_local.to_quaternion(); rotation.rotation_mode='QUATERNION';rotation.rotation_quaternion=rest
 cr=foot.constraints.new('COPY_ROTATION');cr.target=rotation;cr.owner_space='WORLD';cr.target_space='WORLD'
 x=.198 if side=='Left' else -.198
 offset=0 if side=='Left' else .5
 for frame in range(1,73):
  t=(frame-1)/24; y,z=walk(frame,offset)
  # Rigid-shoe test mesh sits ~0.074 below ankle in this rig; studio
  # floor is z=-0.02. This is a calibrated test, not a general solver.
  target.location=(x,y,.054+z);target.keyframe_insert('location',frame=frame)
  pole.location=(x,-speed*t-2,.5);pole.keyframe_insert('location',frame=frame)
# Aim upper arms and forearms toward conservative anatomical targets in rig
# space. Keyframe rotations rather than an unconstrained, inverted elbow pole.
# This remains handcrafted blocking, not validated performance capture.
from mathutils import Matrix
for frame in range(1,73):
 scene.frame_set(frame);t=(frame-1)/24;rig.location=(0,-speed*t,-.065+.014*math.cos(4*math.pi*t));rig.keyframe_insert('location',frame=frame)
 for side,sign in [('Left',1),('Right',-1)]:
  upper=rig.pose.bones['mixamorig:'+side+'Arm'];lower=rig.pose.bones['mixamorig:'+side+'ForeArm']
  swing=sign*.12*math.sin(2*math.pi*t)
  for bone,direction in ((upper,Vector((sign*.04,swing,-.25))), (lower,Vector((sign*.012,swing*.7,-.26)))):
   bpy.context.view_layer.update()
   rest=bone.bone;rest_dir=rest.tail_local-rest.head_local
   q=rest_dir.rotation_difference(direction)
   bone.matrix=Matrix.Translation(bone.head) @ (q @ rest.matrix_local.to_quaternion()).to_matrix().to_4x4()
   bone.rotation_mode='QUATERNION';bone.keyframe_insert('rotation_quaternion',frame=frame)

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=scene.camera;cam.data.type='ORTHO';cam.data.ortho_scale=3.1
for f in (1,72):
 y=-speed*(f-1)/24;cam.location=(4.5,y,1.35);aim(cam,(0,y,1.0));cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
scene.render.resolution_x=640;scene.render.resolution_y=480;scene.cycles.samples=8;scene.render.image_settings.file_format='PNG'
for obj in (rig,cam):
 if obj.animation_data and obj.animation_data.action:
  for curve in obj.animation_data.action.fcurves:
   for key in curve.keyframe_points:key.interpolation='LINEAR'
for ob in [bpy.data.objects[n] for n in ('Left ankle IK target','Right ankle IK target','Left knee pole','Right knee pole')]:
 for curve in ob.animation_data.action.fcurves:
  for key in curve.keyframe_points:key.interpolation='LINEAR'
scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(root/'ik-walk-test.blend'))
for frame in (1,7,13,19,25,31):
 scene.frame_set(frame);scene.render.filepath=str(root/f'ik-walk-{frame:03d}.png');bpy.ops.render.render(write_still=True)
 print('RENDERED',frame,flush=True)
print('Gait mechanism test only: assess mesh/ground and likeness, not final',flush=True)
os._exit(0)
