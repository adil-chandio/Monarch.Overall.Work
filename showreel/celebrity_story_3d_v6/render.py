"""V6 -- a fictional celebrity morning, animated as real 3D scenes.

Characters: Microsoft Rocketbox (MIT).  Furniture and textures: Poly Haven
(CC0).  Every visible element is geometry in a Cycles scene; contacts are read
from the evaluated mocap pose, and the camera frames each subject from its live
head position so framing follows the blocking.
"""
from pathlib import Path
import argparse, json, math, sys, subprocess, tempfile
import bpy
from mathutils import Vector, Quaternion
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import motion
import scene_sets as S
import actors as A
from actors import Actor

ap = argparse.ArgumentParser()
ap.add_argument('--assets', default='/home/user/celebrity-lookdev-assets')
ap.add_argument('--output', default=str(P.parent.parent / 'deliverables/celebrity-story-third-person-3d-v6.mp4'))
ap.add_argument('--start', type=float, default=0.0)
ap.add_argument('--end', type=float, default=60.0)
ap.add_argument('--samples', type=int, default=6)
ap.add_argument('--width', type=int, default=720)
ap.add_argument('--fps', type=int, default=24)
ap.add_argument('--still', type=float, default=None)
ap.add_argument('--stills', type=lambda s: [float(x) for x in s.split(',')], default=None)
ap.add_argument('--stills-dir', default='/home/user/v6-stills')
ap.add_argument('--probe', action='store_true')
args = ap.parse_args()
S.ASSETS = Path(args.assets)
A.ASSETS = str(S.ASSETS)
missing = [n for n in ('ryan.glb', 'mia_smart.glb', 'james_formal.glb', 'daniel_formal.glb',
                       'sophia_formal.glb', 'noah_smart.glb', 'emma.glb', 'priya_casual.glb')
           if not (S.ASSETS / n).is_file()]
if missing:
    raise SystemExit(f'missing character assets in {S.ASSETS}: {missing}')
FPS = args.fps
W = args.width
H = round(W * 16 / 9)
H += H % 2

# ---------------------------------------------------------------- scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = 'CYCLES'
scn.cycles.samples = args.samples
scn.cycles.use_denoising = True
scn.cycles.max_bounces = 3
scn.cycles.diffuse_bounces = 2
scn.cycles.glossy_bounces = 2
scn.cycles.transmission_bounces = 2
scn.cycles.caustics_reflective = False
scn.cycles.caustics_refractive = False
scn.cycles.blur_glossy = 1.0
scn.cycles.sample_clamp_indirect = 6.0
scn.cycles.use_persistent_data = True
scn.cycles.device = 'CPU'
scn.render.threads_mode = 'FIXED'
scn.render.threads = 2
scn.render.resolution_x = W
scn.render.resolution_y = H
scn.render.resolution_percentage = 100
scn.render.image_settings.file_format = 'PNG'
scn.render.film_transparent = False
scn.view_settings.view_transform = 'AgX'
scn.view_settings.look = 'AgX - Medium High Contrast'
scn.view_settings.exposure = .42
scn.render.use_freestyle = False

world = bpy.data.worlds.new('world')
scn.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.42, .52, .68, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = .55

APT_X, KIT_X, ST_X = -80.0, -96.0, 20.0
apt = S.build_apartment(APT_X)
kit = S.build_kitchen(KIT_X)
street = S.build_street(ST_X)


def flatten_sets():
    """Collapse each set into one mesh per group.

    Cycles re-syncs every object before each frame; a street made of a thousand
    little boxes costs more in sync than in tracing, so static geometry is
    joined.  Props that move are tagged dynamic and left alone.
    """
    for grp in ('apt', 'kit', 'street'):
        parts = [o for o in bpy.data.objects
                 if o.type == 'MESH' and o.get('group') == grp and not o.get('dynamic')]
        if not parts:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        joined = bpy.context.view_layer.objects.active
        joined.name = f'{grp} static'
        joined['group'] = grp


flatten_sets()

# camera rig
target_empty = bpy.data.objects.new('aim', None)
scn.collection.objects.link(target_empty)
cam_data = bpy.data.cameras.new('shot cam')
cam = bpy.data.objects.new('shot cam', cam_data)
scn.collection.objects.link(cam)
scn.camera = cam
track = cam.constraints.new('TRACK_TO')
track.target = target_empty
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
cam_data.dof.use_dof = True
cam_data.sensor_width = 36
cam_data.clip_start = .05
cam_data.clip_end = 600

