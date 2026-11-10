"""Experimental automatic rig on a CC-BY static mammoth.

This is a technical rig experiment, NOT a realistic performance or final film.
Blender 4.2 bpy, NumPy and the authored .blend asset are required. File loading
is performed with scripts disabled. Export uses the texture from the input asset.
"""
import math, os, sys
from pathlib import Path
import bpy
from mathutils import Matrix

B=Path(__file__).resolve().parent
source=B/'assets/SDPM-Wooly-Mammoth.blend'
out=B/'assets/SDPM-Mammoth-Experimental-Rig.glb'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
mesh=next(o for o in bpy.data.objects if o.type=='MESH')
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
# Bake the artist's object transform; preserves appearance while placing the
# rig and geometry in the same world-space coordinate system.
mesh.data.transform(mesh.matrix_world);mesh.matrix_world=Matrix.Identity(4)
material=bpy.data.materials.new('PBR conversion of SDPM colour texture');material.use_nodes=True
nodes=material.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');principled=nodes.new('ShaderNodeBsdfPrincipled');texture=nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images['Image_0']
principled.inputs['Roughness'].default_value=.86
material.node_tree.links.new(texture.outputs['Color'],principled.inputs['Base Color']);material.node_tree.links.new(principled.outputs['BSDF'],output.inputs['Surface'])
mesh.data.materials.clear();mesh.data.materials.append(material)

# Bone placements are coarse estimates on this one model; they have not been
# checked by a vertebrate anatomist or matched to the specimen's original rig.
# Four low-elevation connected components of the source mesh are feet. The
# fifth low component at (-.63,-.50) is the trunk tip, NOT a fifth leg.
feet=[(-.206,-.325),(-.203,-.544),(.498,-.213),(.427,-.441)]
bpy.context.scene.render.fps=30
arm=bpy.data.armatures.new('ExperimentalMammothRig');rig=bpy.data.objects.new('ExperimentalMammothRig',arm);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=arm.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=arm.edit_bones[parent]
    return b
bone('root',(0,-.42,.70),(0,-.42,1.0))
for i,(x,y) in enumerate(feet):
    bone('upper'+str(i),(x,y,.64),(x,y,.30),'root')
    bone('lower'+str(i),(x,y,.30),(x,y,.04),'upper'+str(i))
    bone('foot'+str(i),(x,y,.04),(x,y,-.04),'lower'+str(i))
bone('trunk_upper',(-.55,-.50,.78),(-.67,-.50,.43),'root')
bone('trunk_lower',(-.67,-.50,.43),(-.64,-.50,.10),'trunk_upper')
bpy.ops.object.mode_set(mode='OBJECT')

# Spatial weights are provisional. Each vertex has normalised weights and at
# most four influences. The mesh's posing needs manual topology/weight review.
names=['root']+[f'{side}{i}' for i in range(4) for side in ('upper','lower','foot')]+['trunk_upper','trunk_lower']
mesh.vertex_groups.clear()
groups={n:mesh.vertex_groups.new(name=n) for n in names}
def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
for vert in mesh.data.vertices:
    x,y,z=vert.co
    near=min(range(4),key=lambda i:((x-feet[i][0])/.16)**2+((y-feet[i][1])/.13)**2)
    # Below the body, partition by nearest foot; fade to the root toward the
    # torso. Bounds exclude the trunk and tusks; still needs manual review.
    leg=smooth((.62-z)/.18)*smooth((x+.43)/.12)*smooth((.76-x)/.12)
    # Trunk tip lies off centre on this source model. Avoid the two tusks.
    trunk=smooth((-.48-x)/.10)*smooth((.80-z)/.20)*math.exp(-((y+.50)/.12)**4)
    trunk=min(trunk,1-leg)
    low=smooth((.42-z)/.20);foot=smooth((.14-z)/.10)
    trunk_low=smooth((.52-z)/.22)
    w={'root':1-leg-trunk, f'upper{near}':leg*(1-low),f'lower{near}':leg*low*(1-foot),f'foot{near}':leg*low*foot,
       'trunk_upper':trunk*(1-trunk_low),'trunk_lower':trunk*trunk_low}
    w=dict(sorted(((k,v) for k,v in w.items() if v>1e-6),key=lambda kv:kv[1],reverse=True)[:4]);total=sum(w.values())
    for name,value in w.items():groups[name].add([vert.index],value/total,'REPLACE')
