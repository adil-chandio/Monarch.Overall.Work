"""A small numerical pose probe; not a substitute for watching the film."""
from pathlib import Path
import math
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import bpy
from showreel.celebrity_premium_3d.render import Film

film = Film(320, 2)
film.reset('street')
for actor in (film.hero, film.fan, film.press, *film.extra):
    visible = [o.name.split('.')[0] for o in actor.visible_actor.meshes if not o.hide_render]
    assert any(part.startswith(('Outfit_', 'Top_')) for part in visible), (actor.visible_actor.role, visible)
positions = []
for t in (24., 25., 26., 27., 28., 41., 42., 43.):
    film.w.t = t
    film.update_street(t)
    bpy.context.view_layer.update()
    actor = film.hero.visible_actor
    head = actor.rig.matrix_world @ actor.rig.pose.bones['mixamorig:Head'].head
    assert all(math.isfinite(x) for x in head)
    positions.append(head.copy())
    if t >= 41:
        gap = (actor.hand_position('Left') - film.fan.visible_actor.hand_position('Left')).length
        print('contact', t, 'grip-centre gap', round(gap, 4), flush=True)
        assert gap < .12, (t, gap)
assert (positions[0] - positions[4]).length > 1.0, 'hero did not walk into the street'
film.reset('kitchen')
for t in (13.5, 14., 14.5, 15.5, 16.):
    film.w.t = t
    film.update_kitchen(t)
    bpy.context.view_layer.update()
    gap = (film.hero.visible_actor.hand_position('Left') - film.props['cup'].location).length
    print('coffee', t, 'grip-to-cup distance', round(gap, 4), flush=True)
    assert gap < .13, (t, gap)
print('Pose probe passed; still requires visual review.', flush=True)
