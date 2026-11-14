#!/usr/bin/env python3
"""Cave bear, 10 s animated shot — real Blender animation, Cycles CPU.

Beats (frames at 24 fps):
  0–40    the animal stands, breathing, fire flickering, embers rising
  40–130  it lowers its head and swings towards the lens
  130–200 it takes two heavy steps forward (whole rig moves, feet planted on the
          contact frames), head low
  200–240 it stops, lifts its head, breath visible in the cold

Everything is keyframed here so the shot is reproducible from this file alone.

    python3 shots/bear_walk.py --preview          # 1 frame in 3, 400x225
    python3 shots/bear_walk.py --final            # full 640x360, 48 spp
"""
from __future__ import annotations

import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.isdir(os.path.join(ROOT, "tools", "blender_local")) and ROOT != "/":
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "blender_local"))
sys.path.insert(0, HERE)

from blender_env import load_bpy              # noqa: E402

bpy = load_bpy()
from mathutils import Vector                  # noqa: E402

import bear_shot3 as B                        # reuse the character + set builders  # noqa: E402

FPS = 24
DUR = 10.0


# ------------------------------------------------------------------ animation
def key_rig(bear, fire, cam):
    """Block the shot on whole frames: pose in, pose out, no interpolation guesswork."""
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start = 1
    sc.frame_end = int(DUR * FPS)

    def key(ob, path, frame, value):
        setattr(ob, path, value)
        ob.keyframe_insert(data_path=path, frame=frame)

    # the animal's root: stands, steps forward, stops
    root = bear
    key(root, "location", 1, (0.0, 0.0, 0.0))
    key(root, "location", int(1.6 * FPS), (0.0, 0.0, 0.0))
    # two heavy steps: 0.55 m each, with the body dipping on the contact frames
    for i, (t0, t1, y) in enumerate([(1.9, 2.35, -0.30), (2.55, 3.0, -0.62)]):
        key(root, "location", int(t0 * FPS), (0.0, y + 0.30, -0.030))
        key(root, "location", int(t1 * FPS), (0.0, y, 0.0))
    key(root, "location", 6.0 * FPS, (0.0, -0.62, 0.0))

    # head: low and forward, then up at the end. The head is the whole performance.
    key(root, "rotation_euler", 1, (0.0, 0.0, 0.0))
    key(root, "rotation_euler", int(4.0 * FPS), (math.radians(-7), 0.0, math.radians(-5)))
    key(root, "rotation_euler", int(6.0 * FPS), (math.radians(-3), 0.0, math.radians(2)))
    key(root, "rotation_euler", int(8.6 * FPS), (math.radians(6), 0.0, 0.0))

    # breathing: chest scale, 5 s cycle, so the animal is never frozen
    for f in range(1, int(DUR * FPS) + 1, 6):
        t = f / FPS
        key(root, "scale", f, (1.0, 1.0, 1.0 + 0.012 * math.sin(t * 2 * math.pi / 2.6)))

    # the fire: energy flutter, plus an ember birth/death rhythm
    for f in range(1, int(DUR * FPS) + 1, 3):
        t = f / FPS
        n = (math.sin(t * 13.1) * 0.5 + 0.5) * (math.sin(t * 7.7 + 1.3) * 0.5 + 0.5)
        fire.energy = 900.0 * (0.72 + 0.55 * n)
        fire.keyframe_insert(data_path="energy", frame=f)

    # camera: a slow push in and a slight drop, so the step forward has weight
    key(cam, "location", 1, (3.35, 4.75, 1.26))
    key(cam, "location", int(DUR * FPS), (3.05, 4.30, 1.22))
    cam.keyframe_insert(data_path="rotation_euler", frame=1)
    tgt0 = Vector((0, 0.42, 1.05))
    tgt1 = Vector((0, -0.30, 1.05))
    cam.rotation_euler = (tgt0 - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=1)
    cam.location = Vector((3.9, 4.5, 1.25))
    cam.rotation_euler = (tgt1 - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=int(DUR * FPS))


def key_face_beat(bear, fire, cam):
    """6 s face shot: the head lifts towards the lens, breath, fire flicker.

    The camera sits in front of the muzzle, below the line of the brow, so the eyes
    and the nose pad are the only specular marks in the frame. The animal does not
    walk here - the beat is "look at it", not "watch it move".
    """
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, 6 * FPS
    end = 6 * FPS

    def key(ob, path, frame, value):
        setattr(ob, path, value)
        ob.keyframe_insert(data_path=path, frame=frame)

    # head comes up and turns into the lens
    key(bear, "rotation_euler", 1, (math.radians(-2.0), 0.0, math.radians(-7.0)))
    key(bear, "rotation_euler", int(2.4 * FPS), (math.radians(-5.0), 0.0, math.radians(-4.0)))
    key(bear, "rotation_euler", end, (math.radians(-8.0), 0.0, math.radians(-1.5)))
    # breath: one and a half cycles, on a 3.6 s clock
    for f in range(1, end + 1, 5):
        t = f / FPS
        key(bear, "scale", f, (1.0, 1.0, 1.0 + 0.010 * math.sin(t * 2 * math.pi / 3.6)))

    for f in range(1, end + 1, 3):
        t = f / FPS
        n = (math.sin(t * 11.3) * 0.5 + 0.5) * (math.sin(t * 6.1 + 0.7) * 0.5 + 0.5)
        fire.energy = 780.0 * (0.7 + 0.6 * n)
        fire.keyframe_insert(data_path="energy", frame=f)

    # camera: starts wide-ish on the head, ends close on the eye
    lens = cam.data
    key(lens, "lens", 1, 46.0)
    key(lens, "lens", end, 58.0)
    key(cam, "location", 1, (1.15, 3.25, 1.40))
    key(cam, "location", end, (0.95, 3.00, 1.36))
    t0 = Vector((0.02, 1.34, 1.20))
    t1 = Vector((0.0, 1.44, 1.18))
    cam.rotation_euler = (t0 - Vector((1.15, 3.25, 1.40))).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=1)
    cam.location = Vector((0.95, 3.00, 1.36))
    cam.rotation_euler = (t1 - Vector((0.95, 3.00, 1.36))).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=end)


