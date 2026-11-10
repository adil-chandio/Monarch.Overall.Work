"""Set construction: an apartment, a kitchen, and a morning street.

All geometry is built at real scale in metres.  Furniture comes from CC0 scans
(Poly Haven via INTERIO) and is placed at true dimensions; the street set is
authored here so the camera has something to look through at every angle.

Axes: +X runs along the street, +Y points from the road toward the buildings,
+X toward camera-right.  Floors sit at z = 0.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion, Euler

ASSETS = Path('/home/user/celebrity-lookdev-assets')
GROUPS = ('apt', 'kit', 'street')

# ------------------------------------------------------------------ materials
_MATS = {}


def plain(name, col, rough=.65, metal=0.0, emit=0.0, alpha=None):
    key = (name, col, rough, metal, emit, alpha)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (*col, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if emit:
        bs.inputs['Emission Color'].default_value = (*col, 1)
        bs.inputs['Emission Strength'].default_value = emit
    if alpha is not None:
        bs.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'
        m.use_backface_culling = False
    m.diffuse_color = (*col, 1)
    _MATS[key] = m
    return m


_TEXTURE_CACHE = {}


def textured(name, col, tile=(1, 1, 1), rough=.6, variants=None, bump=.25, scale=6.0):
    """Image texture if a CC0 map exists for this slot, otherwise a tinted finish."""
    key = ('tex', name, tile, col, rough)
    if key in _MATS:
        return _MATS[key]
    base = plain(name, col, rough=rough)
    if variants:
        for v in variants:
            p = ASSETS / v
            if p.is_file():
                nt = base.node_tree
                bs = nt.nodes['Principled BSDF']
                tex = nt.nodes.new('ShaderNodeTexImage')
                tex.image = bpy.data.images.load(str(p), check_existing=True)
                tex.projection = 'BOX'
                tex.projection_blend = .4
                mp = nt.nodes.new('ShaderNodeMapping')
                mp.inputs['Scale'].default_value = tile
                tc = nt.nodes.new('ShaderNodeTexCoord')
                nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
                nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
                nt.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
                _TEXTURE_CACHE[name] = tex
                return base
    noise_bump(base, scale=scale, strength=bump)
    _MATS[key] = base
    return base


def noise_bump(mat, scale=9.0, strength=.18):
    nt = mat.node_tree
    bs = nt.nodes['Principled BSDF']
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = .55
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = .012
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return mat


def hide_from_lens(o):
    o.visible_camera = False
    o.visible_shadow = True
    return o


# ------------------------------------------------------------------- geometry
def box(name, loc, dim, mat, bevel=0.0, rot=None, group=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dim
    if rot:
        o.rotation_euler = Euler(rot)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('soft', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('normals', 'WEIGHTED_NORMAL')
    if group:
        o['group'] = group
    return o


def cyl(name, loc, r, depth, mat, verts=24, rot=None, group=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot)
    o.data.materials.append(mat)
    if group:
        o['group'] = group
    return o


def sphere(name, loc, radius, mat, group=None, scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    if scale:
        o.scale = scale
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if group:
        o['group'] = group
    return o


def rod(name, a, b, r, mat, group=None, verts=12):
    a, b = Vector(a), Vector(b)
    v = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=v.length,
                                        location=(a + b) / 2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    if group:
        o['group'] = group
    return o


def model(name, at, z=0.0, rot=0.0, scale=None, group=None):
    """Import a furniture GLB, sit it on the floor, optionally resize it."""
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSETS / name))
    added = [o for o in bpy.context.scene.objects if o not in before]
    roots = [o for o in added if o.parent is None]
    for o in roots:
        o.location += Vector((at[0], at[1], z))
        o.rotation_euler.z += rot
        if scale:
            o.scale = (scale, scale, scale)
    for o in added:
        if o.type == 'MESH':
            o.visible_shadow = True
        if group:
            o['group'] = group
    return added


def area(name, loc, target, power, size, col, shape='RECTANGLE', group=None, spread=None):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.shape = shape
    o.data.size = size
    if spread:
        o.data.size_y = spread
    o.data.color = col
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    hide_from_lens(o)
    if group:
        o['group'] = group
    return o


def point(name, loc, power, col, radius=.35, group=None):
    bpy.ops.object.light_add(type='POINT', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.color = col
    o.data.shadow_soft_size = radius
    hide_from_lens(o)
    if group:
        o['group'] = group
    return o


def spot(name, loc, target, power, col, size=.3, angle=55, blend=.4, group=None):
    bpy.ops.object.light_add(type='SPOT', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.color = col
    o.data.shadow_soft_size = size
    o.data.spot_size = math.radians(angle)
    o.data.spot_blend = blend
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    hide_from_lens(o)
    if group:
        o['group'] = group
    return o


def sky_dome(group='street'):
    """A big sky sphere with a real gradient; the top half is all we need."""
    mat = bpy.data.materials.new('sky')
    mat.use_nodes = True
    nt = mat.node_tree
    bs = nt.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (.55, .70, .92, 1)
    bs.inputs['Roughness'].default_value = 1.0
    bs.inputs['Emission Strength'].default_value = 1.15
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements.remove(cr.color_ramp.elements[1])
    st = cr.color_ramp.elements[0]
    st.position = 0.0
    st.color = (1.45, 1.18, .95, 1)
    for pos, col in ((.10, (1.15, 1.02, .94)), (.28, (.72, .84, .99)),
                     (.55, (.34, .56, .92)), (1.0, (.12, .26, .62))):
        e = cr.color_ramp.elements.new(pos)
        e.color = (*col, 1)
    nt.links.new(cr.outputs['Color'], bs.inputs['Emission Color'])
    nt.links.new(cr.outputs['Color'], bs.inputs['Base Color'])
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], cr.inputs['Fac'])
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=400,
                                         location=(0, 0, -60))
    o = bpy.context.object
    o.name = 'sky dome'
    o.scale = (1, 1, .62)
    o.data.materials.append(mat)
    o['group'] = 'sky'
    o.visible_shadow = False
    hide_from_lens(o)
    return o


def city_outside(x_center, y, z_floor=-24.0, width=180, group='apt'):
    """Distant towers so glazing has depth instead of an empty gradient."""
    dark = plain('tower', (.055, .062, .078), rough=.85)
    lit = plain('tower window', (.55, .62, .72), rough=.2, emit=.9)
    unlit = plain('tower window dark', (.10, .12, .16), rough=.35)
    for i in range(26):
        bx = x_center - width / 2 + (i * 7.3) % width
        depth = y + 26 + (i * 13) % 30
        h = 14 + (i * 9) % 46
        box(f'tower {i}', (bx, depth, z_floor + h / 2), (5.4 + (i % 3), 5.8, h), dark)
        for c in range(3):
            for r in range(int(h / 3.2)):
                on = (i + c + r) % 4 != 0
                box(f'tower win {i}-{c}-{r}',
                    (bx - 1.7 + c * 1.7, depth - 2.92, z_floor + 2.0 + r * 3.2),
                    (.7, .06, 1.0), lit if on else unlit)
    # one closer block on the left so the horizon is not a flat wall
    box('near tower', (x_center - width / 2 + 12, y + 14, z_floor + 30),
        (9, 8, 60), dark)


# ------------------------------------------------------------------ apartment
def build_apartment(x=-80.0):
    """Penthouse bedroom + living bay. Returns the measurements the acts need."""
    g = 'apt'
    floor_mat = textured('apt floor', (.30, .25, .22), (2, 2, 1),
                         variants=('wood_floor.jpg', 'floor.jpg', 'wood.jpg'))
    wall_mat = textured('apt wall', (.66, .62, .57), (1, 1, 1),
                        variants=('plaster.jpg', 'wall.jpg'))
    ceil = plain('apt ceiling', (.52, .50, .48), rough=.9)
    dark = plain('apt dark', (.06, .055, .05), rough=.5, metal=.3)
    brass = plain('apt brass', (.62, .48, .26), rough=.35, metal=1.0)
    linen = plain('apt linen', (.80, .78, .74), rough=.95)
    linen2 = plain('apt linen2', (.52, .48, .46), rough=.95)
    wood = textured('apt wood', (.30, .19, .12), (1, 1, 1))

    # shell: 9 m wide, 10 m deep
    box('apt floor', (x, 0, -.10), (9.6, 10.4, .20), floor_mat, group=g)
    box('apt wall back', (x, 5.15, 1.6), (9.6, .22, 3.2), wall_mat, group=g)
    box('apt wall left', (x - 4.7, 0, 1.6), (.22, 10.4, 3.2), wall_mat, group=g)
    box('apt wall right', (x + 4.7, 0, 1.6), (.22, 10.4, 3.2), wall_mat, group=g)
    box('apt ceiling', (x, 0, 3.22), (9.6, 10.4, .10), ceil, group=g)
    box('apt skirting', (x, 5.02, .07), (9.6, .03, .14), dark, group=g)

    # glazing wall at -Y, six metres wide, with piers and a low sill
    box('apt sill slab', (x, -5.05, .19), (9.6, .40, .38), plain('apt sill', (.72, .70, .66), rough=.35), group=g)
    glass = plain('apt glass', (.62, .72, .82), rough=.05, alpha=.10)
    for i in range(4):
        cxp = x - 3.0 + i * 2.0
        p = box(f'window pane {i}', (cxp, -5.02, 1.86), (1.96, .02, 3.24), glass, group=g)
        hide_from_lens(p)
        p.visible_shadow = False
        box(f'window mullion {i}', (cxp - .98, -5.02, 1.86), (.07, .09, 3.24), dark, group=g)
    box('window head', (x, -5.02, 3.46), (9.6, .12, .12), dark, group=g)
    box('window transom', (x, -5.02, 2.46), (9.4, .08, .06), dark, group=g)
    for px in (x - 4.45, x + 4.45):
        box('window pier', (px, -5.02, 1.8), (.55, .34, 3.6), wall_mat, group=g)
    # drapes, gathered at both ends
    drape = plain('apt drape', (.72, .68, .62), rough=1.0)
    for sx in (-1, 1):
        for k, dx in enumerate((2.55, 2.86)):
            o = box(f'apt drape {sx}{k}', (x + sx * dx, -4.72, 1.75), (.30, .10, 3.5),
                    drape, group=g)
            mod = o.modifiers.new('folds', 'WAVE')
            mod.height = .035
            mod.width = .22
            mod.narrowness = 1.4
            mod.use_normal = True
            mod.use_x = False
            mod.use_y = True
        box(f'curtain rail {sx}', (x + sx * 2.7, -4.72, 3.52), (2.0, .06, .06), brass, group=g)

    # bed against the right-hand wall side, headboard to +Y wall
    bed_at = (x - 3.40, 3.55)
    model('bed.glb', bed_at, rot=0.0, scale=2.05, group=g)
    box('bed head', (x - 3.40, 4.72, .62), (2.10, .14, 1.24), plain('apt head', (.34, .29, .26), rough=.85), group=g)
    for i, dx in enumerate((-.62, 0, .62)):
        box(f'pillow {i}', (x - 3.40 + dx, 4.28, .70), (.54, .34, .16), linen, bevel=.06, group=g)
        box(f'pillow top {i}', (x - 3.40 + dx, 4.26, .79), (.50, .30, .10), linen, bevel=.05, group=g)
    box('duvet', (x - 3.40, 2.62, .62), (2.04, 2.55, .22), linen2, bevel=.07, group=g)
    box('throw', (x - 3.40, 1.48, .70), (2.06, .70, .10), plain('apt throw', (.30, .27, .30), rough=1.0),
        bevel=.04, group=g)

    # nightstands + lamps
    for sx in (-1, 1):
        nx = x - 3.40 + sx * 1.42
        model('nightstand.glb', (nx, 4.32), rot=0.0, scale=1.0, group=g)
        cyl(f'bedside base {sx}', (nx, 4.32, .80), .07, .10, brass, group=g)
        rod(f'bedside stem {sx}', (nx, 4.32, .85), (nx, 4.32, 1.02), .014, brass, group=g)
        sh = cyl(f'bedside shade {sx}', (nx, 4.32, 1.06), .13, .17,
                 plain('apt shade', (.95, .82, .62), rough=.9, emit=.55), group=g)

    # living end toward the glass
    sofa_at = (x + 2.60, 4.25)
    model('sofa.glb', sofa_at, rot=math.pi, scale=1.15, group=g)
    model('coffee-table.glb', (x + 2.60, 2.55), rot=math.pi / 2, scale=1.0, group=g)
    model('bookcase.glb', (x + 4.10, 3.20), rot=-math.pi / 2, scale=1.05, group=g)
    model('armchair.glb', (x + .10, 2.10), rot=-.6, scale=1.0, group=g)
    model('lamp.glb', (x + 4.15, 1.10), rot=0.0, scale=1.55, group=g)
    # rug
    rug = plain('apt rug', (.60, .57, .53), rough=1.0)
    o = box('apt rug', (x + 1.55, 2.55, .012), (5.2, 4.4, .02), rug, group=g)
    mod = o.modifiers.new('pile', 'DISPLACE')
    tex = bpy.data.textures.new('rug noise', 'CLOUDS')
    tex.noise_scale = .18
    mod.texture = tex
    mod.strength = .012

    # wall art: a wide abstract piece above the bed and a tall one by the sofa
    art_a = plain('art a', (.12, .14, .17), rough=.6, emit=.18)
    art_b = plain('art b', (.55, .38, .22), rough=.55, emit=.12)
    for i, (dx, w, h) in enumerate(((-.65, 1.3, .9), (.55, .7, .9))):
        box(f'art frame {i}', (x - 3.40 + dx, 5.02, 2.42), (w, .05, h), dark, group=g)
        box(f'art canvas {i}', (x - 3.40 + dx, 4.99, 2.42), (w - .08, .03, h - .08),
            art_a if i == 0 else art_b, group=g)
    box('art tall', (x + 4.54, 3.0, 2.0), (.05, 1.1, 1.5), art_b, group=g)

    # ceiling cove + downlights (the room must read even in the dark final act)
    cove = plain('apt cove', (.95, .88, .78), rough=.9, emit=2.2)
    for sx in (-1, 1):
        box(f'cove light {sx}', (x + sx * 4.3, 0, 3.05), (.16, 9.8, .05), cove, group=g)
    for i in range(4):
        for j in range(3):
            cyl(f'downlight {i}-{j}', (x - 2.6 + i * 1.75, -2.6 + j * 3.2, 3.16),
                .09, .02, cove, verts=16, group=g)

    # ---- lights
    area('apt warm key', (x - 1.2, 4.2, 2.80), (x - 2.6, 2.2, 1.0), 260, 3.0, (1, .84, .68), group=g)
    area('apt warm fill', (x + 3.6, 4.0, 2.60), (x + 1.6, 2.4, 1.0), 120, 3.5, (1, .88, .76), group=g)
    area('apt sky fill', (x, -4.6, 2.20), (x, 1.5, 1.1), 170, 6.0, (.72, .84, 1), group=g)
    area('apt bounce', (x, 2.0, 3.15), (x + .4, 1.8, 0), 90, 4.0, (1, .93, .86), group=g)
    spot('bed pool', (x - 3.4, 3.2, 3.05), (x - 3.4, 3.4, .6), 45, (1, .85, .70), size=.35, group=g)
    point('cove bounce', (x, 2.0, 2.80), 30, (.95, .9, .85), radius=1.2, group=g)
    for sx in (-1, 1):
        point(f'bedside glow {sx}', (x - 3.40 + sx * 1.42, 4.32, 1.05), 16, (1, .78, .52), radius=.18, group=g)

    sky_dome()
    city_outside(x, y=26.0)

    return {'bed': bed_at, 'mattress': .62, 'nightstand': (x - 3.40 - 1.42, 4.32),
            'sofa': sofa_at, 'sill': (x - 1.6, -4.75, .40), 'x': x}


# -------------------------------------------------------------------- kitchen
def build_kitchen(x=-96.0):
    g = 'kit'
    floor_mat = textured('kit floor', (.34, .32, .31), (2, 2, 1),
                         variants=('tile_floor.jpg', 'tiles.jpg'))
    marble = textured('kit marble', (.88, .87, .85), (1, 1, 1),
                      variants=('marble.jpg', 'marble_counter.jpg'), rough=.22)
    cab = textured('kit cab', (.20, .16, .13), (1, 1, 1),
                   variants=('wood_walnut.jpg', 'walnut.jpg', 'wood.jpg'))
    white = plain('kit wall', (.80, .79, .77), rough=.85)
    dark = plain('kit dark', (.05, .05, .06), rough=.4, metal=.4)
    steel = plain('kit steel', (.72, .73, .75), rough=.25, metal=1.0)

    box('kit floor', (x, 0, -.10), (8.4, 7.6, .20), floor_mat, group=g)
    box('kit wall back', (x, 3.85, 1.6), (8.4, .20, 3.2), white, group=g)
    box('kit wall left', (x - 4.2, 0, 1.6), (.20, 7.6, 3.2), white, group=g)
    box('kit wall right', (x + 4.2, 0, 1.6), (.20, 7.6, 3.2), white, group=g)
    box('kit ceiling', (x, 0, 3.20), (8.4, 7.6, .10), plain('kit ceil', (.72, .71, .69), rough=.9), group=g)

    # back run of cabinets
    box('kit counter', (x - 1.90, 3.35, .92), (4.5, .66, .05), marble, bevel=.01, group=g)
    box('kit counter body', (x - 1.90, 3.35, .46), (4.5, .62, .88), cab, bevel=.01, group=g)
    for i in range(5):
        box(f'kit drawer {i}', (x - 3.9 + i * .92, 3.03, .46), (.86, .03, .80), cab, bevel=.008, group=g)
        box(f'kit handle {i}', (x - 3.9 + i * .92, 3.01, .80), (.22, .02, .02), brass_steel(steel), group=g)
    box('kit splash', (x - 1.90, 3.72, 1.28), (4.5, .05, .70), marble, group=g)
    box('kit uppers', (x - 1.90, 3.55, 2.30), (4.5, .40, .70), cab, bevel=.01, group=g)
    for i in range(4):
        box(f'kit upper door {i}', (x - 3.6 + i * 1.15, 3.34, 2.30), (1.06, .03, .64), cab, group=g)

    # island with waterfall marble and stools
    isl = (x - .40, 1.20)
    box('island body', (isl[0], isl[1], .44), (2.8, 1.05, .86), cab, bevel=.01, group=g)
    box('island top', (isl[0], isl[1], .90), (3.0, 1.16, .06), marble, bevel=.008, group=g)
    box('island fall L', (isl[0] - 1.48, isl[1], .45), (.05, 1.16, .90), marble, bevel=.006, group=g)
    box('island fall R', (isl[0] + 1.48, isl[1], .45), (.05, 1.16, .90), marble, bevel=.006, group=g)
    box('island shelf', (isl[0], isl[1] + .35, .30), (2.6, .30, .06), cab, group=g)
    for i, dx in enumerate((-.85, .0, .85)):
        model('chair.glb', (isl[0] + dx, isl[1] - 1.05), rot=math.pi, scale=1.0, group=g)

    # coffee machine, kettle, cup shelf, fridge
    box('coffee station', (x - 3.35, 3.32, 1.22), (.34, .40, .52), dark, bevel=.02, group=g)
    box('coffee panel', (x - 3.35, 3.10, 1.28), (.26, .02, .22), plain('coffee panel', (.05, .05, .06), rough=.2, emit=.35), group=g)
    cyl('kettle', (x - 2.55, 3.35, 1.06), .085, .22, steel, verts=20, group=g)
    cyl('kettle lid', (x - 2.55, 3.35, 1.20), .07, .04, dark, verts=18, group=g)
    box('fridge', (x + 3.35, 3.40, .95), (.80, .70, 1.90), steel, bevel=.02, group=g)
    box('fridge gap', (x + 3.35, 3.03, 1.18), (.78, .02, .02), dark, group=g)
    rod('fridge handle', (x + 3.62, 3.01, 1.30), (x + 3.62, 3.01, .95), .012, dark, group=g)
    for i in range(3):
        box(f'open shelf {i}', (x - 1.9, 3.62, 1.86 + i * .30), (3.6, .24, .03),
            plain('kit shelf', (.42, .33, .25), rough=.7), group=g)

    # window over the counter run, morning sun angled into the room
    glass = plain('kit glass', (.70, .80, .88), rough=.05, alpha=.12)
    win = box('kit window', (x - 1.60, 3.84, 2.00), (2.20, .03, 1.30), glass, group=g)
    hide_from_lens(win)
    box('kit window frame', (x - 1.60, 3.82, 2.00), (2.32, .06, 1.42), dark, group=g)
    box('kit window mullion', (x - 1.60, 3.80, 2.00), (.05, .07, 1.34), dark, group=g)
    # pendants above the island
    for i, dx in enumerate((-1.0, 0.0, 1.0)):
        rod(f'pendant cord {i}', (isl[0] + dx, isl[1], 3.18), (isl[0] + dx, isl[1], 2.26), .006, dark, group=g)
        cone(f'pendant shade {i}', (isl[0] + dx, isl[1], 2.18), .13, .20,
             plain('pendant', (.16, .16, .17), rough=.35, metal=.6), group=g)
        sphere(f'pendant bulb {i}', (isl[0] + dx, isl[1], 2.10), .045,
               plain('bulb', (1, .84, .62), emit=8), group=g)

    area('kit window light', (x - 1.6, 3.6, 2.1), (x - 1.7, 0, 1.1), 900, 2.4, (1, .95, .86), group=g)
    spot('kit sun shaft', (x - 2.6, 3.4, 2.5), (x - .6, .2, .8), 800, (1, .92, .78), size=.6,
         angle=38, group=g)
    area('kit fill', (x - .2, .6, 2.60), (x - 1.0, 3.0, 1.2), 180, 3.5, (.82, .88, 1), group=g)
    for i, dx in enumerate((-1.0, 0.0, 1.0)):
        spot(f'pendant light {i}', (isl[0] + dx, isl[1], 2.14), (isl[0] + dx, isl[1], .9), 40,
             (1, .82, .58), size=.08, angle=70, group=g)

    return {'island': isl, 'island_top': .93, 'counter': (x - 1.90, 3.35),
            'worktop': .95, 'mug': (isl[0] - .55, isl[1] + .02, .93 + .045), 'x': x}


def brass_steel(steel):
    return steel


def cone(name, loc, r1, depth, mat, group=None):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r1 * .45,
                                    depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    if group:
        o['group'] = group
    return o


# --------------------------------------------------------------------- street
def build_street(x=20.0):
    g = 'street'
    asphalt = textured('street asphalt', (.10, .10, .11), (3, 3, 1),
                       variants=('asphalt.jpg', 'road.jpg'), rough=.92)
    pave = textured('street pave', (.52, .50, .47), (2, 2, 1),
                    variants=('paving.jpg', 'concrete.jpg'), rough=.88)
    facade = textured('street facade', (.30, .34, .40), (1, 1, 1), rough=.7)
    red_facade = textured('street red', (.42, .17, .13), (1, 1, 1), rough=.75)
    stone = plain('street stone', (.56, .54, .50), rough=.55)
    dark = plain('street dark', (.045, .05, .06), rough=.35, metal=.5)
    glass = plain('street glass', (.30, .44, .52), rough=.06, metal=.25)
    red = plain('carpet', (.42, .035, .05), rough=1.0)
    brass = plain('brass', (.68, .52, .26), rough=.28, metal=1.0)
    velvet = plain('rope', (.55, .05, .07), rough=.85)

    # road, kerb, sidewalk, far sidewalk
    box('road', (x, -7.0, -.30), (70, 12.0, .10), asphalt, group=g)
    box('curb', (x, -1.62, -.06), (70, .34, .32), stone, bevel=.03, group=g)
    box('sidewalk', (x, 1.60, -.06), (70, 6.2, .28), pave, bevel=.02, group=g)
    box('far sidewalk', (x, -13.6, -.06), (70, 2.2, .28), pave, group=g)
    for i in range(18):
        box(f'road line {i}', (x - 34 + i * 4.2, -7.0, -.246), (2.0, .12, .012),
            plain('road paint', (.80, .80, .76), rough=.8), group=g)
    box('road centre', (x, -7.0, -.244), (70, .10, .010),
        plain('road centre paint', (.85, .72, .20), rough=.8), group=g)

    # the building behind the carpet: rust-red cladding with a stone base
    box('facade', (x, 4.62, 8.0), (70, .5, 16), red_facade, group=g)
    box('facade base', (x, 4.44, 1.20), (70, .22, 2.40), stone, bevel=.02, group=g)
    for i in range(26):
        bx = x - 30 + i * 2.6
        box(f'facade fin {i}', (bx, 4.30, 7.4), (.16, .18, 13.0),
            plain('street fin', (.22, .10, .09), rough=.6), group=g)
        for r in range(5):
            box(f'facade win {i}-{r}', (bx, 4.34, 3.4 + r * 2.4), (1.5, .08, 1.3), glass, group=g)
    # lobby: recessed, glass doors, warm interior
    box('lobby recess', (x + 6.0, 3.86, 1.55), (5.6, .10, 3.10), glass, group=g)
    box('lobby mullion', (x + 6.0, 3.80, 1.55), (.10, .14, 3.10), dark, group=g)
    for dx in (-1.35, 1.35):
        box('lobby door', (x + 6.0 + dx, 3.78, 1.45), (1.25, .06, 2.90), glass, group=g)
        box('lobby handle', (x + 6.0 + dx * .35, 3.72, 1.10), (.05, .05, .70), brass, group=g)
    box('lobby soffit', (x + 6.0, 3.40, 3.16), (5.8, 1.4, .14), plain('street soffit', (.82, .80, .76), rough=.8, emit=.5), group=g)
    point('lobby glow', (x + 6.0, 3.30, 2.10), 90, (1, .86, .68), radius=1.2, group=g)
    # canopy over the entrance
    box('canopy', (x + 6.0, 2.60, 3.72), (7.0, 2.6, .16), dark, bevel=.02, group=g)
    box('canopy lip', (x + 6.0, 1.34, 3.64), (7.0, .10, .30), dark, group=g)
    for i in range(6):
        box(f'canopy light {i}', (x + 3.4 + i * 1.05, 2.5, 3.62), (.5, .5, .03),
            plain('canopy lamp', (1, .92, .78), emit=3.0), group=g)

    # red carpet from the canopy to the kerb
    box('red carpet', (x + 4.60, 1.05, .008), (24.0, 2.40, .016), red, group=g)
    box('carpet edge L', (x + 4.60, 2.24, .010), (24.0, .04, .02), brass, group=g)
    box('carpet edge R', (x + 4.60, -.14, .010), (24.0, .04, .02), brass, group=g)

    # press wall on the right of the carpet
    box('press wall', (x + 6, 2.10, 1.42), (3.4, .10, 2.84),
        plain('press wall', (.96, .95, .93), rough=.6), group=g)
    for i in range(4):
        for j in range(3):
            box(f'press logo {i}-{j}', (x + 4.8 + i * .8, 2.04, .78 + j * .82),
                (.34, .02, .12), plain('press logo', (.70, .55, .30), rough=.3, metal=.7), group=g)

    # rope line on brass posts, running the length of the carpet
    for i in range(8):
        bx = x - 4.0 + i * 3.4
        cyl(f'rope post {i}', (bx, 2.25, .52), .035, 1.04, brass, group=g)
        sphere(f'rope knob {i}', (bx, 2.25, 1.07), .07, brass, group=g)
        if i < 7:
            for dz in (.86, .70):
                rod('rope', (bx, 2.25, dz), (bx + 3.4, 2.25, dz), .022, velvet, group=g)

    # street furniture: lamp posts, planters, bollards, a distant bus stop
    for i in range(6):
        lx = x - 22 + i * 9.0
        cyl(f'lamp post {i}', (lx, -1.15, 2.6), .055, 5.2, dark, group=g)
        box(f'lamp head {i}', (lx, -1.15, 5.16), (.5, .2, .08), dark, group=g)
        sphere(f'lamp glass {i}', (lx, -1.15, 5.05), .16, plain('lamp glass', (1, .9, .72), emit=2.2), group=g)
    for i in range(5):
        bx = x - 8 + i * 6.4
        box(f'planter {i}', (bx, .35, .38), (.9, .9, .76),
            plain('planter stone', (.44, .43, .41), rough=.8), bevel=.02, group=g)
        sphere(f'bush {i}', (bx, .35, 1.05), .46,
               plain('bush', (.10, .22, .10), rough=.9), scale=(1, 1, .9), group=g)
    for i in range(10):
        bx = x - 6 + i * 3.0
        cyl(f'bollard {i}', (bx, -1.15, .45), .06, .90, dark, verts=12, group=g)
        sphere(f'bollard cap {i}', (bx, -1.15, .91), .062, brass, group=g)

    # the car: long saloon, dark paint, chrome, headlights on
    cx, cy = x + 17.0, -3.20
    paint = plain('car paint', (.035, .038, .05), rough=.16, metal=.55)
    chrome = plain('car chrome', (.85, .86, .88), rough=.10, metal=1.0)
    tyre = plain('car tyre', (.02, .02, .022), rough=.9)
    car_glass = plain('car glass', (.05, .06, .07), rough=.05, metal=.4, alpha=.55)
    box('car body', (cx, cy, .62), (4.60, 1.86, .56), paint, bevel=.18, group=g)
    box('car lower', (cx, cy, .34), (4.50, 1.90, .26), paint, bevel=.10, group=g)
    box('car cabin', (cx - .28, cy, 1.06), (2.28, 1.62, .40), paint, bevel=.20, group=g)
    box('car roof', (cx - .34, cy, 1.25), (1.86, 1.44, .05), paint, bevel=.02, group=g)
    box('car bonnet', (cx + 1.55, cy, .93), (1.50, 1.78, .10), paint, bevel=.05, group=g)
    box('car boot', (cx - 1.85, cy, .93), (1.00, 1.78, .10), paint, bevel=.05, group=g)
    box('car sill', (cx - .10, cy, .40), (3.50, 1.94, .10), plain('car sill', (.03, .03, .035), rough=.4), bevel=.03, group=g)
    for sy in (.82, -.82):
        box('car side glass', (cx - .28, cy + sy, 1.10), (2.02, .035, .30), car_glass, bevel=.02, group=g)
        box('car b pillar', (cx + .12, cy + sy, 1.12), (.07, .05, .34), plain('car pillar', (.02, .02, .025), rough=.3), group=g)
        box('car chrome strip', (cx - .30, cy + sy * 1.02, .80), (2.90, .02, .025), chrome, group=g)
        box('door seam', (cx + .80, cy + sy * 1.01, .78), (.015, .02, .48), plain('car seam', (.01, .01, .012)), group=g)
    box('windscreen', (cx + 1.02, cy, 1.10), (.06, 1.50, .42), car_glass, rot=(0, math.radians(24), 0), group=g)
    box('rear glass', (cx - 1.38, cy, 1.10), (.06, 1.44, .40), car_glass, rot=(0, math.radians(-26), 0), group=g)
    for wx in (-1.5, 1.5):
        for wy in (-.86, .86):
            cyl('wheel', (cx + wx, cy + wy, .34), .34, .22, tyre, verts=28, rot=(math.pi / 2, 0, 0), group=g)
            cyl('rim', (cx + wx, cy + wy * 1.03, .34), .19, .05, chrome, verts=24, rot=(math.pi / 2, 0, 0), group=g)
            cyl('hub', (cx + wx, cy + wy * 1.05, .34), .06, .03, chrome, verts=16, rot=(math.pi / 2, 0, 0), group=g)
    for wy in (-.60, .60):
        sphere('headlight', (cx + 2.28, cy + wy, .66), .10,
               plain('headlamp', (1, .96, .86), emit=14), scale=(.6, 1.5, .7), group=g)
        box('taillight', (cx - 2.29, cy + wy, .72), (.05, .30, .10),
            plain('taillamp', (.85, .06, .05), emit=6), group=g)
    for i, dx in enumerate((-1.30, 1.70)):
        box(f'car plate {i}', (cx + dx, cy - .93, .52), (.40, .02, .12), chrome, group=g)
    point('headlight spill', (cx + 3.2, cy, .55), 140, (1, .95, .82), radius=.5, group=g)
    box('car seat', (cx - .85, cy, .84), (1.10, 1.40, .18), plain('car leather', (.12, .10, .09), rough=.6), bevel=.04, group=g)
    box('car seat back', (cx - 1.42, cy, 1.02), (.18, 1.40, .48), plain('car leather', (.12, .10, .09), rough=.6), bevel=.04, group=g)

    # a second parked car for depth, further down the road
    box('car2 body', (x - 16, -9.4, .60), (4.2, 1.8, .60),
        plain('car2 paint', (.20, .22, .26), rough=.25, metal=.5), bevel=.16, group=g)
    box('car2 cabin', (x - 16.3, -9.4, 1.10), (2.1, 1.55, .42),
        plain('car2 paint', (.20, .22, .26), rough=.25, metal=.5), bevel=.18, group=g)

    # sky + the buildings across the road
    sky_dome()
    far = plain('far block', (.13, .15, .19), rough=.85)
    far_lit = plain('far window', (.42, .52, .64), rough=.25, emit=.7)
    for i in range(11):
        bx = x - 45 + i * 9.0
        bh = 11 + (i * 7) % 15
        box(f'far block {i}', (bx, -32.0, bh / 2 - .6), (8.5, 7.0, bh), far, bevel=.06, group=g)
        for c in range(3):
            for r in range(int(bh / 3.0)):
                box(f'far win {i}-{c}-{r}', (bx - 2.4 + c * 2.4, -28.4, 1.6 + r * 3.0),
                    (1.2, .08, 1.3), far_lit, group=g)

    # ---- lights: real morning sun plus sky bounce
    bpy.ops.object.light_add(type='SUN', location=(x - 12, -18, 16))
    sun = bpy.context.object
    sun.name = 'morning sun'
    sun.data.energy = 3.0
    sun.data.angle = math.radians(2.0)
    sun.data.color = (1, .94, .84)
    sun.rotation_euler = (math.radians(54), 0, math.radians(32))
    hide_from_lens(sun)
    sun['group'] = g
    area('street key', (x + 2, -7.0, 7.5), (x + 4, .8, 1.2), 5200, 7.0, (1, .91, .78),
         shape='RECTANGLE', spread=5.0, group=g)
    area('street fill', (x - 10, 7.0, 6.0), (x - 2, 1.0, 1.4), 2400, 8.0, (.66, .78, 1.0),
         shape='RECTANGLE', group=g)
    area('street bounce', (x + 6, -2.0, 1.0), (x + 5, 3.0, 2.0), 800, 6.0, (.96, .88, .76),
         shape='RECTANGLE', group=g)

    return {'x': x, 'car': (cx, cy), 'press': (x + 6, 3.30), 'barrier_y': 2.25,
            'carpet_y': 1.05, 'canopy': (x + 6, 2.6)}


# ---------------------------------------------------------------- visibility
def show_set(g):
    """Street geometry is visible only in street shots; the sky always is."""
    for o in bpy.data.objects:
        if o.type == 'LIGHT' or o.get('dynamic'):
            continue
        grp = o.get('group', 'other')
        if grp == 'sky':
            o.hide_render = False
        elif grp in GROUPS:
            o.hide_render = grp != g
