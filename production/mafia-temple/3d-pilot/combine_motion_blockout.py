"""Combine the genuine 3D IK rig test with the 3D temple blockout.

This is NOT a final film: the character is generic, the gait/mesh are not
approved, the architecture is a coarse blockout and there is no facial rig.
Requires the two local .blend files produced by the other research scripts.
"""
import os
from pathlib import Path
import bpy
from mathutils import Vector

out=Path(os.environ.get('PILOT_OUTPUT','/tmp/monarch-3d-probe'))
bpy.ops.wm.open_mainfile(filepath=str(out/'temple-blockout.blend'))
with bpy.data.libraries.load(str(out/'ik-walk-test.blend'),link=False) as (src,dst):
 dst.objects=[name for name in src.objects if name.startswith('Human') or name.endswith(' IK target') or name.endswith(' knee pole') or name.endswith(' foot level') or name.endswith(' wrist target') or name.endswith(' elbow pole')]
for obj in dst.objects:
 if obj and not obj.users_collection:bpy.context.scene.collection.objects.link(obj)
rig=bpy.data.objects['Human.rig'];s=bpy.context.scene
# Studio IK floor is z=-0.020; blockout pavement top is z=0.012.
# Lift rig and its world-space controls together; this does not itself prove
# contact, which must be measured on evaluated footwear vertices.
for obj in [rig]+[x for x in dst.objects if x and (x.name.endswith(' IK target') or x.name.endswith(' knee pole'))]:
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   if fc.data_path=='location' and fc.array_index==2:
    for key in fc.keyframe_points:
     key.co.y+=.032;key.handle_left.y+=.032;key.handle_right.y+=.032
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Tracking walk camera';cam.data.type='ORTHO';cam.data.ortho_scale=3.8
for frame in (1,72):
 y=-.85*(frame-1)/24
 # Keep camera inside the posts and lanterns, avoiding foreground occlusion.
 cam.location=(2.0,y+.35,1.35);cam.rotation_euler=(Vector((0,y,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
for fcurve in cam.animation_data.action.fcurves:
 for key in fcurve.keyframe_points:key.interpolation='LINEAR'
s.camera=cam;s.render.engine='CYCLES';s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=72
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'temple-walk-blockout.blend'))
for frame in (1,13,25):
 s.frame_set(frame);s.render.image_settings.file_format='PNG';s.render.filepath=str(out/f'temple-walk-{frame:03}.png');bpy.ops.render.render(write_still=True);print('PREVIEW',frame,flush=True)
# To actually render 72 native 3D frames, opt in; no external services involved.
if os.environ.get('RENDER_TEST_ANIMATION')=='1':
 s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM';s.render.filepath=str(out/'temple-walk-draft.mp4');bpy.ops.render.render(animation=True);print('TEST_ANIMATION_FINISHED',flush=True)
os._exit(0)
