"""Numerical regression probes; still not a substitute for animation review."""
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from showreel.celebrity_deluxe_3d.render import Film, bone_position

def visible_to_camera(scene, target, actor):
    origin = scene.camera.matrix_world.translation.copy()
    direction = target-origin
    distance = direction.length
    direction.normalize()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for _ in range(80):
        hit, point, _, _, obj, _ = scene.ray_cast(depsgraph,origin,direction,distance=distance)
        if not hit or obj in actor.meshes:
            return True
        if not obj.hide_render:
            return False
        advance=(point-origin).length+.001
        distance-=advance
        if distance<=0:
            return True
        origin=point+direction*.001
    return False


film=Film(320,2)
film.reset('bedroom')
last=None
for j in range(31):
    t=2+j*.1
    film.w.t=t;film.update_bedroom(t);bpy.context.view_layer.update()
    point=film.props['phone'].location.copy()
    assert all(math.isfinite(v) for v in point)
    if last is not None:
        assert (point-last).length < .13, ('phone discontinuity',t,(point-last).length)
    last=point
for t in (5.,7.,9.,11.):
    film.w.t=t;film.update_bedroom(t);bpy.context.view_layer.update()
    actor=film.hero.visible_actor
    gap=(actor.hand_position('Left')-film.props['phone'].location).length
    print('phone palm gap',t,round(gap,4),flush=True)
    assert gap<.09,(t,gap)
    for side in ('Left','Right'):
        hip,knee,foot=(bone_position(actor,side+x) for x in ('UpLeg','Leg','Foot'))
        assert knee.y < hip.y-.30 and abs(knee.z-hip.z)<.08
        assert foot.z<knee.z-.30 and foot.z>.05
# Rendering a frame out of order must reproduce the same solved pose.
def snapshot(t):
    film.w.t=t;film.update_bedroom(t);bpy.context.view_layer.update()
    return (film.props['phone'].location.copy(),bone_position(film.hero.visible_actor,'LeftHandIndex3').copy())
a=snapshot(7);snapshot(4);b=snapshot(7)
assert all((x-y).length<1e-5 for x,y in zip(a,b)),('pose accumulation',a,b)

film.reset('kitchen')
for t in (12.,13.5,14.5,15.5,16.5):
    film.w.t=t;film.update_kitchen(t);bpy.context.view_layer.update()
    cup=film.props['cup'].location
    assert (film.props['mug_body'].location-cup).length<1e-5
    if t in (12.,16.5):
        assert abs(cup.z-.052-1.0)<.006,('cup must rest above counter',t,cup)
    if 13.5<=t<=15.5:
        gap=(film.hero.visible_actor.hand_position('Left')-cup).length
        print('cup palm gap',t,round(gap,4),flush=True)
        assert gap<.15,(t,gap)

film.reset('street')
for actor in (film.hero,film.fan,film.press,*film.extra,*film.side_crowd):
    visible=[o.name.split('.')[0] for o in actor.visible_actor.meshes if not o.hide_render]
    assert any(p.startswith(('Outfit_','Top_')) for p in visible),visible
head_start=None
for t in (23.5,24.,24.5,25.,26.,27.,28.,41.,42.,43.):
    film.w.t=t;film.update_street(t)
    extra=Vector((1.54,-1.20,0));arm=extra+Vector((-.26,.06,1.0+.10*math.sin(t*3.3)))
    film.extra[0].pose(extra,yaw=math.pi-.1,targets={1:arm},headyaw=.1*math.sin(t))
    film.cinematography(t);bpy.context.view_layer.update()
    hero=film.hero.visible_actor;head=bone_position(hero,'Head')
    if head_start is None:head_start=head.copy()
    if t<=28:
        inverse=film.props['door'].matrix_world.inverted()
        for name in ('Head','Spine2','Hips','LeftArm','LeftForeArm','LeftHand','RightArm',
                     'RightForeArm','RightHand','LeftUpLeg','RightUpLeg','LeftLeg','RightLeg',
                     'LeftFoot','RightFoot'):
            local=inverse@bone_position(hero,name)
            assert not all(abs(v)<1.05 for v in local),('door intersects joint',t,name)
    if 24.5<=t<=28:
        projected=world_to_camera_view(film.w.scene,film.w.scene.camera,head)
        assert .04<projected.x<.96 and .04<projected.y<.96 and projected.z>0,(t,projected)
        assert visible_to_camera(film.w.scene,head,hero),('hero head occluded',t)
    if t==28:
        assert (head-head_start).length>1.,'hero does not emerge'
    if t>=41:
        gap=(hero.hand_position('Left')-film.fan.visible_actor.hand_position('Left')).length
        print('palms gap',t,round(gap,4),flush=True)
        assert gap<.12,(t,gap)
print('PROBE PASSED: sampled poses, cup, phone, doorway, framing; not a motion or listening review.',flush=True)