# ------------------------------------------------------------------- actors
hero = Actor('hero', 'ryan.glb', loc=(APT_X - 2.4, 2.0, 0), rot=math.pi, outfit='formal')
girl = Actor('girl', 'mia_smart.glb', loc=(0, 0, 0), rot=0, outfit='smart')
guard = Actor('guard', 'james_formal.glb', loc=(0, 0, 0), rot=0, outfit='formal')
fan_a = Actor('fana', 'daniel_formal.glb', loc=(0, 0, 0), rot=0, outfit='formal')
fan_b = Actor('fanb', 'sophia_formal.glb', loc=(0, 0, 0), rot=0, outfit='formal')
fan_c = Actor('fanc', 'noah_smart.glb', loc=(0, 0, 0), rot=0, outfit='smart')
fan_d = Actor('fand', 'emma.glb', loc=(0, 0, 0), rot=0, outfit='smart')
host = Actor('host', 'priya_casual.glb', loc=(0, 0, 0), rot=0, outfit='tee')
crowd = [fan_a, fan_b, fan_c, fan_d]
all_others = [host, girl, guard] + crowd
walker = motion.WalkDriver()

# ------------------------------------------------------------------- props
def prop(name, dim, mat, bevel=0.0):
    o = S.box(name, (0, 0, -50), dim, mat, bevel=bevel)
    o['dynamic'] = True
    o.visible_shadow = True
    return o


phone_mat = S.plain('phone body', (.02, .02, .025), rough=.28, metal=.6)
screen_mat = S.plain('phone screen', (.03, .05, .07), rough=.08)
flash_mat = S.plain('phone flash', (1, 1, .95), emit=30)
hero_phone = prop('hero phone', (.072, .009, .150), phone_mat, .004)
hero_screen = prop('hero screen', (.064, .0015, .134), screen_mat)
hero_screen.parent = hero_phone
hero_screen['dynamic'] = True
hero_phone2 = prop('sill phone', (.072, .009, .150), phone_mat, .004)
hero_screen2 = prop('sill screen', (.064, .0015, .134), screen_mat)
hero_screen2.parent = hero_phone2
hero_screen2['dynamic'] = True

ceramic = S.plain('mug ceramic', (.92, .91, .88), rough=.18)
coffee_mat = S.plain('coffee', (.16, .09, .05), rough=.12)
mug = S.cyl('mug', (0, 0, -50), .043, .09, ceramic, verts=28)
mug['dynamic'] = True
coffee = S.cyl('coffee surface', (0, 0, -50), .037, .004, coffee_mat, verts=28)
coffee['dynamic'] = True
handle = S.rod('mug handle', (-.05, 0, -50), (-.05, 0, -49.9), .008, ceramic, verts=10)
# a real torus-ish handle
bpy.ops.mesh.primitive_torus_add(location=(0, 0, -50), major_radius=.030, minor_radius=.007,
                                 major_segments=20, minor_segments=8)
handle = bpy.context.object
handle.name = 'mug handle'
handle.rotation_euler = (0, math.radians(90), 0)
handle.data.materials.append(ceramic)
handle['dynamic'] = True

letter_mat = S.plain('letter paper', (.92, .90, .84), rough=.9)
letter = prop('letter', (.105, .002, .148), letter_mat)
letter.rotation_mode = 'QUATERNION'

crowd_props = {}
for i, a in enumerate(crowd):
    body = prop(f'crowd phone {i}', (.075, .010, .152), phone_mat, .004)
    scr = prop(f'crowd screen {i}', (.066, .0015, .136), flash_mat)
    scr.parent = body
    scr['dynamic'] = True
    crowd_props[a] = (body, scr)

flash_lights = []
for i in range(5):
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    o = bpy.context.object
    o.name = f'flash light {i}'
    o.data.energy = 0.0
    o.data.color = (1, 1, 1)
    o.data.shadow_soft_size = .08
    o['dynamic'] = True
    flash_lights.append(o)

DYNAMIC = [hero_phone, hero_phone2, mug, coffee, handle, letter] + flash_lights \
          + [p for pair in crowd_props.values() for p in pair]


def hide_phones():
    for o in DYNAMIC:
        if o.name.startswith(('hero', 'sill', 'mug', 'coffee', 'letter')) or o.name in ('mug handle',):
            o.hide_render = True
    for pair in crowd_props.values():
        pair[0].hide_render = True
        pair[1].hide_render = True


def show(o, on=True):
    o.hide_render = not on


