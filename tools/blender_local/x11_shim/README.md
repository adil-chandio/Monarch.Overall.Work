# X11 shim for `bpy`

`bpy` links against X11 even when Blender renders without a display, so importing it
fails on a slim container with:

    ImportError: libXrender.so.1: cannot open shared object file

`build_x11_shim.sh` compiles minimal stand-ins for the four entry points Blender only
reaches when a *window* exists. Headless rendering (Cycles / EEVEE offline, no GUI)
never calls them.

**Measured here:** see `docs/BLENDER_LOCAL.md` in the repo root of this tool for what
actually worked in this sandbox. Do not treat the shim as a general-purpose X11.
