#!/usr/bin/env python3
"""Resolve a working Kaggle credential out of the repository secrets —
or explain, in committed evidence, exactly why none of them works.

The repo carries its Kaggle credential in the secret `COMPALI`. A Kaggle
credential can legitimately be any of:

  * a `KGAT_...` access token          -> KAGGLE_API_TOKEN
  * a legacy `<user>:<hex key>` pair   -> ~/.kaggle/kaggle.json
  * a `{"username":..,"key":..}` blob  -> same
  * a bare key (no user)               -> needs the username guessed

Every plausible shape is tried, and each attempt is judged by *Kaggle's own SDK*
(`KaggleApi.authenticate()` resolves the handle from a token introspect), so an
account that simply has no kernels yet is not mistaken for a bad credential.

Writes public/demo/gpu/cred-report.json: which secret *names* exist, each
slot's shape, and per attempt the verdict plus Kaggle's error text with secret
values redacted. Then prints a one-line summary the workflow puts in the
commit message, so the diagnosis survives even if the push loses a race.
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
    ("KAGGLE_API_TOKEN", ""),
    ("KAGGLE_KEY", ""),
    ("KAGGLE_API_KEY", ""),
    ("MONARCH", ""),
    ("KAGGLE_JSON", ""),
    ("KAGGLE", ""),
]

REPORT = pathlib.Path(os.environ.get("CRED_REPORT", "public/demo/gpu/cred-report.json"))

PROBE = r"""
import json, sys
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except Exception as exc:
    print("FAIL:import:" + type(exc).__name__ + ":" + str(exc)[:200]); sys.exit(0)
try:
    a = KaggleApi(); a.authenticate()
except SystemExit:
    print("FAIL:authenticate-exit"); sys.exit(0)
except Exception as exc:
    print("FAIL:" + type(exc).__name__ + ":" + str(exc)[:240]); sys.exit(0)
