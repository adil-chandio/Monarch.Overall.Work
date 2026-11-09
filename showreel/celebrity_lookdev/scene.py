"""Asset integration/look-development experiment, not a finished film.

Imports a licensable articulated character and scanned furniture; does not use
reference images as plates. Intended for lighting and motion evaluation.
"""
import bpy,math,sys,os
from pathlib import Path
from mathutils import Vector
import argparse
p=argparse.ArgumentParser();p.add_argument('--assets',default='/home/user/celebrity-lookdev-assets');p.add_argument('--output',default='/home/user/celebrity-lookdev');p.add_argument('--samples',type=int,default=8);args=p.parse_args();assets=Path(args.assets);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('World');s.world.color=(.11,.09,.14)
def material(name,c,rough=.6,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m
M={x:material(x,c,metal=.7 if x=='metal' else 0,emission=.35 if x=='sun' else 0) for x,c in {'floor':(.14,.105,.085),'wall':(.19,.14,.18),'dark':(.045,.04,.06),'metal':(.41,.28,.16),'glass':(.3,.23,.29),'sun':(.9,.55,.34),'silhouette':(.08,.07,.1)}.items()}
def box(name,loc,dim,m,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[m])
 if bev:mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bev;mod.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def light(pos,target,power,size,col):
 bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.data.color=col;l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
def place(file,xyz,scale=1,rotation=0):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(assets/file));added=set(bpy.context.scene.objects)-before
 roots=[o for o in added if not o.parent]
 for o in roots:o.location+=Vector(xyz);o.scale*=scale;o.rotation_euler.z+=rotation
 return added
# Layered, physically lit interior with a warm horizon and city geometry.
box('floor',(0,0,-.12),(12,12,.24),'floor');box('rear wall',(0,3.5,2.5),(12,.18,5),'wall');box('left wall',(-6,0,2.5),(.18,7,5),'wall')
box('warm sky',(0,3.39,2.5),(8,.05,3.5),'sun')
for i in range(32):
 x=-3.9+i*.25;height=.4+(i*53%26)*.055;box('distant tower',(x,3.3,.82+height/2),(.18,.1,height),'silhouette')
 for j in range(int(height/.3)):
  if (i+j)%3==0:box('city window',(x,3.23,.95+j*.25),(.025,.025,.04),'sun')
for x in (-4,-2,0,2,4):box('window mullion',(x,3.16,2.5),(.08,.12,3.6),'dark')
for y in (-3,-2,-1,0,1,2):box('floor inlay',(0,y,.005),(12,.014,.01),'metal')
place('sofa.glb',(-1.3,1.35,0));place('armchair.glb',(2.3,1.1,0),rotation=-.45);place('coffee-table.glb',(.1,-.2,0));place('bookcase.glb',(-4,2.6,0));place('nightstand.glb',(3.6,2.4,0))
# Practical fixtures and rim/key lighting.
box('lamp base',(3.6,2.4,.9),(.25,.25,.5),'metal',.06);box('lampshade',(3.6,2.4,1.27),(.5,.5,.3),'sun',.08)
light((-3,-4,4.2),(0,0,1.2),350,4,(1,.72,.52));light((3,2.6,4.3),(0,0,1.2),550,3,(1,.48,.28));light((3,-3,3),(0,0,1.1),160,3,(.48,.6,1))
# Rocketbox: use exactly one outfit, not overlapping clothing meshes.
objs=place('ryan.glb',(.55,0,0));rig=next(o for o in objs if o.type=='ARMATURE')
for o in objs:
 if o.type=='MESH' and o.name in ('Outfit_formal','Skin_formal','Top_shirt','Skin_shirt','Top_tee','Skin_tee','Trousers','Shoes'):o.hide_render=True
rig.animation_data_create();rig.animation_data.action=bpy.data.actions['Phone_Rig'];
# Rotate the entire rig, not individual skinned meshes.
rig.rotation_euler.z=math.pi
bpy.ops.object.camera_add(location=(4.8,-7.5,3.1));camera=bpy.context.object;camera.rotation_euler=(Vector((.1,.6,1.35))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=42;s.camera=camera
for frame in (1,100,200,350):
 s.frame_set(frame);s.render.image_settings.file_format='PNG';s.render.filepath=str(out/f'look-{frame}.png');bpy.ops.render.render(write_still=True)
