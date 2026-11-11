"""Experimental hand-keyed kick and foot-proxy-driven ball bake.

This is blocking, not motion capture, IK, or a validated athletic performance.
"""
import math
from football_physics import Ball, Parameters, step

# Absolute timeline seconds and local right-thigh x rotation in radians.
KEYS=((16.,0.),(18.1,0.),(18.55,-.48),(18.74,-.48),(19.13,.58),(19.45,.34),(20.1,0.),(24.,0.))

def angle_at(t):
    if t<=KEYS[0][0]:return KEYS[0][1]
    for (a,x),(b,y) in zip(KEYS,KEYS[1:]):
        if t<=b:
            u=(t-a)/(b-a);u=u*u*(3-2*u)
            return x+(y-x)*u
    return KEYS[-1][1]

def install_kick(rig,fps=24):
    """Add a sampled additive quaternion action so Blender renders the pose.

    Key every output frame: the input easing is deterministic and interpolation
    between frames supports physics substeps without render-time pose overrides.
    """
    import bpy
    action=bpy.data.actions.new('Experimental_Kick_Offset')
    path='pose.bones["DEF-thigh.R"].rotation_quaternion'
    curves=[action.fcurves.new(data_path=path,index=i) for i in range(4)]
    for frame in range(16*fps,24*fps+1):
        a=angle_at(frame/fps);values=(math.cos(a/2),math.sin(a/2),0.,0.)
        for fc,value in zip(curves,values):
            point=fc.keyframe_points.insert(frame,value,options={'FAST'})
            point.interpolation='LINEAR'
    for fc in curves:fc.update()
    track=rig.animation_data.nla_tracks.new();track.name='Experimental kick offset'
    strip=track.strips.new(action.name,16*fps,action)
    strip.blend_type='COMBINE';strip.extrapolation='NOTHING'
    return strip

def bake(scene,rig,initial,fps=24,substeps=8):
    """Sample the actual rig at each physics step, bake ball and contact events."""
    import bpy
    old_frame,old_subframe=scene.frame_current,scene.frame_subframe
    dt=1/(fps*substeps);start=16.;frames=8*fps;ball=initial;states=[ball];hits=[]
    def foot_at(t):
        f=t*fps;whole=math.floor(f);scene.frame_set(whole,subframe=f-whole)
        bpy.context.view_layer.update()
        toe=rig.matrix_world @ rig.pose.bones['DEF-toe.R'].tail
        # Raise spherical proxy center above the toe tip, which lies on the turf.
        return (toe.x,toe.y,toe.z+.075)
    previous=foot_at(start)
    for i in range(frames*substeps):
        t=start+(i+1)*dt;foot=foot_at(t)
        velocity=tuple((a-b)/dt for a,b in zip(foot,previous));previous=foot
        ball,hit=step(ball,dt,Parameters(),foot,velocity)
        if hit:hits.append(t)
        if (i+1)%substeps==0:states.append(ball)
    scene.frame_set(old_frame,subframe=old_subframe)
    return states,hits
