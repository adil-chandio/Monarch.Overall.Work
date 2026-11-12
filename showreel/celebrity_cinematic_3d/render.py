"""Cinematic art-direction pass for the fictional, animated 3D story.

The people are skinned Rocketbox actors; the rooms, street and skyline are
three-dimensional geometry, not background photographs.  This pass adds
physically based materials and licensed props, remodels the sets, revises the
blocking/camera work and constructs a genuinely bent seated pose.
"""
from __future__ import annotations
import argparse
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import bpy
from mathutils import Matrix, Vector
from showreel.celebrity_premium_3d import render as old
from showreel.celebrity_premium_3d.rig_actor import RigPuppet

base = old.base
ASSETS = Path(os.environ.get('CINEMA_ASSETS', '/home/user/cinema-assets'))
FPS = 24


def paint(name, color, roughness=.55, metal=0., emission=0.):
    mat = bpy.data.materials.get('cinema:' + name)
    if mat:
        return mat
    mat = bpy.data.materials.new('cinema:' + name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metal
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return mat


def assign(obj, mat):
    # The primitive meshes are shared. Copy before changing a single object.
    obj.data = obj.data.copy()
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def box(w, pos, dims, mat):
    return assign(w.box(pos, dims, (.5, .5, .5, 1)), mat)


def cylinder(w, pos, radius, length, mat):
    return assign(w.cylinder(pos, radius, length, (.5, .5, .5, 1)), mat)


def soft_box(w, pos, dims, mat, bevel=.04):
    """Physical-radius bevel, suitable for cushions rather than hard blocks."""
    bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
    obj = bpy.context.object
    obj.name = 'soft cushion'
    obj.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new('soft seams', 'BEVEL')
    modifier.width = min(bevel, min(dims)*.8)
    modifier.segments = 4
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for face in obj.data.polygons:
        face.use_smooth = True
    obj.data.materials.append(mat)
    return obj


def mute_texture(material, color, amount):
    """Preserve real texture variation without overpowering the composition."""
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    socket = shader.inputs['Base Color']
    if socket.is_linked:
        source = socket.links[0].from_socket
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MIX'
        mix.inputs[0].default_value = amount
        mix.inputs[2].default_value = (*color, 1)
        links.new(source, mix.inputs[1])
        links.new(mix.outputs[0], socket)


def hide(w, positions):
    for position in positions:
        old.hide_at(w, position, threshold=.012)


def library_materials():
    """Import packed CC0 albedo, roughness and normal maps, discard swatches."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSETS / 'materials.glb'))
    imported = [o for o in bpy.data.objects if o not in before]
    result = {}
    repeats = {'plaster': 3., 'wood': 2., 'floor': 5., 'concrete': 5.,
               'marble': 2., 'planks': 4., 'fabric': 3.}
    for obj in imported:
        if obj.type != 'MESH' or not obj.data.materials:
            continue
        key = obj.name.split('.')[0]
        if key not in repeats:
            continue
        material = obj.data.materials[0].copy()
        material.name = 'cinema texture ' + key
        nodes, links = material.node_tree.nodes, material.node_tree.links
        uv = nodes.new('ShaderNodeUVMap')
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (repeats[key], repeats[key], 1.)
        links.new(uv.outputs['UV'], mapping.inputs['Vector'])
        for node in nodes:
            if node.type == 'TEX_IMAGE':
                links.new(mapping.outputs['Vector'], node.inputs['Vector'])
        result[key] = material
    for obj in imported:
        bpy.data.objects.remove(obj, do_unlink=True)
    if set(result) != set(repeats):
        raise ValueError('material library is incomplete: ' + str(set(result)))
    return result


def import_fit(name, center, bounds, angle=0):
    """Uniformly fit a GLB's bounding box, rotate and center without flattening."""
    path = ASSETS / name
    if not path.is_file():
        raise FileNotFoundError(path)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in objects if o.parent is None]
    bpy.context.view_layer.update()
    points = [o.matrix_world @ Vector(corner) for o in objects if o.type == 'MESH'
              for corner in o.bound_box]
    if not points:
        raise ValueError('asset contains no geometry: ' + str(path))
    lo = Vector([min(v[i] for v in points) for i in range(3)])
    hi = Vector([max(v[i] for v in points) for i in range(3)])
    size = hi - lo
    factor = min(bounds[i] / max(size[i], 1e-6) for i in range(3))
    root = bpy.data.objects.new('prop: ' + name, None)
    bpy.context.scene.collection.objects.link(root)
    for obj in roots:
        obj.parent = root
    root.scale = (factor,) * 3
    root.rotation_euler.z = angle
    rotation = Matrix.Rotation(angle, 3, 'Z')
    root.location = Vector(center) - rotation @ ((lo + hi) * (.5 * factor))
    return root, objects


