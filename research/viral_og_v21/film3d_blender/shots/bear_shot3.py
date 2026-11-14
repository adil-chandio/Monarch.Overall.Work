#!/usr/bin/env python3
"""Cave bear, shot 3 — real Blender geometry, built in code and rendered with Cycles.

This replaces the raymarched "blob" of the previous cut with an actual mesh: a
subdivided body with per-part deformation, a sculpted head (brow, orbits, muzzle,
ears), four legs, a shaded coat (no strand hair: see notes), a rock floor, a fire, and a
camera with depth of field.

Everything is authored here so the shot is reproducible: no .blend is required to
start, and the script writes its own .blend + PNG next to itself.

    LD_LIBRARY_PATH=tools/blender_local/x11_shim python3 shots/bear_shot3.py --stills
"""
from __future__ import annotations

import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# find the repo root by walking up until tools/blender_local exists
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "tools", "blender_local")) and ROOT != "/":
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "blender_local"))

from blender_env import load_bpy            # noqa: E402

bpy = load_bpy()
from mathutils import Vector, Euler          # noqa: E402


# --------------------------------------------------------------------- helpers
def new_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def principled(name, base, rough=0.6, spec=0.4, sss=0.0, sss_col=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        if sss_col:
            b.inputs["Subsurface Radius"].default_value = sss_col
    return mat


def noise_bump(mat, scale=40.0, strength=0.25, detail=6.0):
    """Procedural surface relief: keeps the mesh from reading as plastic."""
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = detail
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.03
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return tex


# --------------------------------------------------------------------- bear
def build_bear(col, face=True):
    """A cave bear: heavy shoulder hump, low head, short blunt muzzle, small ears.

    Built from one subdivided cube chain (so it deforms smoothly) plus separate
    head/limb meshes, then joined. Measurements follow Ursus spelaeus proportions
    scaled to ~2.9 m nose-to-tail, 1.5 m at the shoulder.
    """
    parts = []

    def capsule(name, p0, p1, r0, r1, verts=24):
        """Tapered tube between two points: legs, neck, muzzle."""
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        length = d.length
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r0, radius2=r1,
                                        depth=length, location=(0, 0, 0))
        o = bpy.context.object
        o.name = name
        # point +Z of the cone along d
        quat = d.to_track_quat("Z", "Y")
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = quat
        o.location = p0 + d * 0.5
        parts.append(o)
        return o

    def ellipsoid(name, loc, scale, subdiv=3):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=1.0, location=loc)
        o = bpy.context.object
        o.name = name
        o.scale = scale
        parts.append(o)
        return o

    # ---- body volumes (metres, origin at the feet, nose towards +Y)
    ellipsoid("torso", (0, -0.05, 0.98), (0.46, 0.76, 0.50), 4)
    ellipsoid("hump", (0, 0.26, 1.27), (0.33, 0.40, 0.28), 3)      # shoulder hump
    ellipsoid("rump", (0, -0.62, 0.94), (0.40, 0.38, 0.44), 3)
    ellipsoid("chest", (0, 0.56, 0.88), (0.41, 0.34, 0.47), 3)
    # neck has to leave a gap under the head, otherwise the remesh welds head to chest
    capsule("neck", (0, 0.84, 0.99), (0, 1.12, 1.05), 0.245, 0.185)

    # ---- head: carried LOW and forward, under the shoulder hump. That hump-over-head
    # silhouette is the whole read of a cave bear; if the head is level with the hump
    # the animal turns into one lump (see earlier test frames).
    ellipsoid("head", (0, 1.32, 1.14), (0.250, 0.300, 0.245), 4)
    ellipsoid("brow", (0, 1.455, 1.215), (0.200, 0.100, 0.098), 3)  # heavy brow ridge
    capsule("muzzle", (0, 1.455, 1.100), (0, 1.790, 1.010), 0.132, 0.072)
    capsule("jaw", (0, 1.455, 1.040), (0, 1.745, 0.975), 0.110, 0.064)
    ellipsoid("nose", (0, 1.800, 1.012), (0.060, 0.044, 0.044), 3)
    for sx in (-1, 1):
        ellipsoid(f"ear{sx}", (0.196 * sx, 1.275, 1.315), (0.064, 0.042, 0.074), 2)
        ellipsoid(f"cheek{sx}", (0.152 * sx, 1.375, 1.065), (0.098, 0.112, 0.112), 2)

    # ---- legs: fore pair forward of the hump, hind pair under the rump
    for sx in (-1, 1):
        capsule(f"fore{sx}", (0.30 * sx, 0.56, 0.90), (0.31 * sx, 0.62, 0.10), 0.152, 0.098)
        ellipsoid(f"forepaw{sx}", (0.32 * sx, 0.68, 0.075), (0.150, 0.21, 0.075), 2)
        capsule(f"hind{sx}", (0.33 * sx, -0.56, 0.90), (0.34 * sx, -0.60, 0.10), 0.150, 0.095)
        ellipsoid(f"hindpaw{sx}", (0.35 * sx, -0.48, 0.072), (0.145, 0.20, 0.072), 2)
    capsule("tail", (0, -0.92, 1.05), (0, -1.02, 1.00), 0.05, 0.03)

    # join into one mesh, then smooth
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    bear = bpy.context.object
    bear.name = "BEAR_body"

    # remesh so the volumes read as one skin, not as glued balls
    vox = bear.modifiers.new("remesh", "REMESH")
    vox.mode = "VOXEL"
    vox.voxel_size = 0.026
    vox.adaptivity = 0.0
    bpy.ops.object.modifier_apply(modifier=vox.name)

    # relax the voxel stair-stepping
    sm = bear.modifiers.new("smooth", "SMOOTH")
    sm.factor = 1.0
    sm.iterations = 8
    bpy.ops.object.modifier_apply(modifier=sm.name)

    dec = bear.modifiers.new("dec", "DECIMATE")
    dec.ratio = 0.30
    bpy.ops.object.modifier_apply(modifier=dec.name)

    # a second, finer relax pass + subdivision for the shading normal
    sub = bear.modifiers.new("sub", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1

    # ---- fur: real strands on the silhouette
    bpy.context.view_layer.objects.active = bear
    bear.data.materials.append(principled("BEAR_fur", (0.062, 0.044, 0.032), rough=0.78,
                                          spec=0.25, sss=0.0))
    noise_bump(bear.data.materials[0], scale=48.0, strength=0.34, detail=8.0)

    # fur: a shell over the body proved to read as a ghost second silhouette
    # (it did not follow the pose tightly enough and its displaced copy showed up as
    # a woolly outline next to the body). Dropped: the coat is shading only, on the
    # body mesh itself, plus the bump below. Everything visible is the bear.
    fur = None

    if not face:
        bear["face_parts"] = []
        bear["fur"] = "shading-only"
        link(bear, col)
        return bear

    # ---- face: a young cave bear reads from three marks only - eye, nose, mouth
    # The body has been remeshed and relaxed by now, which moves the surface by a
    # couple of centimetres: anything placed from hand-written coordinates ends up
    # buried inside the head (that is exactly what happened on the first pass - two
    # spheres rendered nowhere and only the nose showed). So every mark is placed by
    # casting a ray at the finished mesh and sitting it just proud of the hit point.
    face = []

    def surface_hit(origin, direction):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = bear.evaluated_get(dg)
        ok, loc, nor, _ = ev.ray_cast(Vector(origin), Vector(direction).normalized())
        return (Vector(loc), Vector(nor)) if ok else (None, None)

    def eye(sx):
        # from the front, a little to the side: the natural eye socket direction
        d = Vector((0.62 * sx, 0.70, 0.30)).normalized()
        origin = Vector((0.0, 1.32, 1.14)) + d * 0.9
        loc, nor = surface_hit(origin, -d)
        if loc is None:
            print(f"WARN eye{sx}: no surface hit")
            return
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, segments=24, ring_count=12,
                                             location=loc - nor * 0.017)
        o = bpy.context.object
        o.name = f"FACE_eyeball_{sx}"
        o.data.materials.append(principled("EYE_white", (0.055, 0.042, 0.034), rough=0.20, spec=0.5))
        # iris: sits on the front of the eyeball, facing the same way as the socket
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.017, segments=20, ring_count=10,
                                             location=loc - nor * 0.017 + nor * 0.015)
        o2 = bpy.context.object
        o2.name = f"FACE_iris_{sx}"
        o2.scale = (1.0, 1.0, 0.55)
        o2.data.materials.append(principled("EYE_iris", (0.006, 0.005, 0.004), rough=0.08, spec=1.0))
        face.extend([o, o2])

    for sx in (-1, 1):
        eye(sx)

    # nose pad: wet, dark, and the only specular thing on the animal
    loc, nor = surface_hit((0.0, 2.6, 1.045), (0.0, -1.0, 0.0))
    if loc is not None:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.050, segments=24, ring_count=12,
                                             location=loc + nor * 0.008)
        nose = bpy.context.object
        nose.name = "FACE_nose_pad"
        nose.scale = (1.0, 0.55, 0.80)
        nose.data.materials.append(principled("NOSE_wet", (0.030, 0.026, 0.024), rough=0.34, spec=0.55))
        face.append(nose)
    else:
        print("WARN nose: no surface hit")

    # mouth line: a thin dark curve tucked under the muzzle, sampled on the skin
    pts = []
    for x in (-0.085, -0.05, 0.0, 0.05, 0.085):
        loc, nor = surface_hit((x, 2.6, 0.965), (0.0, -1.0, 0.0))
        if loc is not None:
            pts.append((x, loc.y + 0.004, 0.975))
    if len(pts) >= 3:
        cu = bpy.data.curves.new("mouth", type="CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.006
        cu.bevel_resolution = 2
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, co in zip(sp.bezier_points, pts):
            bp.co = co
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        mouth = bpy.data.objects.new("FACE_mouth", cu)
        col.objects.link(mouth)
        mouth.data.materials.append(principled("MOUTH", (0.006, 0.005, 0.004), rough=0.55))
        face.append(mouth)

    for o in face:
        link(o, col)
        o.parent = bear
        o.matrix_parent_inverse = bear.matrix_world.inverted()
    bear["face_parts"] = [o.name for o in face]
    bear["fur"] = "shading-only"

    link(bear, col)
    return bear


# --------------------------------------------------------------------- set
def build_set(col):
    """Cave floor: a displaced grid, limestone-ish, so the bear has something to stand on."""
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "CAVE_floor"
    tex = bpy.data.textures.new("rock", type="CLOUDS")
    tex.noise_scale = 1.2
    disp = floor.modifiers.new("disp", "DISPLACE")
    disp.texture = tex
    disp.strength = 0.35
    disp.mid_level = 0.4
    sub = floor.modifiers.new("sub", "SUBSURF")
    sub.levels = 6
    floor.data.materials.append(principled("ROCK", (0.055, 0.050, 0.045), rough=0.9, spec=0.15))
    noise_bump(floor.data.materials[0], scale=14.0, strength=0.5)

    # cave wall: a curved backdrop so the bear is inside a space, not floating
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=9.0, depth=9.0,
                                        location=(0, 0, 3.0), rotation=(0, 0, 0))
    wall = bpy.context.object
    wall.name = "CAVE_wall"
    wtex = bpy.data.textures.new("wall_rock", type="MUSGRAVE")
    wtex.noise_scale = 2.2
    wdisp = wall.modifiers.new("wd", "DISPLACE")
    wdisp.texture = wtex
    wdisp.strength = 0.9
    wsub = wall.modifiers.new("ws", "SUBSURF")
    wsub.levels = 4
    wm = principled("ROCK_wall", (0.045, 0.042, 0.040), rough=0.95, spec=0.1)
    noise_bump(wm, scale=6.0, strength=0.6)
    wall.data.materials.append(wm)

    # fire: a small stone ring, embers as a light source
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.075,
                                     location=(1.25, -3.35, 0.06))
    ring = bpy.context.object
    ring.name = "FIRE_ring"
    ring.data.materials.append(principled("STONE", (0.030, 0.028, 0.026), rough=0.95))
    for i in range(7):
        a = i / 7 * math.tau
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.10,
                                             location=(1.25 + math.cos(a) * 0.42,
                                                       -3.35 + math.sin(a) * 0.42, 0.04))
        bpy.context.object.data.materials.append(ring.data.materials[0])

    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.55, location=(1.25, -3.35, 0.20),
                                        rotation=(0, 0.9, 0))
    log = bpy.context.object
    log.data.materials.append(principled("CHARRED", (0.012, 0.009, 0.007), rough=0.95))

    # fire light: warm, flickering (animated in the HDR/video pass, fixed here)
    bpy.ops.object.light_add(type="POINT", location=(1.25, -3.35, 0.42))
    fire = bpy.context.object
    fire.name = "LIGHT_fire"
    fire.data.energy = 900.0
    fire.data.color = (1.0, 0.42, 0.13)
    fire.data.shadow_soft_size = 0.22

    # a cold fill from the cave mouth (behind camera, very low)
    bpy.ops.object.light_add(type="AREA", location=(0.0, 6.0, 2.2))
    fill = bpy.context.object
    fill.name = "LIGHT_mouth"
    fill.data.energy = 200.0
    fill.data.color = (0.42, 0.58, 0.95)
    fill.data.size = 4.0
    fill.rotation_euler = Euler((math.radians(-70), 0, 0))

    bpy.ops.object.light_add(type="AREA", location=(3.4, -2.6, 2.4))
    key = bpy.context.object
    key.name = "LIGHT_torch"
    key.data.energy = 260.0
    key.data.color = (1.0, 0.62, 0.34)
    key.data.size = 0.8
    key.rotation_euler = (Vector((0, 0.2, 1.1)) - Vector((3.4, -2.6, 2.4))).to_track_quat("-Z", "Y").to_euler()

    bpy.ops.object.light_add(type="AREA", location=(-2.2, -1.6, 2.0))
    rim = bpy.context.object
    rim.name = "LIGHT_rim"
    rim.data.energy = 95.0
    rim.data.color = (0.38, 0.52, 0.90)
    rim.data.size = 2.6
    rim.rotation_euler = (Vector((0, 0.3, 1.15)) - Vector((-2.2, -1.6, 2.0))).to_track_quat("-Z", "Y").to_euler()

    for o in (floor, wall, ring, log, fire, fill, key, rim):
        link(o, col)
    return floor