def hero_hold_phone(hero, body, screen, visible=True):
    hero.grip('Right', .92)
    bpy.context.view_layer.update()
    pos, q = hero.grasp('Right', .62)
    mq = q @ Quaternion((0, 0, 1), math.radians(-90))
    motion.attach(body, pos, mq)
    screen.location = (0, .0068, 0)
    screen.rotation_mode = 'QUATERNION'
    screen.rotation_quaternion = Quaternion((1, 0, 0), 0)
    show(body, visible)
    show(screen, visible)


# --------------------------------------------------------------- timeline
script = json.loads((P / 'script.json').read_text())
CUES = script
CUE = [c['start'] for c in CUES] + [60.0]
BEDROOM_END, KITCHEN_END, WINDOW_END, STREET_END, BARRIER_END, CAR_END = (
    CUE[2], CUE[3], CUE[4], CUE[6], CUE[8], CUE[9])


WINDOW_START = CUE[2]
STREET_START = CUE[3]
BARRIER_START = CUE[6]
CAR_START = CUE[8]


# Beat timing inside each act (cue table first, then actual walk distances)
ST_WALK_START = STREET_START + 3.6
ST_WAVE_START = ST_WALK_START + 6.2
BARRIER_WALK_START = BARRIER_START - .3
BARRIER_STOP = BARRIER_START + 3.1


def head(a):
    p = a.world_bone('Head')
    return p if p else Vector((0, 0, 1.6))


def update_flashes(t):
    """Camera flashes: short, uneven bursts that scatter across the crowd."""
    import random
    for i, o in enumerate(flash_lights):
        rnd = random.Random(int(t * 12) * 31 + i * 7)
        on = (t > 23.0 and t < 47.0) or (t > 34.0 and t < 43.0)
        energy = 0.0
        if on and rnd.random() < .45:
            energy = 60 + rnd.random() * 120
        o.data.energy = energy
        who = crowd[i % len(crowd)]
        p = who.world_bone('RightHand')
        if p:
            o.location = (p.x, p.y, p.z + .05)


def place_crowd(t, spots, look_at_pt):
    for a, (dx, y, rot) in zip(crowd, spots):
        a.ensure()
        a.place(ST_X + dx, y, 0, rot=rot)
        a.action('Cheer_Rig', 40 + (int(t * 7) + int(dx * 13)) % 120)
        a.expression(t, smile=.5, brow=.15, jaw=.10)
        a.look(look_at_pt, weight=.7)
        a.grip('Right', .85)
        bpy.context.view_layer.update()
        pos, q = a.grasp('Right')
        mq = q @ Quaternion((0, 0, 1), math.radians(-90))
        body, scr = crowd_props[a]
        motion.attach(body, pos, mq)
        scr.location = (0, .0068, 0)
        scr.rotation_mode = 'QUATERNION'
        scr.rotation_quaternion = Quaternion((1, 0, 0), 0)
        body.hide_render = scr.hide_render = False


# --------------------------------------------------------------------- acts
def act_bedroom(t):
    S.show_set('apt')
    hero.show(True); hero.outfit('formal')
    for a in all_others:
        a.show(False)
    hide_phones()
    mug.hide_render = coffee.hide_render = handle.hide_render = True
    letter.hide_render = True
    # 05:40, on his feet at the side of the bed, phone already at his ear
    hero.action('Phone_Rig', 96 + t * 20)
    bpy.context.view_layer.update()
    hero.place(APT_X - 3.55, 1.95, 0, rot=math.pi - .05)
    bpy.context.view_layer.update()
    if t < 8.4:
        hero_hold_phone(hero, hero_phone, hero_screen, visible=True)
        hero.expression(t, smile=.08, brow=.20 if 3.4 < t < 8.0 else .05, jaw=.02)
        hero.look((APT_X - 6.2, -1.4, 1.5))
    else:
        hide_phones()
        motion.attach(hero_phone2, (APT_X - 4.10, 4.30, .626), Quaternion((0, 0, 1), .5))
        hero_phone2.rotation_euler = (math.radians(90), 0, .5)
        hero_phone2.hide_render = hero_screen2.hide_render = False
        hero.expression(t, smile=.14, brow=.05)
        hero.look((APT_X - 1.4, -3.4, 1.2))