def text(w, message, position, size, mat):
    curve = bpy.data.curves.new('architectural lettering', 'FONT')
    curve.body = message
    curve.align_x = 'CENTER'
    curve.size = size
    curve.extrude = .001
    curve.bevel_depth = .0004
    ob = bpy.data.objects.new(message, curve)
    w.scene.collection.objects.link(ob)
    ob.location = position
    ob.rotation_euler = (math.pi/2, 0, 0)  # front of building faces -Y
    ob.data.materials.append(mat)
    return ob


def area_relight(w, kind):
    scene = w.scene
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = {'bedroom': -.80, 'kitchen': -.88,
                                    'street': -.92, 'car': -.82, 'night': -1.06}[kind]
    world = scene.world.node_tree.nodes.get('Background')
    if kind == 'street':
        world.inputs['Color'].default_value = (.20, .29, .42, 1)
        world.inputs['Strength'].default_value = .35
    elif kind == 'night':
        world.inputs['Color'].default_value = (.025, .050, .12, 1)
        world.inputs['Strength'].default_value = .24
    else:
        world.inputs['Color'].default_value = (.10, .14, .22, 1)
        world.inputs['Strength'].default_value = .18
    for light in (o for o in scene.objects if o.type == 'LIGHT' and o.data.type == 'AREA'):
        if light.name == 'Dawn window':
            light.data.color = (.64, .79, 1.0); light.data.size = 3.0; light.data.energy = 470
        elif light.name == 'Bedside warmth':
            light.data.color = (1.0, .63, .36); light.data.size = 1.8; light.data.energy = 230
        elif light.name == 'Morning key':
            light.data.color = (1.0, .90, .79); light.data.size = 3.0; light.data.energy = 650
        elif light.name == 'Open sky':
            light.data.color = (.78, .87, 1.0); light.data.size = 4.2; light.data.energy = 850
        elif light.name == 'Warm side':
            light.data.color = (1.0, .76, .55); light.data.size = 2.4
        elif light.name == 'Window edge':
            light.data.color = (.42, .63, 1.0); light.data.size = 1.8; light.data.energy = 580
    if kind == 'night':
        old.add_area('Warm apartment bounce', (2.8, -.9, 2.15), (.3, .3, 1.1),
                     (1., .53, .26), 100, 2.)


class CinematicRig(RigPuppet):
    def __init__(self, asset, kind, role):
        super().__init__(asset, kind, role)
        # Retain the original diffuse/normal maps, add a little skin translucency.
        for obj in self.meshes:
            if obj.name.split('.')[0] != 'Body':
                continue
            for mat in obj.data.materials:
                if not mat or not mat.use_nodes:
                    continue
                node = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if node:
                    node.inputs['Subsurface Weight'].default_value = .035
                    node.inputs['Subsurface Radius'].default_value = (1.0, .45, .27)

    def aim_joint(self, parent, child, target):
        joint = self.rig.pose.bones['mixamorig:' + parent]
        end = self.rig.pose.bones['mixamorig:' + child]
        pivot = self.rig.matrix_world @ joint.head
        current = (self.rig.matrix_world @ end.head) - pivot
        desired = Vector(target) - pivot
        if min(current.length, desired.length) < 1e-6:
            return
        rotation = current.rotation_difference(desired)
        world = Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot)
        joint.matrix = self.rig.matrix_world.inverted() @ world @ self.rig.matrix_world @ joint.matrix
        bpy.context.view_layer.update()

    def animate(self, proxy, base_pos, yaw, sit, walk, targets, smile, t):
        super().animate(proxy, base_pos, yaw, sit, walk, targets, smile, t)
        if self.role == 'hero' and self.kind in ('bedroom', 'car') and sit:
            # A seated skeleton needs forward thighs, bent knees, and shins
            # down to the floor. A foot-only IK target makes a standing lean.
            direction = Vector((math.sin(yaw), -math.cos(yaw), 0))
            for side in ('Left', 'Right'):
                hip = self.rig.matrix_world @ self.rig.pose.bones['mixamorig:' + side + 'UpLeg'].head
                knee_target = hip + direction * .39 + Vector((0, 0, -.025))
                self.aim_joint(side + 'UpLeg', side + 'Leg', knee_target)
                knee = self.rig.matrix_world @ self.rig.pose.bones['mixamorig:' + side + 'Leg'].head
                foot_target = knee + direction * .035 + Vector((0, 0, -.39))
                self.aim_joint(side + 'Leg', side + 'Foot', foot_target)


