#!/usr/bin/env python3
"""Resolve a working Kaggle credential out of the repository secrets.

The repo carries the token in a secret named `COMPALI`; older workflows also
carry KAGGLE_KEY / KAGGLE_API_TOKEN / MONARCH. Any of them may be either a
`user:key` pair, a raw `KGAT_...` token, or a `{"username":..,"key":..}` blob,
so every form is accepted, then *probed* against the Kaggle API before use —
a slot that does not authenticate is skipped instead of failing the job later.

Writes ~/.kaggle/kaggle.json (0600) and appends KAGGLE_USERNAME / KAGGLE_KEY /
KAGGLE_API_TOKEN to $GITHUB_ENV. Prints only the slot name and the handle.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

SLOTS = [
    ("COMPALI", "compali"),
    ("KAGGLE_KEY", ""),
    ("KAGGLE_API_TOKEN", ""),
    ("KAGGLE_API_KEY", ""),
    ("MONARCH", ""),
    ("KAGGLE_JSON", ""),
    ("KAGGLE", ""),
]


def parse(raw: str) -> tuple[str, str, str]:
    """-> (username_hint, key, token)"""
    raw = raw.strip()
    user, key, token = "", raw, ""
    if raw.startswith("{"):
        try:
            d = json.loads(raw)
            user = str(d.get("username") or "").strip()
            key = str(d.get("key") or d.get("token") or "").strip()
        except Exception:
            pass
    elif ":" in raw and not raw.startswith("KGAT_"):
        left, right = raw.split(":", 1)
        if re.fullmatch(r"[A-Za-z0-9_.-]{2,40}", left.strip()):
            user, key = left.strip(), right.strip()
    if key.startswith("KGAT_"):
        token, key = key, ""
    return user, key, token


def probe(user: str, key: str, token: str) -> str:
    """Return the authenticated handle, or ''."""
    env = dict(os.environ)
    env["KAGGLE_USERNAME"] = user or "placeholder"
    if token:
        env["KAGGLE_API_TOKEN"] = token
        env.pop("KAGGLE_KEY", None)
    else:
        env["KAGGLE_KEY"] = key
        env.pop("KAGGLE_API_TOKEN", None)
    try:
        r = subprocess.run(["kaggle", "kernels", "list", "--mine", "--page-size", "5", "-v"],
                           capture_output=True, text=True, env=env, timeout=45)
    except Exception as exc:  # pragma: no cover
        print(f"::warning::probe error: {exc}", flush=True)
        return ""
    for line in r.stdout.splitlines()[1:]:
        ref = line.split(",", 1)[0].strip()
        if "/" in ref and not ref.lower().startswith("ref"):
            return ref.split("/", 1)[0].strip()
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()
        print(f"::warning::slot rejected: {tail[-1] if tail else 'no output'}", flush=True)
    return ""


def main() -> int:
    chosen = None
    for slot, hint in SLOTS:
        raw = (os.environ.get(slot) or "").strip()
        if not raw:
            continue
        for line in raw.splitlines():
            if line.strip():
                print(f"::add-mask::{line.strip()}", flush=True)
        user, key, token = parse(raw)
        if not key and not token:
            print(f"::warning::slot {slot} is not a key/token, skipping", flush=True)
            continue
        handle = probe(user or hint, key, token)
        print(f"::notice::slot {slot} -> {handle or 'not authenticated'}", flush=True)
        if handle:
            chosen = (slot, handle, key, token)
            break

    if not chosen:
        print("::error::No Kaggle secret in this repository authenticated. "
              "Expected a `user:key` pair or a `KGAT_...` token in COMPALI.", flush=True)
        return 1

    slot, user, key, token = chosen
    kdir = pathlib.Path.home() / ".kaggle"
    kdir.mkdir(parents=True, exist_ok=True)
    cfg = kdir / "kaggle.json"
    if token:
        # the CLI reads the token from the env, not from the json
        cfg.write_text(json.dumps({"username": user, "key": token}))
    else:
        cfg.write_text(json.dumps({"username": user, "key": key}))
    os.chmod(cfg, 0o600)

    env_file = os.environ.get("GITHUB_ENV")
    if env_file:
        with open(env_file, "a") as fh:
            fh.write(f"KAGGLE_USERNAME={user}\n")
            if token:
                fh.write(f"KAGGLE_API_TOKEN={token}\n")
            else:
                fh.write(f"KAGGLE_KEY={key}\n")

    print(f"::notice::using slot {slot} as {user} (token_mode={bool(token)})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