def act_kitchen(t):
    S.show_set('kit')
    hero.show(True); hero.outfit('shirt')
    for a in all_others:
        a.show(False)
    hide_phones()
    letter.hide_render = True
    hero.action('Drink_Rig', 330 + (t - 11.9) * 60)
    bpy.context.view_layer.update()
    hero.place(KIT_X - .42, 1.72, 0, rot=0.32)
    bpy.context.view_layer.update()
    hero.expression(t, smile=.10, brow=.10)
    hero.look((KIT_X - .6, 1.35, 1.05))
    # the mug sits in his right hand from the moment we cut in
    hero.grip('Right', .90)
    bpy.context.view_layer.update()
    pos, q = hero.grasp('Right', .58)
    mq = q @ Quaternion((1, 0, 0), math.radians(90))
    motion.attach(mug, pos, mq)
    motion.attach(coffee, (pos.x, pos.y, pos.z + .026), mq)
    motion.attach(handle, (pos.x, pos.y, pos.z), mq)
    mug.hide_render = coffee.hide_render = handle.hide_render = False


def act_window(t):
    S.show_set('apt')
    hero.show(True); hero.outfit('smart')
    for a in all_others:
        a.show(False)
    hide_phones()
    mug.hide_render = coffee.hide_render = handle.hide_render = True
    letter.hide_render = True
    hero.action('Think_Rig', 30 + (t - WINDOW_START) * 14)
    bpy.context.view_layer.update()
    hero.place(APT_X - .25, -3.55, 0, rot=math.pi + .12)
    bpy.context.view_layer.update()
    hero.expression(t, smile=.04, brow=.12)
    hero.look((APT_X + 4.0, -40.0, 3.0))


def act_street(t):
    S.show_set('street')
    for a in (hero, guard) + tuple(crowd):
        a.show(True)
    hero.outfit('formal'); guard.outfit('formal')
    host.show(False); girl.show(False)
    guard.place(ST_X + 6.4, 2.55, 0, rot=math.pi - .15)
    guard.action('Idle_Rig', 20 + t * 4)
    guard.expression(t, smile=0, brow=.02)
    guard.look((ST_X + 3.0, 1.0, 1.4))
    place_crowd(t, [(-6.4, 2.75, -.35), (-3.2, 3.15, -.12), (2.6, 2.95, .22),
                    (5.2, 3.20, -.05)], (ST_X + 3.2, 1.0, 1.5))
    if t < ST_WALK_START:
        hero.action('Idle_Rig', 16 + t * 5)
        hero.place(ST_X - 4.2, 1.05, 0, rot=math.pi - .25)
    elif t < ST_WAVE_START:
        f, off = walker.pose(t - ST_WALK_START, .95)
        hero.action('Walk_Rig', f)
        hero.place(ST_X + 17.4, -1.55 + off.y, 0, rot=math.pi)
    else:
        hero.action('Wave_Rig', 8 + (t - ST_WAVE_START) * 10)
        hero.place(ST_X + 3.2, 1.15, 0, rot=math.pi - .40)
    bpy.context.view_layer.update()
    hero.expression(t, smile=.44 if t > ST_WAVE_START else .18, brow=.2, jaw=.03)
    hero.look((ST_X - 1.2, 2.2, 1.55) if t < ST_WAVE_START + 1 else (ST_X - .8, 2.4, 1.5))
    hide_phones()
    mug.hide_render = coffee.hide_render = handle.hide_render = True
    letter.hide_render = True
    update_flashes(t)


def act_barrier(t):
    S.show_set('street')
    for a in (hero, guard, girl) + tuple(crowd):
        a.show(True)
    fan_a.show(False)
    hero.outfit('formal'); girl.outfit('smart'); guard.outfit('formal')
    guard.place(ST_X + 1.0, 2.75, 0, rot=math.pi - .10)
    guard.action('Idle_Rig', 20 + t * 4)
    guard.expression(t, smile=0, brow=.04)
    guard.look((ST_X + 2.4, 1.6, 1.3))
    girl.place(ST_X + 1.55, 2.48, 0, rot=0.10)
    if t < BARRIER_STOP:
        f, off = walker.pose(t - BARRIER_WALK_START, 1.0)
        hero.action('Walk_Rig', f)
        hero.place(ST_X + 2.55, -1.30 + off.y, 0, rot=math.pi)
        girl.action('Wave_Rig', 10 + (t - BARRIER_START) * 8)
    else:
        hero.action('Wave_Rig', 8 + (t - BARRIER_STOP) * 6)
        hero.place(ST_X + 2.55, 1.72, 0, rot=math.pi - .22)
        girl.action('Wave_Rig', 16 + (t - BARRIER_STOP) * 6)
    bpy.context.view_layer.update()
    hero.expression(t, smile=.28 if t < BARRIER_STOP + 2.1 else .46, brow=.24)
    hero.look((ST_X + 1.55, 2.48, 1.46))
    bpy.context.view_layer.update()
    girl.grip('Right', .55)
    bpy.context.view_layer.update()
    gpos, gq = girl.grasp('Right')
    letter.hide_render = False
    motion.attach(letter, gpos, gq @ Quaternion((1, 0, 0), math.radians(70)))
    girl.expression(t, smile=.20, brow=.46, jaw=.02)
    girl.look((ST_X + 2.55, 1.72, 1.55))
    girl.tremble(.5 if t < BARRIER_STOP + 3.1 else .2, t, 1.7)
    place_crowd(t, [(-3.9, 3.05, -.35), (-2.2, 3.75, -.1), (3.9, 3.05, .3),
                    (5.6, 2.85, -.2)], (ST_X + 2.55, 1.7, 1.5))
    mug.hide_render = coffee.hide_render = handle.hide_render = True
    update_flashes(t)


