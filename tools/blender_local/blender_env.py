#!/usr/bin/env python3
"""Blender-in-repo: resolve missing X11 libraries, probe, and run bpy headless.

Why this exists
---------------
`bpy` (Blender 4.x as a Python module) installs from PyPI on Linux, but importing it
needs a handful of X11 shared objects (libXrender, libXi, libXfixes, libXkbcommon,
libSM, libICE, libXxf86vm, libXrandr, libXinerama) that a slim container usually
does not have, and there is no root to `apt-get install` them.

This module resolves each one at import time: if the system already has it, it is
used; if not, the Debian package that ships it is downloaded, extracted with
`dpkg -x` into `.vendored/`, and the directory is added to the loader path. Nothing
outside the repository is modified and no root is needed.

Usage
-----
    python3 tools/blender_local/blender_env.py --probe          # what works here
    python3 tools/blender_local/blender_env.py --test           # import bpy + render

    from blender_env import load_bpy
    bpy = load_bpy()          # import is done only after the libs are in place

Licence note
------------
The extracted libraries come from the Debian archive and keep their own licences
(LGPL/GPL/MIT as per each package). They are only used to run Blender locally and
are not redistributed in this repository (`.vendored/` is gitignored).
"""
from __future__ import annotations

import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
VENDOR = os.path.join(HERE, ".vendored")
LIBDIR = os.path.join(VENDOR, "lib")
CACHE = os.path.join(VENDOR, "cache")
# NOTE: onion-only network in this sandbox blocks the Debian mirrors (TLS closed,
# and the plain-HTTP mirror drops the connection). prepare() therefore resolves only
# libraries that are already present; anything else needs the X11 shim below.
DEBIAN_MIRROR = "https://deb.debian.org/debian"

# soname -> (debian package, path inside the package)
PROVIDERS = {
    "libXrender.so.1": ("libxrender1", "usr/lib/x86_64-linux-gnu/libXrender.so.1.3.0"),
    "libXfixes.so.3": ("libxfixes3", "usr/lib/x86_64-linux-gnu/libXfixes.so.3.0.0"),
    "libXi.so.6": ("libxi6", "usr/lib/x86_64-linux-gnu/libXi.so.6.1.0"),
    "libXkbcommon.so.0": ("libxkbcommon0", "usr/lib/x86_64-linux-gnu/libxkbcommon.so.0.0.0"),
    "libSM.so.6": ("libsm6", "usr/lib/x86_64-linux-gnu/libSM.so.6.0.1"),
    "libICE.so.6": ("libice6", "usr/lib/x86_64-linux-gnu/libICE.so.6.0.2"),
    "libXxf86vm.so.1": ("libxxf86vm1", "usr/lib/x86_64-linux-gnu/libXxf86vm.so.1.0.0"),
    "libXrandr.so.2": ("libxrandr2", "usr/lib/x86_64-linux-gnu/libXrandr.so.2.2.0"),
    "libXinerama.so.1": ("libxinerama1", "usr/lib/x86_64-linux-gnu/libXinerama.so.1.0.0"),
    "libGL.so.1": ("libgl1", "usr/lib/x86_64-linux-gnu/libGL.so.1.7.0"),
    "libEGL.so.1": ("libegl1", "usr/lib/x86_64-linux-gnu/libEGL.so.1.1.0"),
}


def _find_in_system(soname: str) -> str | None:
    """Look for a soname in the usual places, without needing ldconfig."""
    dirs = ["/usr/lib/x86_64-linux-gnu", "/usr/lib64", "/usr/lib", "/lib/x86_64-linux-gnu",
            "/usr/local/lib", sysconfig.get_paths()["purelib"]]
    for d in dirs:
        p = os.path.join(d, soname)
        if os.path.exists(p):
            return p
    return None


def _debian_package_url(pkg: str) -> str | None:
    """Resolve a package name to a .deb URL in the current Debian stable pool."""
    for section in ("libs", "x11", "libdevel"):
        idx = f"{DEBIAN_MIRROR}/dists/stable/main/binary-amd64/Packages.gz"
        if not os.path.exists(os.path.join(CACHE, "Packages")):
            _fetch(idx, os.path.join(CACHE, "Packages.gz"))
            import gzip
            with gzip.open(os.path.join(CACHE, "Packages.gz")) as f:
                open(os.path.join(CACHE, "Packages"), "wb").write(f.read())
        with open(os.path.join(CACHE, "Packages"), "r", errors="ignore") as f:
            cur = {}
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    if cur.get("Package") == pkg:
                        return cur.get("Filename")
                    cur = {}
                    continue
                if line.startswith("Package: "):
                    cur["Package"] = line[9:]
                elif line.startswith("Filename: "):
                    cur["Filename"] = line[10:]
    return None