def add_eye_light(target=(0.03, 1.42, 1.18), loc=(1.05, 3.55, 1.90), energy=110.0):
    """A small soft source just off the lens for the face beat.

    Without it the head is lit only by the fire behind the animal, so the eyes and
    the muzzle fall into shadow and the face reads as a dark lump with a shiny nose.
    This is a lighting change only - no geometry, nothing added to the frame.
    """
    bpy.ops.object.light_add(type="AREA", location=loc)
    lt = bpy.context.object
    lt.name = "LIGHT_eye"
    lt.data.energy = energy
    lt.data.color = (1.0, 0.82, 0.68)
    lt.data.size = 1.6
    lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return lt


def add_embers(col, base=(1.25, -3.35, 0.35), n=90, seed=3):
    """Embers are geometry, not compositing: they catch the fire light and parallax."""
    import random
    rng = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.008, location=base)
    proto = bpy.context.object
    proto.name = "FX_ember_src"
    proto.data.materials.append(B.principled("EMBER", (1.0, 0.35, 0.08), rough=0.4))
    m = proto.data.materials[0]
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1.0, 0.35, 0.06, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 6.0
    B.link(proto, col)

    for i in range(n):
        e = proto.copy()
        e.name = f"FX_ember_{i:03d}"
        col.objects.link(e)
        x0 = base[0] + rng.uniform(-0.35, 0.35)
        y0 = base[1] + rng.uniform(-0.35, 0.35)
        z0 = base[2] + rng.uniform(0.0, 0.2)
        rise = rng.uniform(0.8, 2.4)
        len_f = rng.randint(int(0.8 * FPS), int(2.6 * FPS))
        start = rng.randint(1, int(DUR * FPS) - len_f)
        drift = rng.uniform(-0.25, 0.25)
        e.location = (x0, y0, z0)
        e.keyframe_insert(data_path="location", frame=start)
        e.location = (x0 + drift, y0 + drift * 0.6, z0 + rise)
        e.keyframe_insert(data_path="location", frame=start + len_f)
        # shrink to nothing at the end of life
        e.scale = (1, 1, 1)
        e.keyframe_insert(data_path="scale", frame=start)
        e.scale = (0.05, 0.05, 0.05)
        e.keyframe_insert(data_path="scale", frame=start + len_f)
    proto.hide_render = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--samples", type=int, default=None)
    ap.add_argument("--res", type=int, nargs=2, default=None, help="override output size")
    ap.add_argument("--step", type=int, default=1, help="render every Nth frame")
    ap.add_argument("--frames", type=int, nargs=2, default=None, help="frame range")
    ap.add_argument("--face", action="store_true", help="include eyes / nose / mouth")
    ap.add_argument("--tag", default=None, help="output prefix (default: preview/final/test)")
    ap.add_argument("--face-beat", action="store_true",
                    help="render the 6 s face beat instead of the walk")
    a = ap.parse_args()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    col_bear = B.new_collection("COL_bear")
    col_set = B.new_collection("COL_set")
    col_cam = B.new_collection("COL_camera")
    col_fx = B.new_collection("COL_fx")

    # The script earns the face later: S3/S4 are the animal as a shape in the cave,
    # so they are shot without the eyes/nose mouth geometry.
    bear = B.build_bear(col_bear, face=a.face)
    B.build_set(col_set)
    cam = B.build_camera(col_cam)
    bpy.context.scene.camera = cam
    fire = bpy.data.objects["LIGHT_fire"]
    add_embers(col_fx)
    if a.face_beat:
        add_eye_light()
        key_face_beat(bear, fire.data, cam)
    else:
        key_rig(bear, fire.data, cam)

    res = tuple(a.res) if a.res else ((400, 225) if a.preview else (640, 360))
    bpy.context.scene.render.resolution_percentage = 100
    samples = a.samples if a.samples is not None else (24 if a.preview else 48)
    B.setup_render(samples, res)

    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)
    tag = a.tag or ("preview" if a.preview else ("final" if a.final else "test"))
    bpy.context.scene.render.filepath = os.path.join(out_dir, f"walk_{tag.rstrip('_')}_")
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.frame_step = a.step
    if a.frames:
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = a.frames

    blend = os.path.join(out_dir, "bear_walk.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("blend:", blend, "frames", bpy.context.scene.frame_start, "-", bpy.context.scene.frame_end,
          "step", a.step, "samples", samples, "res", res, flush=True)

    bpy.ops.render.render(animation=True)
    print("done")


if __name__ == "__main__":
    main()