def act_car(t):
    S.show_set('street')
    for a in (hero, guard):
        a.show(True)
    for a in crowd:
        a.show(False)
    host.show(False); girl.show(False)
    hero.outfit('formal'); guard.outfit('formal')
    f, off = walker.pose(max(0, t - CAR_START), .9)
    hero.action('Walk_Rig', f)
    hero.place(ST_X + 13.4, -1.55 + off.y, 0, rot=math.pi)
    bpy.context.view_layer.update()
    hero.expression(t, smile=.2, brow=.06)
    guard.place(ST_X + 12.0, 1.2, 0, rot=math.pi - .5)
    guard.action('Idle_Rig', 10 + t * 3)
    guard.expression(t, smile=0, brow=.02)
    hide_phones()
    mug.hide_render = coffee.hide_render = handle.hide_render = True
    letter.hide_render = True
    for o in flash_lights:
        o.data.energy = 0.0


def act_final(t):
    S.show_set('apt')
    hero.show(True); hero.outfit('shirt')
    hide_phones()
    hero.action('Idle_Rig', 40 + (t - CAR_END) * 8)
    bpy.context.view_layer.update()
    hero.place(APT_X + 2.55, 3.25, 0, rot=math.pi - .06)
    bpy.context.view_layer.update()
    hero.expression(t, smile=.02, brow=.06)
    hero.look((APT_X + 2.4, -30.0, 2.6))
    # phone face-down on the coffee table, out of reach
    motion.attach(hero_phone2, (APT_X + 2.10, 2.70, .404), Quaternion((0, 0, 1), .9))
    hero_phone2.rotation_euler = (0, 0, .9)
    hero_phone2.hide_render = hero_screen2.hide_render = False
    mug.hide_render = coffee.hide_render = handle.hide_render = True
    letter.hide_render = True



# -------------------------------------------------------------------- shots
# (start, end, subject, azimuth from facing, distance, cam height, aim dz, lens)
# Shots are generated from the narration cues, so camera and blocking can never
# drift apart: every beat below is expressed inside one act's window.
ACTS = [
    ('bedroom', 0.0, BEDROOM_END),
    ('kitchen', BEDROOM_END, KITCHEN_END),
    ('window', KITCHEN_END, WINDOW_END),
    ('street', WINDOW_END, STREET_END),
    ('barrier', STREET_END, BARRIER_END),
    ('car', BARRIER_END, CAR_END),
    ('final', CAR_END, 60.0),
]

