# Blender, locally, in this repo

The vendored `tools/blender-skills/` pack (94 skills, MIT, upstream `arjun988/blender-skills`
@ `904f095`) assumes **Blender + a live MCP server on your desktop**. That assumption is
wrong for this environment, in one specific way, so it was fixed rather than copied:

| upstream assumption | what is true here | what we did |
|---|---|---|
| Blender runs as a GUI app, driven over MCP on `localhost:9876` | no GUI, no display, no root, no Blender install | ran Blender as the **`bpy` Python module** (4.2.0), headless |
| `uvx blender-mcp` provides the tools | MCP would need a GUI Blender on the other end | replaced by a repo-local, scriptable entry point (`blender_env.py`) |
| imports work on a normal desktop | `import bpy` dies on missing `libXrender.so.1`, `libGL.so.1`, … | stub libraries built from `nm` output of `bpy` itself |

The skill *content* (prompt guidance) was left as upstream wrote it. Only the execution
claim was corrected, because "MCP executes directly in Blender" is not true here.

## What is installed

- `bpy` 4.2.0 (PyPI wheel, ~520 MB unpacked), `--break-system-packages --no-deps`.
- `scipy`, `scikit-image` (topology / texture work), `trimesh` 5.2.1 (glTF in and out).
- `tools/blender_local/x11_shim/` — 147 X11/GLX/core-GL stubs + 21 `xkb*` stubs under
  the `V_0.5.0` version tag, built with `gcc` from a scan of bpy's own symbols.

## Verified here

```
$ python3 tools/blender_local/blender_env.py --probe
bpy         : OK — Blender 4.2.0
```

- Cycles **CPU** renders: 320×180 sphere test, 16 samples, 0.96 s. No GPU is present.
- `research/viral_og_v21/film3d_blender/shots/bear_shot3.py` builds a cave bear from
  code (13.9k faces after voxel remesh + decimate), a displaced cave floor and wall, a
  fire with a warm light, a cool mouth fill, a 42 mm camera with depth of field, AgX
  grade, and world volumetrics — then renders stills.
- Cost measured at 640×360: **~60 s/frame at 48 samples** on 2 cores (denoised).
  A 10 s shot at 24 fps is therefore ~4 h. This is the honest budget for this box.

## What the shim is **not**

It is not X11 and not OpenGL. It binds every symbol the loader asks for and returns
0/NULL. Consequences:

- the **GUI cannot run** through it (no window, no viewport, no `bpy.ops` that needs one);
- **EEVEE will not render** (it needs a real GL context) — use Cycles CPU;
- any add-on that opens a window or queries GL state will misbehave.

Headless Cycles does not touch those paths, which is why the renders above are correct.

## How to run

```bash
# 1. probe / install check
python3 tools/blender_local/blender_env.py --probe

# 2. rebuild the stubs after a bpy upgrade
tools/blender_local/x11_shim/build_x11_shim.sh

# 3. render the bear shot stills
cd research/viral_og_v21/film3d_blender
LD_LIBRARY_PATH=$PWD/../../tools/blender_local/x11_shim \
  python3 shots/bear_shot3.py --stills --samples 48 --res 640 360
```

`.vendored/`, `x11_shim/*.so*` and shot `out/` are gitignored: they are machine-local
build products, not source.

## Known gaps

- No GPU: Cycles is CPU-only, so sample counts stay low and denoising does the rest.
- Rigging/animation is scripted (`pose_bone` / keyframes), not authored in an editor —
  no weight-paint iteration loop exists here.
- The bear still lacks a face (no eye geometry, no mouth line): the head is a form, not
  a character. Next pass adds eyes, a lip line and a nose pad as separate materials.