def build_camera(col, target=(0, 0.42, 1.05), loc=(3.35, 4.75, 1.26)):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = "CAM_shot3"
    cam.data.lens = 44.0
    cam.data.sensor_width = 36.0
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (Vector(target) - Vector(loc)).length
    cam.data.dof.aperture_fstop = 3.5
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    link(cam, col)
    return cam


# --------------------------------------------------------------------- render
def setup_render(samples=96, res=(640, 360)):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.image_settings.file_format = "PNG"
    # a hint of haze, so the fire has something to light
    world = bpy.data.worlds.new("WORLD_cave")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.004, 0.006, 0.012, 1)
    bg.inputs["Strength"].default_value = 1.0
    sc.world = world
    vol = world.node_tree.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.008
    vol.inputs["Anisotropy"].default_value = 0.45
    world.node_tree.links.new(vol.outputs["Volume"], world.node_tree.nodes["World Output"].inputs["Volume"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="render the still frames")
    ap.add_argument("--samples", type=int, default=96)
    ap.add_argument("--res", type=int, nargs=2, default=(640, 360))
    a = ap.parse_args()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    col_bear, col_set, col_cam = new_collection("COL_bear"), new_collection("COL_set"), new_collection("COL_camera")
    bear = build_bear(col_bear)
    build_set(col_set)
    cam = build_camera(col_cam)
    bpy.context.scene.camera = cam
    setup_render(a.samples, tuple(a.res))

    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)
    blend = os.path.join(out_dir, "bear_shot3.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("blend:", blend)

    if a.stills:
        for i, (loc, tgt) in enumerate([((3.3, 3.5, 1.60), (0, 0.30, 1.10)),      # 3/4 front
                                        ((4.5, 0.55, 1.40), (0, 0.25, 1.05)),      # side
                                        ((1.35, 3.30, 0.85), (0, 0.35, 1.15))]):   # low hero
            cam.location = Vector(loc)
            cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
            path = os.path.join(out_dir, f"shot3_view{i}.png")
            bpy.context.scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            print("wrote", path, os.path.getsize(path))
    print("faces:", len(bear.data.polygons), "verts:", len(bear.data.vertices))


if __name__ == "__main__":
    main()