# per act: list of (fraction_start, fraction_end, subject, az, dist, height, dz, lens)
BEATS = {
    'bedroom': [(0.0, .22, 'hero', 0, 3.0, 1.60, -.05, 32),
                (.22, .40, 'phone', 34, .58, 1.62, .05, 85),
                (.40, .52, 'hero', -32, 2.2, 1.54, -.02, 52),
                (.52, .66, 'hero', 54, 2.0, 1.38, -.02, 46),
                (.66, .83, 'hero', 16, 3.2, 1.66, -.08, 36),
                (.83, 1.0, 'hero', -74, 2.4, 1.46, .02, 40)],
    'kitchen': [(0.0, .34, 'mug', 54, .78, 1.28, .04, 50),
                (.34, .58, 'hero', -26, 2.6, 1.54, -.02, 48),
                (.58, .78, 'hero', 34, 1.55, 1.57, .05, 68),
                (.78, 1.0, 'hero', 68, 2.5, 1.50, -.05, 40)],
    'window': [(0.0, .26, 'hero', -150, 3.0, 1.62, -.02, 40),
               (.26, .46, 'hero', 156, 2.4, 1.63, .02, 62),
               (.46, .66, 'hero', -96, 2.7, 1.32, -.10, 38),
               (.66, .84, 'hero', -34, 2.5, 1.55, .04, 46),
               (.84, 1.0, 'hero', 148, 4.6, 1.80, -.04, 30)],
    'street': [(0.0, .18, 'hero', 150, 6.4, 1.86, -.02, 30),
               (.18, .38, 'hero', 66, 6.8, 1.78, -.10, 30),
               (.38, .52, 'hero', 58, 4.2, 1.58, .02, 44),
               (.52, .68, 'hero', 26, 3.0, 1.55, .04, 46),
               (.68, .84, 'hero', 104, 3.6, 1.66, 0.0, 36),
               (.84, 1.0, 'hero', 38, 1.7, 1.56, .03, 62)],
    'barrier': [(0.0, .14, 'hero', 68, 3.0, 1.56, 0.0, 44),
                (.14, .28, 'girl', -70, 2.6, 1.50, .02, 44),
                (.28, .46, 'gift', 32, 1.30, 1.44, -.01, 52),
                (.46, .64, 'pair', 26, 1.95, 1.42, -.06, 44),
                (.64, .82, 'hero', 10, 1.25, 1.54, .03, 70),
                (.82, 1.0, 'hero', 74, 3.2, 1.68, -.06, 44)],
    'car': [(0.0, .45, 'hero', 150, 4.6, 1.44, -.02, 34),
            (.45, 1.0, 'hero', 116, 4.0, 1.48, -.02, 36)],
    'final': [(0.0, .30, 'hero', 22, 1.30, 1.54, .02, 68),
              (.30, .58, 'hero', 66, 4.0, 1.48, -.06, 34),
              (.58, .80, 'hero', 38, 1.45, 1.54, .03, 66),
              (.80, 1.0, 'hero', -64, 3.4, 1.46, -.02, 38)],
}

SHOTS = []
for name, a, b in ACTS:
    span = b - a
    for f0, f1, subj, az, dist, ch, dz, lens in BEATS[name]:
        SHOTS.append((a + span * f0, a + span * f1, subj, az, dist, ch, dz, lens))
PUSH = [(0.0, .0)] * len(SHOTS)

def shot_at(t):
    for i, s in enumerate(SHOTS):
        if t < s[1] or i == len(SHOTS) - 1:
            return i, s
    return len(SHOTS) - 1, SHOTS[-1]


def focal_point(subj):
    if subj == 'hero':
        p = head(hero)
        return Vector((p.x, p.y, p.z - .05))
    if subj == 'girl':
        p = head(girl)
        return Vector((p.x, p.y, p.z - .05))
    if subj == 'pair':
        a, b = head(hero), head(girl)
        m = (a + b) * .5
        return Vector((m.x, m.y, m.z - .12))
    if subj == 'gift':
        return head(girl) * .55 + hero.world_bone('RightHand') * .45
    if subj in ('phone', 'mug'):
        p = hero.world_bone('RightHand')
        return Vector((p.x, p.y, p.z))
    if subj == 'car':
        return Vector((ST_X + 17.0, -2.4, 1.10))
    return head(hero)


def in_bounds(o):
    if o.x > -70.0:
        return -5.6 < o.y < 3.15 and o.z > .8
    if o.x > -88.0:
        return (-84.4 < o.x < -75.7) and (-4.35 < o.y < 5.4) and (0.55 < o.z < 2.85)
    return (-100.9 < o.x < -91.2) and (-3.6 < o.y < 4.6) and (0.55 < o.z < 2.85)


def _clear(origin, focus, skip):
    d = focus - origin
    L = d.length
    d.normalize()
    # side rays: a camera buried in furniture fails one of these even when the
    # straight line to the subject happens to end on the subject itself
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    for side in (Vector((d.y, -d.x, 0)).normalized(), Vector((-d.y, d.x, 0)).normalized()):
        hit, loc, nrm, idx, obj, mat = scn.ray_cast(dg, origin, side, distance=.45)
        if hit and obj.get('group') in S.GROUPS:
            return False
    hit, loc, nrm, idx, obj, mat = scn.ray_cast(dg, origin + d * .06, d, distance=max(.1, L - .55))
    if not hit:
        return True
    name = obj.name
    if any(name.startswith(c) for c in skip):
        return True
    if name.startswith(('sky', 'far', 'tower', 'city', 'sidewalk', 'curb', 'lamp', 'traffic',
                        'awning', 'bollard', 'canopy', 'railing', 'planter', 'bush', 'tree',
                        'kerb', 'road', 'street', 'rope', 'drape', 'window', 'glass')):
        return True
    return False


