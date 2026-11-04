#!/usr/bin/env python3
<<<<<<< HEAD
"""Resolve a working Kaggle credential out of the repository secrets.

The repo carries the token in a secret named `COMPALI`; older workflows also
carry KAGGLE_KEY / KAGGLE_API_TOKEN / MONARCH. Any of them may be either a
`user:key` pair, a raw `KGAT_...` token, or a `{"username":..,"key":..}` blob,
so every form is accepted, then *probed* against the Kaggle API before use —
a slot that does not authenticate is skipped instead of failing the job later.

Writes ~/.kaggle/kaggle.json (0600) and appends KAGGLE_USERNAME / KAGGLE_KEY /
KAGGLE_API_TOKEN to $GITHUB_ENV. Prints only the slot name and the handle.
=======
"""Resolve a working Kaggle credential out of the repository secrets —
or explain, in committed evidence, exactly why none of them works.

The repo carries its Kaggle credential in the secret `COMPALI`. A Kaggle
credential can legitimately be any of:

  * a `KGAT_...` access token          -> goes in KAGGLE_API_TOKEN
  * a legacy `<user>:<hex key>` pair   -> goes in ~/.kaggle/kaggle.json
  * a `{"username":..,"key":..}` blob  -> same
  * a bare key (no user)               -> needs the username guessed

So every plausible shape is tried against the live API, and the *error text*
of each attempt is recorded. Kaggle rate-limits and expires tokens, so a
failure here must say which of those it is — not just "auth failed".

Never writes a secret value to disk outside ~/.kaggle (0600) or to the report.
>>>>>>> b328a01 (fix(gpu): try every Kaggle credential shape and commit the real verdict)
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

<<<<<<< HEAD
=======
# secret name -> username hint (used only when the secret itself carries none)
>>>>>>> b328a01 (fix(gpu): try every Kaggle credential shape and commit the real verdict)
SLOTS = [
    ("COMPALI", "compali"),
    ("KAGGLE_KEY", ""),
    ("KAGGLE_API_TOKEN", ""),
    ("KAGGLE_API_KEY", ""),
    ("MONARCH", ""),
    ("KAGGLE_JSON", ""),
    ("KAGGLE", ""),
<<<<<<< HEAD
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


def write_report(rows: list[dict], chosen: dict | None) -> None:
    """Evidence, not vibes: which secret *names* exist and why each was rejected.

    Only names, booleans and the CLI's own error text — never a secret value.
    """
    out = pathlib.Path(os.environ.get("CRED_REPORT", "public/demo/gpu/cred-report.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "slots_present": [r["slot"] for r in rows if r["present"]],
        "slots_absent": [r["slot"] for r in rows if not r["present"]],
        "attempts": rows,
        "chosen": chosen,
    }, indent=1) + "\n")


def main() -> int:
    chosen = None
    rows: list[dict] = []
=======
    ("KAGGLE_USERNAME", ""),
]

REPORT = pathlib.Path(os.environ.get("CRED_REPORT", "public/demo/gpu/cred-report.json"))


def parse(raw: str) -> dict:
    """Classify a secret into its possible credential shapes."""
    raw = raw.strip()
    out = {"username": "", "key": "", "token": "", "shapes": []}
    if raw.startswith("{"):
        try:
            d = json.loads(raw)
            out["username"] = str(d.get("username") or "").strip()
            k = str(d.get("key") or d.get("token") or "").strip()
            if k.startswith("KGAT_"):
                out["token"] = k
            else:
                out["key"] = k
            out["shapes"].append("json")
            return out
        except Exception:
            pass
    if raw.startswith("KGAT_"):
        out["token"] = raw
        out["shapes"].append("access-token")
        return out
    if ":" in raw:
        left, right = raw.split(":", 1)
        if re.fullmatch(r"[A-Za-z0-9_.-]{2,40}", left.strip()) and len(right.strip()) >= 8:
            out["username"], out["key"] = left.strip(), right.strip()
            out["shapes"].append("user:key")
            return out
    out["key"] = raw
    out["shapes"].append("bare-key")
    return out


def cli(args: list[str], env: dict) -> tuple[int, str]:
    try:
        r = subprocess.run(["kaggle", *args], capture_output=True, text=True,
                           env=env, timeout=60)
    except Exception as exc:  # pragma: no cover
        return 99, f"{type(exc).__name__}: {exc}"
    text = (r.stdout or "") + (r.stderr or "")
    return r.returncode, text.strip()


def redact(text: str, secrets: list[str]) -> str:
    for s in secrets:
        if s:
            text = text.replace(s, "<secret>")
    return text[-600:]


