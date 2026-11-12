"""Numerical scene checks; they supplement, not replace, visual motion review."""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from showreel.celebrity_cinematic_3d.render import Film


def position(rig, name):
    return rig.matrix_world @ rig.pose.bones['mixamorig:' + name].head


def visible_to_camera(scene, target, actor):
    cam = scene.camera
    origin = cam.matrix_world.translation.copy()
    direction = target - origin
    distance = direction.length
    direction.normalize()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for _ in range(80):
        hit, point, _, _, obj, _ = scene.ray_cast(depsgraph, origin, direction, distance=distance)
        if not hit:
            return True  # a joint may lie just outside a low-poly face
        if obj in actor.meshes:
            return True
        if not obj.hide_render:
            return False
        advance = (point-origin).length + .001
        distance -= advance
        if distance <= 0:
            return True
        origin = point + direction*.001
    return False


film = Film(320, 2)
film.reset('bedroom')
for t in (0.5, 3., 5., 8., 11.):
    film.w.t = t
    film.update_bedroom(t)
    bpy.context.view_layer.update()
    rig = film.hero.visible_actor.rig
    for side in ('Left', 'Right'):
        hip, knee, ankle = [position(rig, side+n) for n in ('UpLeg', 'Leg', 'Foot')]
        assert knee.y < hip.y - .30 and abs(knee.z-hip.z) < .08, (t, side, hip, knee)
        assert ankle.z < knee.z - .30 and ankle.z > .05, (t, side, knee, ankle)
    if t >= 5:
        gap = (film.hero.visible_actor.hand_position('Left') - film.props['phone'].location).length
        print('phone', t, 'grip-to-phone', round(gap, 4), flush=True)
        assert gap < .17, (t, gap)

film.reset('street')
for actor in (film.hero, film.fan, film.press, *film.extra):
    visible = [o.name.split('.')[0] for o in actor.visible_actor.meshes if not o.hide_render]
    assert any(part.startswith(('Outfit_', 'Top_')) for part in visible), (actor.visible_actor.role, visible)
heads = []
for t in (23.5, 24., 24.5, 25., 26., 27., 28., 41., 42., 43.):
    film.w.t = t
    film.update_street(t)
    # render_time also poses the background press member after update_street.
    extra_base = Vector((1.54, -1.20, 0))
    arm = extra_base + Vector((-.26, .06, 1.0 + .10 * math.sin(t*3.3)))
    film.extra[0].pose(extra_base, yaw=math.pi-.1, targets={1: arm}, headyaw=.1*math.sin(t))
    film.cinematography(t)
    bpy.context.view_layer.update()
    actor = film.hero.visible_actor
    head = position(actor.rig, 'Head')
    assert all(math.isfinite(v) for v in head)
    heads.append(head)
    if 24.5 <= t <= 28.:
        p = world_to_camera_view(film.w.scene, film.w.scene.camera, head)
        assert .04 < p.x < .96 and .04 < p.y < .96 and p.z > 0, (t, p)
        assert visible_to_camera(film.w.scene, head, actor), ('hero head occluded', t)
    if t >= 41.:
        gap = (actor.hand_position('Left') - film.fan.visible_actor.hand_position('Left')).length
        print('handshake', t, 'grip-centre gap', round(gap, 4), flush=True)
        assert gap < .12, (t, gap)
assert (heads[0] - heads[6]).length > 1.0, 'hero did not walk out'

film.reset('kitchen')
for t in (13.5, 14., 14.5, 15.5, 16.):
    film.w.t = t
    film.update_kitchen(t)
    bpy.context.view_layer.update()
    gap = (film.hero.visible_actor.hand_position('Left') - film.props['cup'].location).length
    print('coffee', t, 'grip-to-cup', round(gap, 4), flush=True)
    assert gap < .13, (t, gap)
print('Numerical scene probe passed; visual and audio review still required.', flush=True)