def _tokens(subj):
    if subj == 'hero':
        return ('hero',)
    if subj == 'girl':
        return ('girl',)
    if subj in ('pair', 'gift'):
        return ('hero', 'girl')
    return ()


OVERRIDES = {}

# light anchor shared by all street shots
ST_LIGHT = (ST_X + 2.0, -7.0, 7.5)


def _clearance(origin):
    """How far the nearest surface is all around the camera.

    A camera buried in a counter or a wall still renders *something*, so the
    solver refuses any spot without breathing room in eight directions.
    """
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    best = 9.9
    for k in range(8):
        a = k * math.pi / 4
        d = Vector((math.cos(a), math.sin(a), 0))
        hit, loc, nrm, idx, obj, mat = scn.ray_cast(dg, origin, d, distance=1.2)
        if hit and obj.get('group') in S.GROUPS:
            best = min(best, (loc - origin).length)
    return best


def _projects(pos, lens, focus, dz=0.0):
    """Is the subject actually inside the frame, with margin?"""
    from bpy_extras.object_utils import world_to_camera_view
    old_loc = cam.location.copy()
    old_lens = cam.data.lens
    cam.location = pos
    cam.data.lens = lens
    scn.camera.data.shift_x = 0
    scn.camera.data.shift_y = 0
    bpy.context.view_layer.update()
    v = world_to_camera_view(scn, cam, focus)
    cam.location = old_loc
    cam.data.lens = old_lens
    return (0.30 < v.x < 0.70) and (0.22 < v.y < 0.74) and v.z > 0


OVERRIDES = {
    # deliberate wides: the solver keeps people centred, but an establishing
    # frame has to show the room, so these are placed by hand and checked.
    0: ((APT_X + 3.35, -2.05, 1.62), (APT_X - 2.30, 3.20, 1.22), 26),
}


def place_camera(t, idx, s):
    t0, t1, subj, az, dist, ch, dz, lens = s
    u = motion.ease((t - t0) / max(1e-3, t1 - t0))
    if idx in OVERRIDES:
        pos, tgt, ln = OVERRIDES[idx]
        cam.location = pos
        target_empty.location = tgt
        cam.data.lens = ln * (1 + .05 * u)
        cam.data.dof.focus_distance = (Vector(tgt) - cam.location).length
        cam.data.dof.aperture_fstop = 5.0
        return
    focal = focal_point(subj)
    rig = girl.rig if subj == 'girl' else hero.rig
    # the imported rig faces +Y; shot azimuth 0 means *facing him* (camera in
    # front, looking at his face), positive swings toward his left shoulder
    fwd = rig.rotation_quaternion @ Vector((0, -1, 0))
    right = rig.rotation_quaternion @ Vector((1, 0, 0))
    if subj == 'pair':
        # side-on to the two of them, always from the road
        axis = head(hero) - head(girl)
        axis.z = 0
        axis = axis.normalized() if axis.length > .05 else Vector((1, 0, 0))
        side = 1 if az >= 0 else -1
        dirv0 = (Vector((-axis.y, axis.x, 0)) * side * .9 + Vector((0, -1, 0)) * .3).normalized()
    else:
        a = math.radians(az)
        dirv0 = (fwd * math.cos(a) + right * math.sin(a)).normalized()
    d0 = dist * (1 - .05 * u)
    skip = _tokens(subj)
    aim = Vector((focal.x, focal.y, focal.z + dz))

    best = None
    for dscale in (1.0, .82, 1.22, .66, 1.5, .55):
        d = d0 * dscale
        base = math.atan2(dirv0.y, dirv0.x)
        for k in (0, 10, -10, 20, -20, 32, -32, 46, -46, 62, -62, 80, -80, 100, -100):
            ang = base + math.radians(k)
            o = Vector((focal.x + math.cos(ang) * d, focal.y + math.sin(ang) * d, ch))
            if not in_bounds(o):
                continue
            if min(_clearance(o), _clearance(Vector((o.x, o.y, ch + .30)))) < .34:
                continue
            if not _clear(o, focal, skip):
                continue
            if not _projects(o, lens, aim):
                continue
            best = o
            break
        if best:
            break
    if best is None:                      # fall back to the authored angle
        best = Vector((focal.x + dirv0.x * d0, focal.y + dirv0.y * d0, ch))
    cam.location = best
    target_empty.location = aim
    cam.data.lens = lens * (1 + .03 * u)
    cam.data.dof.focus_distance = (aim - best).length
    cam.data.dof.aperture_fstop = 4.0 if lens > 60 else (5.0 if lens > 45 else 6.3)


