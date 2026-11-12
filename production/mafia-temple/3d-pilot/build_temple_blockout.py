"""Procedural 3D temple environment blockout, without image-to-video.

This is a geometry/lighting test, not a finished realistic environment. No
photographs or recognizable assets are used. Requires Blender Python 4.2.
Output lives only in the private PILOT_OUTPUT directory.
"""
import math, os, random
from pathlib import Path
import bpy
from mathutils import Vector

out=Path(os.environ.get('PILOT_OUTPUT','/tmp/monarch-3d-probe'));out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
random.seed(71)
def mat(name,c,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
wood=mat('Dark cedar',(.072,.037,.022),.7);roof=mat('Aged roof tile',(.035,.045,.052),.55);plaster=mat('Warm plaster',(.17,.13,.095),.85);stone=mat('Wet stone',(.075,.09,.10),.3)
emit=bpy.data.materials.new('Warm paper lantern');emit.use_nodes=True;p=emit.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,.56,.19,1);p.inputs['Emission Color'].default_value=(1,.3,.065,1);p.inputs['Emission Strength'].default_value=2.0

def box(name,loc,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o

def roof_mesh(name,x,y,z,w,d,peak):
 # Two sloping roof planes, each with thickness: real geometry, no background image.
 verts=[(-w/2,-d/2,0),(w/2,-d/2,0),(-w/2,d/2,0),(w/2,d/2,0),(0,-d/2,peak),(0,d/2,peak)]
 verts=[(x+a,y+b,z+c) for a,b,c in verts];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[(0,1,4),(2,5,3),(0,4,5,2),(1,3,5,4)]);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(roof);return o

def lantern(x,y):
 box('Lantern base',(x,y,.1),(.52,.52,.2),stone);box('Lantern column',(x,y,.55),(.18,.18,.9),stone);box('Lit lantern',(x,y,1.19),(.42,.42,.55),emit);box('Lantern cap',(x,y,1.53),(.56,.56,.1),roof)
 bpy.ops.object.light_add(type='POINT',location=(x,y,1.2));l=bpy.context.object;l.data.energy=38;l.data.color=(1,.48,.18);l.data.shadow_soft_size=.55

box('Continuous ground',(0,0,-.15),(30,35,.3),stone)
for x in range(-10,11):
 for y in range(-14,15):
  s=1.05;box('Paving',((x+.5)*s,(y+.5)*s,.003),(s-.025,s-.025,.018),stone)
# Temple central hall and porch.
box('Temple hall',(0,-7,1.9),(9,4,3.8),plaster)
for x in (-4.2,-2.1,0,2.1,4.2):box('Temple front timber',(x,-4.94,2),(.20,.25,4),wood)
for z in (.35,2.8,3.75):box('Temple front beam',(0,-4.94,z),(9,.3,.2),wood)
box('Temple door',(0,-4.77,1.45),(2.0,.18,2.9),wood)
roof_mesh('Temple roof',0,-7,3.85,10.6,5.3,1.6)
# Gate with real pillars, lintels, and pitched tiled roof.
for x in (-2.4,2.4):box('Gate post',(x,1,1.6),(.34,.4,3.2),wood)
box('Gate lintel',(0,1,2.85),(5.3,.46,.3),wood)
roof_mesh('Gate roof',0,1,3.15,6.0,1.5,.65)
# Distant street buildings line approach to gate.
for side in (-1,1):
 for y in (4,8,12):
  x=side*4.5;box('Street building',(x,y,1.5),(3.2,3.4,3),plaster)
  for dx in (-1.5,1.5):box('Street vertical timber',(x+dx,y,1.55),(.15,3.5,3.1),wood)
  roof_mesh('Street roof',x,y,3.05,3.8,3.8,.65)
for x in (-3.1,3.1):
 for y in (-4,-1,4,9):lantern(x,y)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.015,.028,.05,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
bpy.ops.object.light_add(type='AREA',location=(0,-1,8));area=bpy.context.object;area.data.energy=800;area.data.color=(.32,.48,1);area.data.size=9

def camera(name,loc,target,lens):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
cam_gate=camera('Gate locked camera',(0,9,2.4),(0,-3,1.65),35)
cam_aerial=camera('Aerial camera',(0,7,14),(0,-3,0),28)
s=bpy.context.scene;s.camera=cam_gate;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'temple-blockout.blend'))
for cam in (cam_gate,cam_aerial):
 s.camera=cam;s.render.filepath=str(out/(cam.name.replace(' ','-')+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',cam.name,flush=True)
os._exit(0)