mesh.parent=rig;mod=mesh.modifiers.new('Experimental skin','ARMATURE');mod.object=rig

# Independent authored actions. No ground contact or world translation is
# solved here. They are deliberately small test motions, NOT approved walk/gait.
rig.animation_data_create()
def action(name):
    a=bpy.data.actions.new(name);rig.animation_data.action=a;return a
for pb in rig.pose.bones:pb.rotation_mode='XYZ'
a=action('Idle_Experimental')
for frame in range(1,122,10):
    phase=(frame-1)/120*2*math.pi
    for n,amp in [('trunk_upper',.035),('trunk_lower',.055)]:
        pb=rig.pose.bones[n];pb.rotation_euler=(0,0,amp*math.sin(phase+(0.4 if n.endswith('lower') else 0)));pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=n)
for frame in (1,121):
    for n in ('trunk_upper','trunk_lower'):
        pb=rig.pose.bones[n];pb.rotation_euler=(0,0,0);pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=n)
# Keep the idle action as an NLA strip for glTF export.
rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='Idle_Experimental';track.strips.new('Idle_Experimental',1,a)
a=action('WalkInPlace_Experimental')
# A kinematic two-link plane solution approximates planted feet on flat ground
# IF a consumer translates the root in -X at STRIDE/(PERIOD*STANCE) m/s.
# This is not a physics simulation and cannot solve uneven terrain.
phases=[.25,.75,0,.5];stride=.14;stance=.75;period=72
l1=.34;l2=.26;hip_drop=.015
for frame in range(1,period+2):
    u=(frame-1)/period
    root=rig.pose.bones['root'];root.location=(0,-hip_drop,0);root.keyframe_insert(data_path='location',frame=frame,group='root')
    for i,offset in enumerate(phases):
        q=(u+offset)%1
        if q<stance:
            dx=-stride/2+stride*q/stance;lift=0
        else:
            v=(q-stance)/(1-stance);dx=stride/2-stride*(v*v*(3-2*v));lift=.035*math.sin(math.pi*v)
        h=l1+l2-hip_drop-lift;r=math.hypot(dx,h)
        if r>l1+l2:raise ValueError('unreachable leg target')
        phi=math.atan2(-dx,h)
        upper=phi+math.acos(max(-1,min(1,(l1*l1+r*r-l2*l2)/(2*l1*r))))
        lower=phi-math.acos(max(-1,min(1,(l2*l2+r*r-l1*l1)/(2*l2*r))))
        pb=rig.pose.bones['upper'+str(i)];pb.rotation_euler=(0,0,upper);pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name)
        pb=rig.pose.bones['lower'+str(i)];pb.rotation_euler=(0,0,lower-upper);pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name)
        pb=rig.pose.bones['foot'+str(i)];pb.rotation_euler=(0,0,-lower);pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name)
    for n,amp in [('trunk_upper',.03),('trunk_lower',.045)]:
        pb=rig.pose.bones[n];pb.rotation_euler=(0,0,amp*math.sin(2*math.pi*u));pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=n)
# Linear interpolation preserves the sampled target more faithfully than bezier.
for curve in a.fcurves:
    for key in curve.keyframe_points:key.interpolation='LINEAR'
rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='WalkInPlace_Experimental';track.strips.new('WalkInPlace_Experimental',1,a)
# NLA tracks should not be blended into the bind-pose at export.
for track in rig.animation_data.nla_tracks:track.mute=True
bpy.context.scene.frame_set(1)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_animations=True,export_animation_mode='NLA_TRACKS')
print('Experimental export:',out,flush=True)
# Some isolated headless bpy wheel/runtime combinations crash during teardown;
# exit after successful synchronous export instead of interpreting teardown as QC.
os._exit(0)