vals = getattr(a, "config_values", {}) or {}
print("HANDLE:" + str(vals.get("username") or ""))
print("METHOD:" + str(vals.get("auth_method") or ""))
"""


def parse(raw: str) -> dict:
    raw = raw.strip()
    out = {"username": "", "key": "", "token": "", "shape": ""}
    if raw.startswith("{"):
        try:
            d = json.loads(raw)
            out["username"] = str(d.get("username") or "").strip()
            k = str(d.get("key") or d.get("token") or "").strip()
            if k.startswith("KGAT_"):
                out["token"], out["shape"] = k, "json+access-token"
            else:
                out["key"], out["shape"] = k, "json+key"
            return out
        except Exception:
            pass
    if raw.startswith("KGAT_"):
        out["token"], out["shape"] = raw, "access-token"
        return out
    if ":" in raw:
        left, right = raw.split(":", 1)
        if re.fullmatch(r"[A-Za-z0-9_.-]{2,40}", left.strip()) and len(right.strip()) >= 8:
            out["username"], out["key"] = left.strip(), right.strip()
            out["shape"] = "user:key"
            return out
    out["key"], out["shape"] = raw, "bare-key"
    return out


def redact(text: str, secrets: list[str]) -> str:
    for s in secrets:
        if s and len(s) >= 6:
            text = text.replace(s, "<secret>")
    return text.strip()[-400:]


def run(cmd: list[str], env: dict, secrets: list[str], timeout: int = 90) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)
    except Exception as exc:  # pragma: no cover
        return 99, f"{type(exc).__name__}: {exc}"
    return r.returncode, redact((r.stdout or "") + (r.stderr or ""), secrets)


def attempt(shape: str, username: str, key: str, token: str, secrets: list[str]) -> dict:
    env = {k: v for k, v in os.environ.items()
           if k not in ("KAGGLE_KEY", "KAGGLE_API_TOKEN", "KAGGLE_USERNAME")}
    cfg_dir = pathlib.Path(os.environ.get("HOME", "/tmp")) / ".kaggle"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    for p in (cfg_dir / "access_token", cfg_dir / "kaggle.json"):
        p.unlink(missing_ok=True)

    if token:
        env["KAGGLE_API_TOKEN"] = token
    else:
        env["KAGGLE_USERNAME"] = username or "placeholder"
        env["KAGGLE_KEY"] = key

    code, text = run([sys.executable, "-c", PROBE], env, secrets)
    handle, method, failure = "", "", ""
    for line in text.splitlines():
        if line.startswith("HANDLE:"):
            handle = line[7:].strip()
        elif line.startswith("METHOD:"):
            method = line[7:].strip()
        elif line.startswith("FAIL:"):
            failure = line[5:].strip()

    row = {"shape": shape, "authenticated": bool(handle and not failure),
           "handle": handle, "auth_method": method, "error": failure}
    if row["authenticated"]:
        rc, out = run(["kaggle", "kernels", "list", "--mine", "--page-size", "3", "-v"],
                      env, secrets)
        row["kernels_list_rc"] = rc
        row["kernels_list_head"] = out.splitlines()[0][:160] if out else ""
    return row


def main() -> int:
    secrets: list[str] = []
    rows: list[dict] = []
    chosen: dict | None = None

    rows_net = {}
    try:
        import urllib.request
        with urllib.request.urlopen(
                "https://www.kaggle.com/api/v1/datasets/list?pageSize=1", timeout=30) as r:
            rows_net = {"reachable": True, "detail": f"HTTP {r.status}"}
    except Exception as exc:
        rows_net = {"reachable": False, "detail": f"{type(exc).__name__}: {exc}"[:200]}
    print(f"::notice::kaggle.com reachable={rows_net['reachable']} {rows_net['detail']}",
          flush=True)

    for slot, hint in SLOTS:
        raw = (os.environ.get(slot) or "").strip()
        if not raw:
            rows.append({"slot": slot, "present": False})
            continue
        secrets.append(raw)
        for line in raw.splitlines():
            if line.strip():
                print(f"::add-mask::{line.strip()}", flush=True)

        p = parse(raw)
        cands: list[tuple[str, str, str, str]] = []
        if p["token"]:
            cands.append(("access-token", "", "", p["token"]))
        if p["key"]:
            cands.append(("key" + (f"@{p['username']}" if p["username"] else ""),
                          p["username"] or hint, p["key"], ""))
            if p["username"] and hint and hint != p["username"]:
                cands.append(f"key@{hint}", hint, p["key"], "")

        tried = []
        for shape, user, key, token in cands:
            row = attempt(shape, user, key, token, secrets)
            tried.append(row)
            print(f"::notice::slot {slot} [{shape}] authenticated={row['authenticated']} "
                  f"handle={row['handle'] or '-'} err={row['error'] or '-'}", flush=True)
            if row["authenticated"]:
                chosen = {"slot": slot, "shape": shape, "handle": row["handle"] or user,
                          "key": key, "token": token, "auth_method": row["auth_method"]}
                break

        rows.append({
            "slot": slot,
            "present": True,
            "chars": len(raw),
            "shape": p["shape"],
            "verdict": "authenticated" if chosen and chosen["slot"] == slot else "not_authenticated",
            "tried": tried,
        })
        if chosen:
            break

    if chosen:
        cfg_dir = pathlib.Path(os.environ.get("HOME", "/tmp")) / ".kaggle"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        if chosen["token"]:
            (cfg_dir / "access_token").write_text(chosen["token"] + "\n")
            os.chmod(cfg_dir / "access_token", 0o600)
            (cfg_dir / "kaggle.json").write_text(
                json.dumps({"username": chosen["handle"] or "unknown",
                            "key": chosen["token"]}))
        else:
            (cfg_dir / "kaggle.json").write_text(
                json.dumps({"username": chosen["handle"], "key": chosen["key"]}))
        os.chmod(cfg_dir / "kaggle.json", 0o600)
        gh_env = os.environ.get("GITHUB_ENV")
        if gh_env:
            with open(gh_env, "a") as fh:
                fh.write(f"KAGGLE_USERNAME={chosen['handle']}\n")
                fh.write(f"KAGGLE_CRED_SHAPE={chosen['shape']}\n")
                if chosen["token"]:
                    fh.write(f"KAGGLE_API_TOKEN={chosen['token']}\n")
                else:
                    fh.write(f"KAGGLE_KEY={chosen['key']}\n")
        print(f"::notice::using {chosen['slot']} [{chosen['shape']}] as {chosen['handle']}",
              flush=True)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "network": rows_net,
        "slots_present": [r["slot"] for r in rows if r["present"]],
        "slots_absent": [r["slot"] for r in rows if not r["present"]],
        "attempts": rows,
        "chosen": ({k: chosen[k] for k in ("slot", "shape", "handle", "auth_method")}
                   if chosen else None),
    }, indent=1) + "\n")

    summary_bits = []
    for r in rows:
        if not r["present"]:
            continue
        if r["verdict"] == "authenticated":
            tried = (r.get("tried") or [{}])[0]
            summary_bits.append(f"{r['slot']}:{r['shape']}:ok:{tried.get('handle', '')}")
        else:
            errs = "; ".join((t.get("error") or "no handle")[:80] for t in (r.get("tried") or []))
            summary_bits.append(f"{r['slot']}:{r['shape']}:rejected:{errs}")
    summary = " | ".join(summary_bits) or "no credential slots present"
    print(f"::notice::CRED_SUMMARY {summary} | net={'up' if rows_net['reachable'] else 'down'}",
          flush=True)

    if not chosen:
        print("::error::No Kaggle secret in this repository authenticated; "
              "public/demo/gpu/cred-report.json carries each attempt's verdict.", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