def update(t):
    if t < BEDROOM_END:
        act_bedroom(t)
    elif t < KITCHEN_END:
        act_kitchen(t)
    elif t < WINDOW_END:
        act_window(t)
    elif t < STREET_END:
        act_street(t)
    elif t < BARRIER_END:
        act_barrier(t)
    elif t < CAR_END:
        act_car(t)
    else:
        act_final(t)
    idx, s = shot_at(t)
    place_camera(t, idx, s)
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ captions
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def word_schedule(text, start, duration):
    words = text.split()
    weights = [max(2, len(w.strip('.,')) + 1) for w in words]
    total = sum(weights)
    out, acc = [], 0.0
    for w, wt in zip(words, weights):
        a = start + duration * acc / total
        acc += wt
        out.append((w, a, start + duration * acc / total))
    return out


CUES_WORDS = [word_schedule(c['text'], c['start'] + .05, c['duration'] - .12) for c in CUES]


def caption_for(t):
    for ci, words in enumerate(CUES_WORDS):
        for wi, (w, a, b) in enumerate(words):
            if a <= t < b + .02:
                lo = max(0, wi - 3)
                line = ' '.join(x[0] for x in words[lo:wi + 1])
                return line[-46:], motion.ease((t - a) / .08)
    return '', 0


def overlay(png, t):
    im = Image.open(png).convert('RGB')
    line, alpha = caption_for(t)
    d = ImageDraw.Draw(im, 'RGBA')
    if line:
        font = ImageFont.truetype(FONT, max(18, int(W * .046)))
        d.text((W // 2, int(H * .795)), line, font=font, fill=(255, 255, 255, int(245 * alpha)),
               anchor='mm', stroke_width=max(2, int(W * .006)),
               stroke_fill=(0, 0, 0, int(210 * alpha)))
    small = ImageFont.truetype(FONT, max(12, int(W * .019)))
    d.text((W - int(W * .04), int(H * .035)), 'FICTIONAL', font=small,
           fill=(255, 255, 255, 150), anchor='ra', stroke_width=1, stroke_fill=(0, 0, 0, 120))
    if t < .45:
        im = Image.blend(Image.new('RGB', im.size), im, motion.ease(t / .45))
    if t > 59.55:
        im = Image.blend(im, Image.new('RGB', im.size), motion.ease((t - 59.55) / .45))
    return im


def render(t, path):
    update(t)
    scn.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if args.probe:
    for t in (0, 4, 8, 12, 15, 18, 21, 24, 27, 31, 34, 37, 40, 43, 46, 49, 52, 56, 59):
        update(t)
        print('PROBE', t, tuple(round(v, 2) for v in cam.location),
              tuple(round(v, 2) for v in focal_point('hero')), flush=True)
    raise SystemExit(0)

if args.stills:
    outdir = Path(args.stills_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        frame = Path(td) / 'f.png'
        for t in args.stills:
            render(t, frame)
            overlay(frame, t).save(outdir / f'still-{t:05.1f}.jpg', quality=93)
            print('STILL', t, flush=True)
    print('STILLS', outdir, flush=True)
else:
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    first, last = int(round(args.start * FPS)), int(round(args.end * FPS))
    with tempfile.TemporaryDirectory() as td:
        frame = Path(td) / 'f.png'
        proc = subprocess.Popen([ff, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an',
                                 '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17',
                                 '-pix_fmt', 'yuv420p', '-x264-params', 'keyint=48', str(out)],
                                stdin=subprocess.PIPE)
        for n in range(first, last):
            t = n / FPS
            render(t, frame)
            proc.stdin.write(overlay(frame, t).tobytes())
            if n % 24 == 0:
                print('RENDER_PROGRESS', n, '/', last, flush=True)
        proc.stdin.close()
        if proc.wait():
            raise RuntimeError('encode failed')
    if not out.is_file() or out.stat().st_size < 10000:
        raise RuntimeError(f'encoder produced no usable file: {out}')
    print('OUTPUT', out, out.stat().st_size, flush=True)