# premium.Actor constructs this rig, and the inherited scene builders create
# the same visible animated secondary characters using that actor class.
old.RigPuppet = CinematicRig


class Film(old.Film):
    def reset(self, kind):
        self.w = old.BlenderWorld(kind, self.width, self.samples)
        self.kind = kind
        self.extra = []
        self.props = {}
        self.hero = old.Actor(self.w)
        getattr(self, 'build_' + kind)()
        self.dress(kind)
        area_relight(self.w, kind)

    def dress(self, kind):
        # Keep existing action props and contact targets, then improve the set.
        super().dress(kind)
        self.mats = library_materials()
        mute_texture(self.mats['concrete'], (.24, .255, .26), .70)
        mute_texture(self.mats['wood'], (.34, .26, .19), .24)
        self.brass = paint('aged brass', (.38, .25, .12), .28, .72)
        self.darkmetal = paint('blackened metal', (.045, .056, .068), .30, .58)
        self.cream = paint('warm cream', (.64, .57, .47), .74)
        self.glass = paint('deep blue glazing', (.055, .12, .16), .21, .25)
        self.linen = paint('ivory bedding', (.72, .69, .61), .91)
        self.navy = paint('navy wool', (.08, .12, .17), .82)
        self.light = paint('warm practical glow', (1.0, .66, .30), .5, 0, 1.8)
        getattr(self, 'dress_' + kind)()

    def dress_bedroom(self):
        w, m = self.w, self.mats
        # Replace the too-tall box bed; its .57 m mattress now meets the hip.
        hide(w, [(-.3, .40, .37), (-.3, .40, .70), (-.3, 1.1, .83),
                 (-.3, 1.5, .95), (-.3, .31, .82)])
        for ob in w.objects:
            if (ob.location - Vector((0, 0, -.09))).length < .01:
                assign(ob, m['floor'])
            elif (ob.location - Vector((0, 2.4, 3))).length < .01:
                assign(ob, m['plaster'])
        box(w, (-.30, .40, .22), (.87, 1.12, .22), m['wood'])
        soft_box(w, (-.30, .40, .48), (.84, 1.10, .095), self.linen, .045)
        soft_box(w, (-.30, .35, .59), (.82, .74, .04), m['fabric'], .025)
        for x in (-.68, .07):
            pillow = soft_box(w, (x, 1.14, .65), (.32, .25, .08), self.linen, .06)
            pillow.rotation_euler.z = .04 if x < 0 else -.04
        self.props['phone'].scale *= .72
        self.props['screen'].scale *= .72
        self.props['clock'].data.size = .018
        box(w, (-.30, 1.54, .86), (.91, .07, .46), self.navy)
        for x in (-1.05, -.55, -.05, .45):
            box(w, (x, 1.455, .87), (.008, .006, .40), self.brass)
        # Runner, side panel and crown molding provide scale and softness.
        box(w, (-.22, -.15, .003), (1.48, 1.70, .009), self.navy)
        for y in (-1.75, 1.44):
            box(w, (-.22, y, .016), (1.40, .008, .004), self.brass)
        box(w, (0, 2.28, 2.75), (3.0, .035, .045), self.brass)
        box(w, (-2.90, .25, 1.62), (.025, .80, .70), self.navy)
        for y in (-.42, .25, .92):
            box(w, (-2.865, y, 1.62), (.012, .015, .70), self.brass)
        # Dawn window: modeled distant blocks and warm pinprick windows.
        for j, (x, height) in enumerate(((1.29, .36), (1.50, .48), (1.76, .30), (2.04, .52), (2.22, .41))):
            box(w, (x, 2.20, 1.24 + height / 2), (.085, .012, height / 2),
                paint('dawn skyline ' + str(j), (.10 + j*.008, .16 + j*.01, .22 + j*.01), .65))
            for z in (1.28, 1.42, 1.56):
                if z < 1.24 + height:
                    box(w, (x, 2.175, z), (.012, .005, .017), self.light)
        import_fit('vase.glb', (-1.67, 1.57, .62), (.27, .27, .55))
        # Existing bedside lamp gains a warmer, physically present light.
        lamp = next((o for o in w.scene.objects if o.type == 'LIGHT' and o.name == 'Bedside practical'), None)
        if lamp:
            lamp.data.energy = 48

    def dress_kitchen(self):
        w, m = self.w, self.mats
        for ob in w.objects:
            p = ob.location
            if (p - Vector((0, 0, -.09))).length < .01:
                assign(ob, m['floor'])
            elif (p - Vector((0, -.15, .95))).length < .01:
                assign(ob, m['marble'])
            elif (p - Vector((0, -.15, .47))).length < .01:
                assign(ob, m['wood'])
            elif abs(p.y - 1.95) < .01 and abs(p.z - 1.9) < .01:
                assign(ob, m['wood'])
            elif (p - Vector((0, 2.1, 3))).length < .01:
                assign(ob, m['plaster'])
        # Backsplash, seams, cupboard frames and under-cabinet lights.
        box(w, (0, 2.015, 1.24), (2.85, .012, .50), m['marble'])
        for x in (-2.4, -1.8, -1.2, -.6, 0, .6, 1.2, 1.8, 2.4):
            box(w, (x, 1.994, 1.24), (.005, .004, .49), self.darkmetal)
        for z in (.91, 1.24, 1.57):
            box(w, (0, 1.99, z), (2.86, .004, .004), self.darkmetal)
        for x in (-1.2, -.4, .4, 1.2):
            box(w, (x, 1.82, 1.60), (.34, .012, .009), self.light)
            for z in (1.70, 2.10):
                box(w, (x, 1.827, z), (.34, .009, .008), self.brass)
        # Espresso machine and steel details: modeled, not a backdrop.
        box(w, (-1.15, .06, 1.19), (.19, .17, .18), self.darkmetal)
        box(w, (-1.15, -.12, 1.25), (.15, .008, .08), self.brass)
        for x in (-1.23, -1.16, -1.09):
            button = cylinder(w, (x, -.135, 1.29), .012, .012, self.light)
            w.move(button, (x, -.135, 1.29), base.p.getQuaternionFromEuler((math.pi/2, 0, 0)))
        cylinder(w, (-1.15, -.09, 1.04), .04, .10, self.brass)
        import_fit('vase.glb', (1.85, 1.86, 1.02), (.20, .20, .40))

    def dress_street(self):
        w, m = self.w, self.mats
        # Replace the flat-colored ground and backdrop with a dimensional block.
        for ob in w.objects:
            p = ob.location
            if (p - Vector((0, 0, -.09))).length < .01:
                assign(ob, m['concrete'])
            elif (p - Vector((0, 6, 3))).length < .01:
                ob.hide_render = True
            elif abs(p.y - 1.75) < .02 and p.z > 2.9:
                assign(ob, m['plaster'])
                # The original wall slabs overlap the lintel and obstruct the
                # actor.  Meet at the jambs instead, leaving a real doorway.
                if abs(p.x + 1.35) < .01:
                    ob.location.x = -1.875
                    ob.scale.x = .825
                elif abs(p.x - 1.35) < .01:
                    ob.location.x = 1.625
                    ob.scale.x = .575
        hide(w, [(0, 1.83, 1.18)])  # remove the opaque panel behind the door
        # Lit lobby depth behind the animated door, clear of the actor's path.
        lobby = paint('lobby wall', (.18, .20, .20), .78)
        box(w, (0, 3.20, 1.50), (1.02, .06, 1.50), lobby)
        box(w, (-1.02, 2.50, 1.50), (.035, .70, 1.50), self.darkmetal)
        box(w, (1.02, 2.50, 1.50), (.035, .70, 1.50), self.darkmetal)
        box(w, (0, 2.70, 2.60), (.86, .04, .025), self.light)
        old.add_area('Lobby glow', (0, 2.8, 2.45), (0, 1.55, 1.15), (1.0, .75, .50), 120, 1.4)
        old.add_area('Entrance face bounce', (-.6, -1.8, 2.8), (0, 1.5, 1.3), (1., .84, .70), 180, 2.2)
        # Fill the space above the original lintel and add actual upper-story
        # windows and sills; the establishing view should not be a blank wall.
        box(w, (0, 1.75, 5.675), (1.05, .13, .425), m['plaster'])
        for x in (-1.95, -.68, .68, 1.65):
            for z in (3.30, 4.32, 5.35):
                box(w, (x, 1.598, z), (.26, .018, .34), self.glass)
                box(w, (x, 1.574, z), (.010, .008, .34), self.brass)
                box(w, (x, 1.573, z-.35), (.28, .02, .012), self.cream)
        # Slate sidewalk slabs, road, raised curb, lane paint and tactile crosswalk.
        asphalt = paint('asphalt', (.045, .055, .061), .93)
        pavement = paint('paving seam', (.17, .19, .20), .9)
        stripe = paint('road paint', (.72, .68, .54), .87)
        box(w, (0, -4.30, .005), (9, 1.45, .012), asphalt)
        box(w, (0, -2.86, .055), (9, .075, .055), self.cream)
        for x in range(-8, 9):
            box(w, (x * .70, -1.52, .008), (.004, 1.25, .003), pavement)
        for y in (-2.50, -2.0, -1.50, -1.0, -.50, 0, .50, 1.):
            box(w, (0, y, .009), (7, .004, .003), pavement)
        for x in (-5.0, -2.5, 0., 2.5, 5.):
            box(w, (x, -5.20, .023), (.72, .04, .004), stripe)
        for x in (-2.8, -2.35, -1.90, -1.45):
            box(w, (x, -3.55, .023), (.14, .55, .004), stripe)
        # Stone facade, bronze mullions, transom and a deep entrance canopy.
        for x in (-2.55, -1.02, 1.02, 2.24):
            box(w, (x, 1.52, 1.64), (.038, .085, 1.60), self.brass)
        for x in (-2.05, 1.67):
            box(w, (x, 1.54, 1.28), (.32, .035, .84), self.glass)
            for dx in (-.28, 0, .28):
                box(w, (x + dx, 1.48, 1.28), (.014, .025, .84), self.brass)
            box(w, (x, 1.48, 1.28), (.31, .022, .012), self.brass)
        box(w, (0, 1.44, 2.47), (1.15, .08, .075), self.darkmetal)
        box(w, (0, 1.10, 2.62), (1.60, .52, .08), self.darkmetal)
        box(w, (0, 1.08, 2.525), (1.53, .46, .012), self.brass)
        text(w, 'THE MERIDIAN', (0, .575, 2.585), .105, self.brass)
        # Neighboring real 3D architecture, window mullions and cornices.
        for x, width, height, tone in ((-4.3, 1.25, 5.5, 'west'), (4.15, 1.35, 6., 'east'),
                                       (-7., 1.25, 6.8, 'far-west'), (7., 1.35, 6.5, 'far-east')):
            facade = paint('facade ' + tone, (.25, .29, .31) if x < 0 else (.32, .30, .27), .78)
            box(w, (x, 3.02, height / 2), (width, .30, height / 2), facade)
            for z in (1.0, 2.05, 3.15, 4.25, 5.35):
                if z > height - .45:
                    continue
                box(w, (x, 2.69, z), (width*.84, .02, .33), self.glass)
                box(w, (x, 2.66, z), (.018, .018, .33), self.brass)
                box(w, (x, 2.66, z - .34), (width*.86, .025, .018), self.cream)
            box(w, (x, 2.67, height - .12), (width, .12, .08), self.cream)
        # The reverse shot looks across the road, not into an empty blue void.
        for j, x in enumerate((-10.8, -8.1, -5.4, -2.7, 0., 2.7, 5.4)):
            facade = paint('opposite block ' + str(j % 2),
                           (.24, .28, .30) if j % 2 else (.29, .30, .29), .78)
            box(w, (x, -11.5, 2.55), (1.28, .30, 2.55), facade)
            for z in (.75, 1.60, 2.55, 3.50, 4.45):
                box(w, (x, -11.17, z), (1.12, .02, .27), self.glass)
                for dx in (-.54, .0, .54):
                    box(w, (x + dx, -11.14, z), (.014, .018, .27), self.brass)
                box(w, (x, -11.13, z-.28), (1.16, .028, .014), self.cream)
        # Replace simple spheres with actual scanned foliage at the edges.
        for x in (-2.05, 2.05):
            hide(w, [(x, .95, .19), (x, .95, .60), (x+.12, .99, .51), (x-.1, .92, .53)])
        import_fit('planter.glb', (-2.45, .78, .60), (.65, .65, 1.20))
        import_fit('planter.glb', (2.55, .88, .60), (.65, .65, 1.20))
        import_fit('streetLamp.glb', (-3.40, -2.58, 1.72), (.65, .65, 3.45))
        # An authored, CC-BY 3D sedan provides a believable curbside vehicle.
        root, objects = import_fit('car.glb', (3.55, -3.87, .64), (1.85, 5.02, 1.28), -math.pi/2)
        for obj in objects:
            if obj.type != 'MESH':
                continue
            # Omit baked plate/badge meshes; this is a fictional car.
            if obj.name.split('.')[0] in ('body5', 'body6'):
                obj.hide_render = True
            for material in obj.data.materials:
                if material and material.name.startswith('kyardTint:Bodycolor'):
                    node = material.node_tree.nodes.get('Principled BSDF')
                    if node:
                        node.inputs['Base Color'].default_value = (.028, .045, .065, 1)
                        node.inputs['Metallic'].default_value = .65
                        node.inputs['Roughness'].default_value = .24

    def dress_car(self):
        w, m = self.w, self.mats
        leather = paint('car leather', (.11, .085, .074), .48)
        for ob in w.objects:
            p = ob.location
            if (p - Vector((0, 0, -.09))).length < .01:
                assign(ob, m['concrete'])
            elif (p - Vector((.2, .40, 1.02))).length < .01:
                assign(ob, leather)
        # A thin dark window frame reads as a car door, not a white railing.
        assign(self.props['door'], leather)
        assign(self.props['door_top'], self.darkmetal)
        assign(self.props['door_pillar'], self.darkmetal)
        self.props['door_top'].scale.z *= .45
        self.props['door_top'].scale.y *= .75
        self.props['door_pillar'].scale.x *= .70
        # Sculpted upholstery, stitching, console and dashboard silhouette.
        box(w, (.22, .34, .80), (.35, .20, .08), leather)
        box(w, (.22, .46, 1.08), (.33, .07, .32), leather)
        box(w, (.22, .44, 1.47), (.14, .06, .14), leather)
        for x in (-.03, .20, .43):
            box(w, (x, .365, 1.08), (.004, .006, .26), self.brass)
        box(w, (-.68, .0, .96), (.20, .44, .08), self.darkmetal)
        box(w, (-.47, .0, .98), (.12, .30, .025), self.brass)
        # Animated interior trim is moved with the same hinge as the door.
        assign(self.props['inside_handle'], self.darkmetal)
        self.props['door_trim'] = box(w, (0, 0, -20), (.48, .014, .055), leather)
        self.props['door_detail'] = box(w, (0, 0, -20), (.30, .014, .012), self.darkmetal)
        self.props['door_speaker'] = cylinder(w, (0, 0, -20), .09, .014, self.darkmetal)
        self.props['window_switch'] = box(w, (0, 0, -20), (.085, .014, .012), self.darkmetal)
        # Facade beyond the far window rather than the old uniform blue wall.
        for x in (-1.5, 0, 1.5):
            box(w, (x, 5.75, 1.65), (.50, .025, 1.30), self.glass)
            for z in (.7, 1.45, 2.2):
                box(w, (x, 5.70, z), (.50, .02, .014), self.brass)

    def dress_night(self):
        w, m = self.w, self.mats
        # Open the window: buildings beyond the mullions have genuine depth.
        hidden = [(0, 2, 3.), (0, 1.88, 1.8)]
        for x, z in ((-1.2, 1.1), (-.86, 1.), (-.4, 1.1), (.2, 1.), (.75, 1.05), (1.16, 1.08)):
            hidden.append((x, 1.79, z))
            for dz in (-.18, 0, .18):
                hidden.append((x, 1.755, z + dz))
        hide(w, hidden)
        for ob in w.objects:
            if (ob.location - Vector((0, 0, -.09))).length < .01:
                assign(ob, m['floor'])
            elif (ob.location - Vector((1.05, -.3, .72))).length < .01:
                assign(ob, m['wood'])
            elif (ob.location - Vector((1.05, -.3, .37))).length < .01:
                assign(ob, m['wood'])
        assign(self.props['phone'], paint('phone back', (.012, .015, .018), .80))
        box(w, (-3.05, 2, 2.1), (1.53, .09, 2.1), m['plaster'])
        box(w, (3.05, 2, 2.1), (1.53, .09, 2.1), m['plaster'])
        box(w, (0, 2, 3.30), (1.54, .09, .45), m['plaster'])
        box(w, (0, 1.84, .71), (1.54, .035, .05), self.darkmetal)
        city = [(-6.6, 5.5, 1.0, 5.2), (-4.7, 6.6, 1.0, 5.7), (-2.7, 5.1, .75, 4.5),
                (-1.1, 6.4, .70, 5.5), (.55, 5.4, .75, 4.15), (2.35, 7.2, 1.05, 6.3),
                (4.4, 5.5, .85, 4.8), (6.15, 7., .9, 5.8)]
        for j, (x, y, halfwidth, height) in enumerate(city):
            facade = paint('night tower ' + str(j % 3),
                           ((.065, .12, .19), (.075, .14, .22), (.045, .09, .15))[j % 3], .8, 0, .24)
            box(w, (x, y, height/2), (halfwidth, .35, height/2), facade)
            for ix in range(-2, 3):
                for floor in range(1, int(height / .42)):
                    if (j * 17 + ix * 7 + floor * 11) % 5 < 2:
                        continue
                    glow = self.light if (j + floor + ix) % 4 else paint('cool city windows', (.36, .57, .75), .8, 0, 1.1)
                    box(w, (x + ix*halfwidth*.35, y-.36, floor*.42), (.035, .012, .085), glow)
        old.add_area('City blue bounce', (0, 3.1, 4.8), (0, 6.2, 1.8), (.33, .52, 1.0), 430, 5.)
        # Warm furnishings frame the quiet return without hiding the figure.
        import_fit('armchair.glb', (-2.1, .65, .47), (.82, .95, .95), math.radians(12))
        import_fit('planter.glb', (2.10, 1.23, .55), (.60, .60, 1.10))

    def update_bedroom(self, t):
        w = self.w
        b = base.vec((-.05, -.62, 0))
        sit = 1.35
        reach = base.smooth((t - 2.) / 1.4)
        lift = base.smooth((t - 3.8) / 1.3)
        resting = b + base.vec((.26, -.05, .83 - .25*sit))
        table = self.props['handhold']
        reading = b + base.vec((.21, -.30, 1.27 - .25*sit))
        target = base.blend(base.blend(resting, table, reach), reading, lift)
        other = base.blend(b + base.vec((-.26, -.03, .68)), target + base.vec((-.10, -.02, .02)),
                           base.smooth((t-6.4)/1.) * (1-base.smooth((t-8.5)/.8)))
        self.hero.pose(b, sit=sit, headyaw=-.15*lift, targets={1: target, -1: other})
        phone = base.blend(base.vec((.70, -.53, .83)), target + base.vec((.02, -.025, .08)), reach)
        # The display faces the viewer on the table, then turns toward its
        # owner as he reads.  It is a phone, not the former tablet-sized prop.
        phone_angle = math.pi * lift
        q = base.qz(phone_angle)
        w.move(self.props['phone'], phone, q)
        w.move(self.props['screen'], phone + base.rot((0, -.011, 0), phone_angle), q)
        self.props['clock'].location = tuple(phone + base.rot((0, -.014, .018), phone_angle))
        self.props['clock'].rotation_euler = (math.pi/2, 0, phone_angle)
        return w.view((2.3, -4.1, 1.95), (.05, -.35, .85))

    def update_street(self, t):
        result = super().update_street(t)
        # Swing outward, away from the emerging actor. The old inward sweep
        # intersected his shoulder and arm during the opening frames.
        angle = -base.smooth((t - 22.9) / 1.2) * 1.25
        pivot = base.vec((-.8, 1.67, 0))
        self.w.move(self.props['door'], pivot + base.rot((.8, 0, 1.18), angle), base.qz(angle))
        self.w.move(self.props['knob'], pivot + base.rot((1.4, -.07, 1.10), angle))
        return result

    def update_car(self, t):
        result = super().update_car(t)
        w = self.w
        u = t - 46.293
        angle = -.65 * (1 - base.smooth((u - .7) / 1.9))
        pivot = base.vec((-.52, -.72, 0))
        for name, offset in (('door_trim', (.59, -.066, .82)),
                             ('door_detail', (.70, -.080, .91)),
                             ('door_speaker', (.34, -.082, .62)),
                             ('window_switch', (.88, -.082, .84))):
            pos = pivot + base.rot(offset, angle)
            if name == 'door_speaker':
                q = old.bpy_quat_mul(base.qz(angle), base.p.getQuaternionFromEuler((math.pi/2, 0, 0)))
            else:
                q = base.qz(angle)
            w.move(self.props[name], pos, q)
        return result

    def cinematography(self, t):
        # Keep story-aware hero/fan coverage, then reframe the establishing and
        # interior shots to include the newly modeled space.
        super().cinematography(t)
        w = self.w
        if t < 3.8:
            start, end = 0., 3.8
            eye, target, angle, stop = Vector((2.05, -4.25, 1.90)), Vector((.08, -.48, .87)), 45, 6.3
        elif t < 11.914:
            start, end = 3.8, 11.914
            eye, target, angle, stop = Vector((1.42, -3.05, 1.58)), Vector((-.04, -.58, .95)), 37, 5.6
        elif t < 17.237:
            start, end = 11.914, 17.237
            eye, target, angle, stop = Vector((2.05, -3.65, 2.06)), Vector((.02, .26, 1.22)), 40, 5.6
        elif t < 20.15:
            start, end = 17.237, 20.15
            eye, target, angle, stop = Vector((2.25, -9.8, 3.75)), Vector((.30, -.55, 1.15)), 53, 8.0
        elif t < 24.2:
            # Hold the wide as the door begins to swing, rather than cutting
            # to a frame filled only by the closed door.
            start, end = 20.15, 24.2
            eye, target, angle, stop = Vector((-2.9, -4.9, 2.2)), Vector((.45, -.35, 1.14)), 43, 6.3
        elif t < 29.81:
            # Keep the doorway and moving actor visible, rather than tracking
            # directly behind the foreground photographer's head.
            torso = Vector(self.hero.torso.location)
            target = Vector((torso.x, torso.y, 1.18))
            eye = target + Vector((.10, -4.15, .85))
            angle, stop, start, end = 42, 6.3, 24.2, 29.81
        elif 46.293 <= t < 50.544:
            start, end = 46.293, 50.544
            eye, target, angle, stop = Vector((1.16, -2.55, 1.60)), Vector((.06, -.02, 1.28)), 35, 5.6
        elif t >= 50.544:
            start, end = 50.544, 60.
            eye, target, angle, stop = Vector((3.05, -4.5, 2.35)), Vector((.10, .60, 1.25)), 42, 6.3
        else:
            return
        u = base.smooth((t-start) / max(.01, end-start))
        eye = eye + (target-eye) * (.055*u)
        old.look_camera(w.scene, eye, target, angle, stop)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--width', type=int, default=576)
    p.add_argument('--samples', type=int, default=8)
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--end', type=float, default=60)
    p.add_argument('--stills', default='')
    p.add_argument('--out', type=Path, default=Path('/home/user/cinema-cinematic-frames'))
    args = p.parse_args()
    if not 0 <= args.start < args.end <= 60 or args.width < 16 or args.samples < 1:
        raise SystemExit('invalid render settings')
    args.out.mkdir(parents=True, exist_ok=True)
    film = Film(args.width, args.samples)
    if args.stills:
        jobs = [(round(float(s)*FPS), float(s), f'still_{float(s):05.2f}.png') for s in args.stills.split(',')]
    else:
        jobs = [(f, f/FPS, f'frame_{f:05d}.png') for f in range(math.ceil(args.start*FPS), math.ceil(args.end*FPS))]
    started = time.monotonic()
    print('JOBS', len(jobs), 'WIDTH', args.width, 'SAMPLES', args.samples, flush=True)
    for i, (frame, t, name) in enumerate(jobs):
        film.render_time(t, args.out / name)
        if i % 12 == 0 or i == len(jobs)-1:
            print('FRAME', frame, 'done', i+1, '/', len(jobs), 'elapsed', round(time.monotonic()-started, 1), flush=True)
    print('DONE', args.out, round(time.monotonic()-started, 1), flush=True)


if __name__ == '__main__':
    main()
