"""Construct a 20-second Blender *blockout*, not a finished likeness film.

Extends the generic 3D rig/temple into five timed shots. Requires the locally
created temple-walk-blockout.blend from combine_motion_blockout.py. This is a
previsualization with a generic character, primitive scenery and handcrafted
motion; do not upload it as the user's requested finished film. It uses no
reference photograph. Renders representative frames; render full animation
only when explicitly enabled with RENDER_TEST_ANIMATION=1.
"""
import math, os
from pathlib import Path
import bpy
from mathutils import Vector, Euler

out=Path(os.environ.get('PILOT_OUTPUT','/tmp/monarch-3d-probe'))
bpy.ops.wm.open_mainfile(filepath=str(out/'temple-walk-blockout.blend'))
s=bpy.context.scene; rig=bpy.data.objects['Human.rig']; fps=24
# The base rig's zero-degree pole produced visibly splayed/crossed knees. On
# this rig + forward axis, pi/2 aims the bends forward instead. This is an
# experimentally measured correction, not a substitute for visual gait QA.
for side in ('Left','Right'):
 for con in rig.pose.bones['mixamorig:'+side+'Leg'].constraints:
  if con.type=='IK': con.pole_angle=math.pi/2
# Preserve existing hand-blocked arm poses before replacing the rig's action.
arms=['mixamorig:'+side+part for side in ('Left','Right') for part in ('Arm','ForeArm')]
armposes={}
for i in range(24):
 s.frame_set(1+i); armposes[i]={n:rig.pose.bones[n].rotation_quaternion.copy() for n in arms}
rig.animation_data_clear()
for name in ('Left ankle IK target','Right ankle IK target','Left knee pole','Right knee pole'):
 bpy.data.objects[name].animation_data_clear()

# Shot-dependent travel. Teleports occur only across cuts, not within a shot.
def state(f):
 if f<=96:return 10.0,.85,24,.64,.12,(f-1)/fps
 if f<=216:return 6.6,0,24,.64,.12,0
 if f<=312:return 4.0,.65,24,.64,.10,(f-217)/fps
 if f<=384:return 2.0,1.45,18,.38,.16,(f-313)/fps
 return -2.29,0,24,.64,.12,0

def foot(t,y0,speed,period,stance,height,offset):
 phase=(t*fps/period+offset);cycle=math.floor(phase);p=phase-cycle
 initial=(cycle-offset)*period/fps
 y=y0-speed*initial-speed*(period/fps)*.27
 if p<stance:return y,0
 u=(p-stance)/(1-stance);smooth=u*u*(3-2*u)
 return y-speed*(period/fps)*smooth,height*math.sin(math.pi*u)

for f in range(1,481):
 y0,speed,period,stance,height,t=state(f);y=y0-speed*t
 # Add a modest flight bounce during running; this is procedural blocking.
 bounce=.014*math.cos(4*math.pi*t*fps/period) if speed else 0
 rig.location=(0,y,-.033+bounce);rig.keyframe_insert('location',frame=f)
 for n in arms:
  bone=rig.pose.bones[n];bone.rotation_mode='QUATERNION';bone.rotation_quaternion=armposes[int((t*fps)%24)][n];bone.keyframe_insert('rotation_quaternion',frame=f)
 for side,x,offset in (('Left',.198,0),('Right',-.198,.5)):
  py,pz=foot(t,y0,speed,period,stance,height,offset)
  ankle=bpy.data.objects[side+' ankle IK target'];ankle.location=(x,py,.086+pz);ankle.keyframe_insert('location',frame=f)
  pole=bpy.data.objects[side+' knee pole'];pole.location=(x,y-2,.532);pole.keyframe_insert('location',frame=f)
 # A basic head turn; no facial expression or reconstructed likeness.
 head=rig.pose.bones['mixamorig:Head'];head.rotation_mode='XYZ'
 a=0 if f<385 else -.48*(1-min(1,(f-385)/45))
 head.rotation_euler=(0,0,a);head.keyframe_insert('rotation_euler',frame=f)

# Gate is empty; the figure reappears for the aerial shot.
for ob in [o for o in s.objects if o.type=='MESH' and o.name.startswith('Human')]:
 for f,hidden in ((1,False),(97,True),(217,False)):
  ob.hide_render=hidden;ob.keyframe_insert('hide_render',frame=f)

def camera(name,loc,target,lens=None,scale=None):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name
 o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 if scale:o.data.type='ORTHO';o.data.ortho_scale=scale
 else:o.data.lens=lens
 return o

def animate_camera(c,f,loc,target):
 c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.keyframe_insert('location',frame=f);c.keyframe_insert('rotation_euler',frame=f)

street=camera('Shot 1 rear street',(0,14,1.55),(0,10,1.0),lens=35)
for f in (1,96):
 y=10-.85*(f-1)/fps;animate_camera(street,f,(0,y+4.2,1.6),(0,y,1.1))
gate=bpy.data.objects['Gate locked camera']
aerial=bpy.data.objects['Aerial camera']
for f,z in ((217,16),(312,10)):
 animate_camera(aerial,f,(0,7,z),(0,-2.5,.1))
run=camera('Shot 4 running',(2,2.35,1.35),(0,2,1.04),scale=3.8)
for f in (313,384):
 y=2-1.45*(f-313)/fps;animate_camera(run,f,(2,y+.35,1.35),(0,y,1.04))
close=camera('Shot 5 portrait',(0,-4.50,1.55),(0,-2.29,1.56),lens=65)
for f,y in ((385,-4.50),(480,-4.0)):
 animate_camera(close,f,(0,y,1.55),(0,-2.29,1.56))
for f,cam in ((1,street),(97,gate),(217,aerial),(313,run),(385,close)):
 marker=s.timeline_markers.new('Shot '+str(f),frame=f);marker.camera=cam
for obj in s.objects:
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
s.frame_start=1;s.frame_end=480;s.render.fps=fps;s.render.engine='CYCLES';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100;s.cycles.samples=4;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'20s-temple-blockout.blend'))
for f in (1,48,97,155,217,290,313,345,384,385,430,480):
 s.frame_set(f);s.render.filepath=str(out/f'blockout-{f:03}.png');bpy.ops.render.render(write_still=True);print('BLOCKOUT_FRAME',f,flush=True)
if os.environ.get('RENDER_TEST_ANIMATION')=='1':
 s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM';s.render.filepath=str(out/'20s-blockout-silent.mp4');bpy.ops.render.render(animation=True);print('BLOCKOUT_VIDEO_COMPLETE',flush=True)
os._exit(0)
