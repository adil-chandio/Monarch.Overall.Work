"""Private, generic MPFB rig/render probe; NOT a character likeness or motion pilot.

Requires Blender 4.2 Python and MPFB 2.0.18. See README.md for paths and limits.
Never includes or transmits the user reference photo.
"""
import os, sys, time, bpy, math
from mathutils import Vector
user_dir=os.environ.get('MPFB_USER_DIR', '/tmp/mafia-mpfb-user')
os.makedirs(user_dir,exist_ok=True)
# Source checkout rather than an installed Blender extension.
bpy.utils.extension_path_user=lambda *a,**k:user_dir
bpy.ops.preferences.addon_enable(module='mpfb')
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
from mpfb.entities.objectproperties import HumanObjectProperties
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
h=HumanService.create_human()
HumanObjectProperties.set_value('gender', 1.0, entity_reference=h)
TargetService.reapply_macro_details(h)
rig=HumanService.add_builtin_rig(h,'mixamo')
def mat(name,color,rough=0.5):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; return m
skin=mat('neutral procedural skin',(0.37,0.19,0.11))
h.data.materials.clear(); h.data.materials.append(skin)
assets_dir=os.environ.get('MAKEHUMAN_ASSETS', '/tmp/makehuman-assets/base')
output_dir=os.environ.get('PILOT_OUTPUT', '/tmp/mafia-3d-probe')
os.makedirs(output_dir,exist_ok=True)
for rel,typ,color in [('clothes/male_elegantsuit01/male_elegantsuit01.mhclo','Clothes',(0.012,0.012,0.014)),('hair/short04/short04.mhclo','Hair',(0.015,0.01,0.008))]:
 obj=HumanService.add_mhclo_asset(os.path.join(assets_dir, rel),h,asset_type=typ,material_type='NONE',subdiv_levels=0)
 obj.data.materials.clear(); obj.data.materials.append(mat(typ,color))
 print('ADDED',obj.name,flush=True)
# basic studio look, deliberately no claim of identity or production asset
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-0.02)); plane=bpy.context.object; plane.data.materials.append(mat('ground',(0.03,0.03,0.03)))
world=bpy.context.scene.world; world.color=(0.08,0.08,0.08)
def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((2,-4,3.5),700,4),((-3,-1,2.6),400,3),((0,3,3),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(0,-4.6,1.65));cam=bpy.context.object;aim(cam,(0,0,1.03));cam.data.type='ORTHO';cam.data.ortho_scale=2.2
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=480;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(output_dir, 'rig-probe.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(output_dir, 'rig-probe.blend'))
t=time.time();bpy.ops.render.render(write_still=True); print('RENDER_SECONDS',round(time.time()-t,2),flush=True)
os._exit(0)