def attempt(name: str, username: str, key: str, token: str, secrets: list[str]) -> dict:
    """Try one auth shape. Returns a report row with the CLI's own verdict."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("KAGGLE_KEY", "KAGGLE_API_TOKEN", "KAGGLE_USERNAME")}
    home = pathlib.Path(os.environ.get("HOME", "/tmp"))
    cfg_dir = home / ".kaggle"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    tok_file = cfg_dir / "access_token"
    json_file = cfg_dir / "kaggle.json"
    for p in (tok_file, json_file):
        p.unlink(missing_ok=True)

    if token:
        env["KAGGLE_API_TOKEN"] = token
        if username:
            env["KAGGLE_USERNAME"] = username
    else:
        env["KAGGLE_USERNAME"] = username or "placeholder"
        env["KAGGLE_KEY"] = key

    code, text = cli(["kernels", "list", "--mine", "--page-size", "3", "-v"], env)
    handle = ""
    for line in text.splitlines()[1:]:
        ref = line.split(",", 1)[0].strip()
        if "/" in ref and not ref.lower().startswith("ref"):
            handle = ref.split("/", 1)[0].strip()
            break
    return {
        "attempt": name,
        "rc": code,
        "authenticated": bool(handle),
        "handle": handle,
        "error": "" if handle else redact(text, secrets),
    }


def main() -> int:
    rows: list[dict] = []
    secrets: list[str] = []
    chosen: dict | None = None

    # 0. is kaggle.com even reachable from this runner?
    reach_code, reach_text = 0, ""
    try:
        import urllib.request
        with urllib.request.urlopen("https://www.kaggle.com/api/v1/datasets/list?pageSize=1",
                                    timeout=30) as r:
            reach_text = f"HTTP {r.status}"
    except Exception as exc:
        reach_code, reach_text = 1, f"{type(exc).__name__}: {exc}"
    reach = {"reachable": reach_code == 0, "detail": reach_text[:200]}

>>>>>>> b328a01 (fix(gpu): try every Kaggle credential shape and commit the real verdict)
    for slot, hint in SLOTS:
        raw = (os.environ.get(slot) or "").strip()
        if not raw:
            rows.append({"slot": slot, "present": False})
            continue
<<<<<<< HEAD
        for line in raw.splitlines():
            if line.strip():
                print(f"::add-mask::{line.strip()}", flush=True)
        user, key, token = parse(raw)
        if not key and not token:
            print(f"::warning::slot {slot} is not a key/token, skipping", flush=True)
            rows.append({"slot": slot, "present": True, "verdict": "unparseable"})
            continue
        handle = probe(user or hint, key, token)
        print(f"::notice::slot {slot} -> {handle or 'not authenticated'}", flush=True)
        rows.append({
            "slot": slot, "present": True, "chars": len(raw),
            "shape": ("json" if raw.startswith("{") else
                      "token" if token else "user:key" if user else "key"),
            "verdict": handle or "not_authenticated",
        })
        if handle:
            chosen = {"slot": slot, "handle": handle, "token_mode": bool(token)}
            break

    write_report(rows, chosen)

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
=======
        secrets.append(raw)
        for line in raw.splitlines():
            if line.strip():
                print(f"::add-mask::{line.strip()}", flush=True)

        p = parse(raw)
        shapes = "+".join(p["shapes"])
        if not p["key"] and not p["token"]:
            rows.append({"slot": slot, "present": True, "chars": len(raw),
                         "shape": "unparseable", "verdict": "not_authenticated"})
            continue

        # candidate auth shapes for this slot, best first
        cands = []
        if p["token"]:
            cands.append(("token-env", p["username"] or hint, "", p["token"]))
            if hint:
                cands.append(("token-env+hint", hint, "", p["token"]))
        if p["key"]:
            if p["username"]:
                cands.append(("user:key", p["username"], p["key"], ""))
            for u in filter(None, [hint]):
                cands.append((f"key+hint:{u}", u, p["key"], ""))

        tried = []
        for name, user, key, token in cands:
            row = attempt(name, user, key, token, secrets)
            tried.append(row)
            print(f"::notice::slot {slot} [{name}] rc={row['rc']} "
                  f"auth={row['authenticated']}", flush=True)
            if row["authenticated"]:
                chosen = {"slot": slot, "shape": name, "handle": row["handle"],
                          "username": row["handle"], "key": key, "token": token}
                break

        rows.append({
            "slot": slot,
            "present": True,
            "chars": len(raw),
            "shape": shapes,
            "is_access_token": bool(p["token"]),
            "verdict": "authenticated" if chosen and chosen["slot"] == slot else "not_authenticated",
            "tried": tried,
        })
        if chosen:
            break

    # persist the winning credential
    if chosen:
        cfg_dir = pathlib.Path(os.environ.get("HOME", "/tmp")) / ".kaggle"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        if chosen["token"]:
            (cfg_dir / "access_token").write_text(chosen["token"] + "\n")
            os.chmod(cfg_dir / "access_token", 0o600)
            (cfg_dir / "kaggle.json").write_text(
                json.dumps({"username": chosen["username"], "key": chosen["token"]}))
        else:
            (cfg_dir / "kaggle.json").write_text(
                json.dumps({"username": chosen["username"], "key": chosen["key"]}))
        os.chmod(cfg_dir / "kaggle.json", 0o600)
        gh_env = os.environ.get("GITHUB_ENV")
        if gh_env:
            with open(gh_env, "a") as fh:
                fh.write(f"KAGGLE_USERNAME={chosen['username']}\n")
                if chosen["token"]:
                    fh.write(f"KAGGLE_API_TOKEN={chosen['token']}\n")
                else:
                    fh.write(f"KAGGLE_KEY={chosen['key']}\n")
        print(f"::notice::using {chosen['slot']} via {chosen['shape']} as "
              f"{chosen['username']}", flush=True)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "network": reach,
        "slots_present": [r["slot"] for r in rows if r["present"]],
        "slots_absent": [r["slot"] for r in rows if not r["present"]],
        "attempts": rows,
        "chosen": ({k: chosen[k] for k in ("slot", "shape", "handle")} if chosen else None),
    }, indent=1) + "\n")

    if not chosen:
        print("::error::No Kaggle secret in this repository authenticated. "
              "The committed report says exactly what each one returned.", flush=True)
        return 1
>>>>>>> b328a01 (fix(gpu): try every Kaggle credential shape and commit the real verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