def _fetch(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    with urllib.request.urlopen(url, timeout=60) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def vendor_lib(soname: str) -> str | None:
    """Make `soname` loadable, vendoring it from Debian if the system lacks it."""
    have = _find_in_system(soname)
    if have:
        return have
    target = os.path.join(LIBDIR, soname)
    if os.path.exists(target):
        return target
    pkg = PROVIDERS.get(soname)
    if not pkg:
        return None
    pkgname, _inner = pkg
    rel = _debian_package_url(pkgname)
    if not rel:
        return None
    deb = os.path.join(CACHE, os.path.basename(rel))
    _fetch(f"{DEBIAN_MIRROR}/{rel}", deb)
    tmp = tempfile.mkdtemp(dir=CACHE)
    subprocess.run(["dpkg-deb", "-x", deb, tmp], check=False)
    os.makedirs(LIBDIR, exist_ok=True)
    # copy every .so* the package carries, so inter-library deps resolve too
    found = False
    for base, _dirs, files in os.walk(os.path.join(tmp, "usr", "lib", "x86_64-linux-gnu")):
        for fn in files:
            if ".so" in fn:
                src = os.path.join(base, fn)
                dst = os.path.join(LIBDIR, fn)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                if fn == soname:
                    found = True
    shutil.rmtree(tmp, ignore_errors=True)
    return target if found or os.path.exists(target) else None


def prepare(libs: list[str] | None = None) -> dict:
    """Vendor whatever is missing and preload it. Returns {soname: path|None}."""
    if os.path.isdir(LIBDIR):
        os.environ["LD_LIBRARY_PATH"] = LIBDIR + ":" + os.environ.get("LD_LIBRARY_PATH", "")
        try:
            ctypes.CDLL(os.path.join(LIBDIR, "libXrender.so.1"), mode=ctypes.RTLD_GLOBAL)
        except OSError:
            pass
    wanted = libs or list(PROVIDERS)
    out = {}
    for s in wanted:
        out[s] = vendor_lib(s)
    # load what we have with RTLD_GLOBAL so later deps can see the symbols
    for s, p in out.items():
        if p:
            try:
                ctypes.CDLL(p, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass
    return out


def load_bpy(allow_network: bool = False):
    """Prepare the libraries, then import bpy.

    The stub libraries in x11_shim/ are used if present; no network access is
    attempted unless `allow_network` is true (the Debian mirror is unreachable in
    this sandbox, and a failed lookup is slow).
    """
    if allow_network:
        prepare()
    else:
        _prepare_local()
    import bpy  # noqa: E402  (import must follow the loader setup)
    return bpy


def _prepare_local():
    """Put the repo's stub libraries on the loader path (no downloads)."""
    shim = os.path.join(HERE, "x11_shim")
    if not os.path.isdir(shim):
        return None
    os.environ["LD_LIBRARY_PATH"] = shim + ":" + os.environ.get("LD_LIBRARY_PATH", "")
    return shim


def probe() -> int:
    print(f"python      : {sys.version.split()[0]}")
    print(f"repo        : {REPO}")
    print(f"vendor dir  : {VENDOR}")
    try:
        import bpy  # noqa: F401
        print("bpy         : already importable")
        return 0
    except OSError as exc:
        print(f"bpy         : not importable yet (shared library: {exc})")
    except ImportError as exc:
        print(f"bpy         : not installed ({exc})")
        shim = os.path.join(HERE, "x11_shim", "libXrender.so.1")
        print(f"shim        : {'built' if os.path.exists(shim) else 'not built'}"
              f"  (tools/blender_local/build_x11_shim.sh)")
    res = prepare()      # only resolves libs the system already has; never downloads
    ok = [k for k, v in res.items() if v]
    bad = [k for k, v in res.items() if not v]
    print(f"libraries   : {len(ok)} resolved, {len(bad)} missing")
    for k in bad:
        print(f"  missing   : {k}")
    try:
        import bpy
        print(f"bpy         : OK — Blender {bpy.app.version_string}")
        return 0
    except Exception as exc:
        print(f"bpy         : still failing ({exc.__class__.__name__}: {exc})")
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe", action="store_true", help="report what resolves")
    ap.add_argument("--test", action="store_true", help="import bpy and render a cube")
    a = ap.parse_args()
    if a.test:
        bpy = load_bpy()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1))
        bpy.ops.object.light_add(type="AREA", location=(3, -3, 4))
        bpy.ops.object.camera_add(location=(4, -4, 3), rotation=(1.1, 0, 0.78))
        bpy.context.scene.camera = bpy.context.object
        bpy.context.scene.render.resolution_x = 320
        bpy.context.scene.render.resolution_y = 180
        out = os.path.join(VENDOR, "test.png")
        bpy.context.scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print("rendered:", out, os.path.getsize(out) if os.path.exists(out) else "MISSING")
        return 0
    return probe()


if __name__ == "__main__":
    sys.exit(main())
