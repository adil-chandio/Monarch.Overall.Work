#!/usr/bin/env python3
"""Monarch.Overall.Work continuity OS.

A dependency-free archive/import/resume tool. It preserves raw evidence, a
machine-readable state ledger, an append-only event ledger, and a validator that
CI can run. It never claims a screenshot is a transcript or a technical gate is
human approval.

Commands:
  resume                 Show the exact new-chat bootstrap and current state.
  validate               Verify schema, hashes, references, claims and inbox.
  refresh                Rebuild EVIDENCE_MANIFEST.json and coverage counts.
  render [--check]       Regenerate (or check) human-readable ledgers.
  import-chat FILE ...   Preserve a raw chat/export and normalize it.
  checkpoint ...         Append a state/event checkpoint and rerender.
  bootstrap              Print the pasteable new-chat prompt with HEAD pinned.
  channel [ID]           Print the active channel easy-resume capsule.
  recover                Fetch and fast-forward a stale checkout.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
C = ROOT / "docs/continuity"
STATE = C / "STATE.json"
COVERAGE = C / "COVERAGE.json"
SESSIONS = C / "SESSION_INDEX.json"
MANIFEST = C / "EVIDENCE_MANIFEST.json"
EVENTS = C / "EVENTS.jsonl"
DECISIONS = C / "DECISION_LOG.jsonl"
PROMPTS = C / "PROMPT_RESULT_LOG.jsonl"
EXPORTS = C / "chat_exports"
INBOX = EXPORTS / "inbox"
SOURCES = EXPORTS / "sources"
SESSIONS_DIR = C / "sessions"
EVIDENCE = C / "evidence"
CHANNELS_DIR = C / "channels"
CHANNELS_INDEX = CHANNELS_DIR / "CHANNEL_INDEX.json"

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "config/continuity.json",
    "tools/continuity.py",
    ".github/workflows/continuity-validate.yml",
    "docs/continuity/README.md",
    "docs/continuity/00_START_HERE.md",
    "docs/continuity/NEW_CHAT_PROMPT.md",
    "docs/continuity/MINDSET.md",
    "docs/continuity/WORK_LEVELS.md",
    "docs/continuity/PROBLEMS_FIXES.md",
    "docs/continuity/UPDATE_PROTOCOL.md",
    "docs/continuity/IMPORT_PROTOCOL.md",
    "docs/continuity/GAPS.md",
    "docs/continuity/STATE.json",
    "docs/continuity/COVERAGE.json",
    "docs/continuity/SESSION_INDEX.json",
    "docs/continuity/EVIDENCE_MANIFEST.json",
    "docs/continuity/EVENTS.jsonl",
    "docs/continuity/DECISION_LOG.jsonl",
    "docs/continuity/PROMPT_RESULT_LOG.jsonl",
    "docs/continuity/chat_exports/README.md",
    "docs/continuity/chat_exports/inbox/README.md",
    "docs/continuity/external/README.md",
    "docs/continuity/external/APP_SNAPSHOT.json",
    "docs/continuity/external/DRIVE_INDEX.md",
    "RECOVER.md",
    "MONARCH_CAM.md",
    "docs/continuity/channels/README.md",
    "docs/continuity/channels/CHANNEL_INDEX.json",
    "docs/continuity/channels/monarch-cam/00_START_HERE.md",
    "docs/continuity/channels/monarch-cam/CHANNEL_STATE.json",
    "docs/continuity/channels/monarch-cam/EASY_RESUME.md",
    "docs/continuity/channels/monarch-cam/NEXT_ACTION.md",
    "docs/continuity/channels/monarch-cam/PLAYBOOK.md",
    "docs/continuity/channels/monarch-cam/WORKFLOW.md",
    "docs/continuity/channels/monarch-cam/REJECTIONS.md",
    "docs/continuity/channels/monarch-cam/EVIDENCE.md",
]

GENERATED_NAMES = {
    "STATE.md", "COVERAGE.md", "SESSION_INDEX.md", "TIMELINE.md",
    "DECISION_LOG.md", "PROMPT_RESULT_LOG.md", "EVIDENCE_MANIFEST.md",
    "CHANNEL_INDEX.md",
}

EVIDENCE_LEVELS = {
    "verbatim_transcript": "Exact exported chat turns; raw bytes are authoritative.",
    "verbatim_event_log": "Exact exported hash-chained event/journal file; not a chat transcript.",
    "verbatim_source": "Raw imported transcript/export bytes before normalization.",
    "repo_evidence": "Git object, commit, branch, PR, workflow run, or checked-in repository file.",
    "connected_app_record": "Drive/Docs/Notion/Linear/Supabase/Vercel/Gmail/Dropbox record or imported text.",
    "screenshot_only": "Visible screenshot image evidence; truncated/partial and never a full transcript.",
    "session_memory": "Condensed session-memory reconstruction; lower confidence than a transcript.",
    "state_ledger": "Machine-readable state, coverage, session index or append-only JSONL ledger.",
    "operating_contract": "Human-readable continuity contract, protocol, index or session note.",
    "archive_metadata": "Generated archive metadata, hash index or integrity manifest.",
    "gap": "Known missing source; explicitly not claimed as preserved.",
}

SCAN_GLOBS = [
    "docs/continuity/evidence/screenshots/*",
    "docs/continuity/evidence/github/*",
    "docs/continuity/evidence/github/other_repo_docs/**/*",
    "docs/continuity/evidence/external/**/*",
    "docs/continuity/chat_exports/sources/**/*",
    "docs/continuity/chat_exports/README.md",
    "docs/continuity/chat_exports/inbox/README.md",
    "docs/continuity/external/*",
    "docs/continuity/channels/*",
    "docs/continuity/channels/**/*",
    "docs/continuity/sessions/*",
    "docs/continuity/*",
    "docs/MONARCH_CAM_*.md",
    "production/monarch-cam/short_ranking_raw_v5/*.json",
    "production/monarch-cam/short_ranking_raw_v5/*.md",
    "production/monarch-cam/short_ranking_raw_v5/*.py",
    "production/monarch-cam/short_ranking_raw_v5/review/*.json",
    "production/monarch-cam/short_ranking_raw_v5/review/*.txt",
    "production/monarch-cam/short_ranking_raw_v6/*.json",
    "production/monarch-cam/short_ranking_raw_v6/*.md",
    "production/monarch-cam/short_ranking_raw_v6/*.py",
    "production/monarch-cam/short_ranking_raw_v6/*.txt",
    "production/monarch-cam/short_ranking_raw_v6/review/*.json",
    "production/monarch-cam/short_ranking_raw_v6/review/*.txt",
    "production/monarch-cam/short_ranking_raw_v6/review/candidates/*.json",
    ".github/workflows/monarch-cam-short-ranking-raw-v6.yml",
    "deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V6.mp4",
    "production/monarch-cam/short_ranking_raw_v7/*.json",
    "production/monarch-cam/short_ranking_raw_v7/*.md",
    "production/monarch-cam/short_ranking_raw_v7/*.py",
    "production/monarch-cam/short_ranking_raw_v7/*.txt",
    "production/monarch-cam/short_ranking_raw_v7/review/*.json",
    "production/monarch-cam/short_ranking_raw_v7/review/*.txt",
    "production/monarch-cam/short_ranking_raw_v7/review/candidates/*.json",
    ".github/workflows/monarch-cam-short-ranking-viral-v7.yml",
    ".github/workflows/v7-audio-window-diagnostic.yml",
    "deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4",
    "RECOVER.md",
    "MONARCH_CAM.md",
    "config/continuity.json",
    "config/spaces.json",
    "config/channels.json",
    "config/repos.json",
    "tools/continuity.py",
    ".github/workflows/continuity-validate.yml",
    "AGENTS.md",
    "README.md",
    ".gitignore",
    ".gitattributes",
]

BINARY_EXTS = {".zip", ".gz", ".tgz", ".tar", ".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".wav", ".mp3", ".m4a", ".ogg", ".flac", ".blend", ".bin"}


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def read_jsonl(path: pathlib.Path):
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{n}: invalid JSON: {exc}") from exc
    return out


def append_jsonl(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=False) + "\n")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: pathlib.Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout.strip()


def repo_head() -> str:
    return git("rev-parse", "HEAD")


def commit_tree_url(sha: str) -> str:
    return f"https://github.com/adil-chandio/Monarch.Overall.Work/tree/{sha}"


def evidence_level_for(path: str) -> str:
    p = path.lower()
    if "docs/continuity/channels/" in p:
        return "operating_contract"
    if p.startswith(("docs/monarch_cam_", "production/monarch-cam/")):
        return "repo_evidence"
    if p in {"recover.md", "monarch_cam.md"}:
        return "operating_contract"
    if p == "config/channels.json":
        return "repo_evidence"
    if "evidence/screenshots/" in p and p.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
        return "screenshot_only"
    if "chat_exports/sources/" in p:
        return "verbatim_source"
    if "evidence/github/" in p:
        return "repo_evidence"
    if "evidence/external/" in p:
        return "connected_app_record"
    if p.endswith(("state.json", "coverage.json", "session_index.json")) or p.endswith(".jsonl"):
        return "state_ledger"
    if p.endswith(".md"):
        return "operating_contract"
    return "archive_metadata"


def manifest_paths():
    seen = set()
    for pattern in SCAN_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file():
                continue
            rp = rel(path)
            if path.name in GENERATED_NAMES or rp == "docs/continuity/EVIDENCE_MANIFEST.json":
                continue
            if rp.startswith("docs/continuity/chat_exports/inbox/") and path.name not in {"README.md", ".gitkeep"}:
                continue
            if rp in seen:
                continue
            seen.add(rp)
            yield path, rp


def build_manifest():
    files = []
    for path, rp in manifest_paths():
        files.append({
            "path": rp,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "evidence_level": evidence_level_for(rp),
        })
    files.sort(key=lambda x: x["path"])
    return {
        "schema_version": "1.0.0",
        "generated_at": utcnow(),
        "head": repo_head(),
        "note": "Hashes cover evidence, raw chat sources, ledgers and operating contracts. Generated *.md summaries are intentionally excluded to avoid circular hashes.",
        "files": files,
    }


def refresh_coverage(manifest=None):
    coverage = load_json(COVERAGE)
    sessions = load_json(SESSIONS)
    manifest = manifest or load_json(MANIFEST)
    imported = []
    for meta in sorted(SOURCES.glob("*/metadata.json")):
        imported.append(load_json(meta))
    verbatim = [m for m in imported if str(m.get("evidence_level", "")).startswith("verbatim")]
    partial = [m for m in verbatim if m.get("coverage") != "complete"]
    complete = [m for m in verbatim if m.get("coverage") == "complete"]
    coverage.setdefault("verbatim_transcripts", {})
    coverage["verbatim_transcripts"].update({
        "available": bool(verbatim),
        "imported_sessions": len(verbatim),
        "complete_sessions": len(complete),
        "partial_sessions": len(partial),
        "full_arena_export_available": bool(complete) and all("arena" in str(m.get("source", "")).lower() for m in complete),
    })
    coverage["counts"] = {
        "manifest_files": len(manifest.get("files", [])),
        "sessions_indexed": len(sessions.get("sessions", [])),
        "events": len(read_jsonl(EVENTS)),
        "decisions": len(read_jsonl(DECISIONS)),
        "prompt_results": len(read_jsonl(PROMPTS)),
        "screenshots": sum(1 for f in manifest.get("files", []) if f.get("evidence_level") == "screenshot_only" and f.get("path", "").lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"))),
        "channels_indexed": len(load_json(CHANNELS_INDEX).get("channels", [])),
        "channel_files": sum(1 for f in manifest.get("files", []) if "docs/continuity/channels/" in f.get("path", "")),
    }
    dump_json(COVERAGE, coverage)
    return coverage


def refresh():
    # COVERAGE.json is itself hashed by the manifest. Build once to compute counts,
    # update COVERAGE.json, then rebuild so the final hash covers the final bytes.
    provisional = build_manifest()
    coverage = refresh_coverage(provisional)
    manifest = build_manifest()
    dump_json(MANIFEST, manifest)
    print(f"Refreshed manifest: {len(manifest['files'])} files, head {manifest['head']}")
    print(f"Verbatim transcript sessions: {coverage['verbatim_transcripts']['imported_sessions']} "
          f"(complete={coverage['verbatim_transcripts']['complete_sessions']}, partial={coverage['verbatim_transcripts']['partial_sessions']})")


def md_json(obj) -> str:
    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n```\n"


def render_outputs():
    state = load_json(STATE)
    coverage = load_json(COVERAGE)
    sessions = load_json(SESSIONS)
    manifest = load_json(MANIFEST)
    events = read_jsonl(EVENTS)
    decisions = read_jsonl(DECISIONS)
    prompts = read_jsonl(PROMPTS)
    channels = load_json(CHANNELS_INDEX)

    state_md = [
        "# Current state",
        "",
        f"- Repo: `{state.get('repo')}`",
        f"- Branch: `{state.get('branch')}`",
        f"- Head at capture: `{state.get('head_at_capture')}`",
        f"- Captured: `{state.get('captured_at')}`",
        f"- Updated: `{state.get('updated_at')}`",
        f"- Last event: `{state.get('last_event_id')}`",
        "",
        "## Active channel", md_json({"active_channel": state.get("active_channel"), "channel_context": state.get("channel_context", {})}),
        "## Active task", md_json(state.get("active_task", {})),
        "## Infrastructure task", md_json(state.get("infrastructure_task", {})),
        "## Parallel video task", md_json(state.get("parallel_task", {})),
        "## Continuation requirements", md_json(state.get("continuation_requirements", [])),
        "## Latest mindset", md_json(state.get("latest_mindset", {})),
        "## Claims (all false unless a real acceptance record is imported)", md_json(state.get("claims", {})),
        "## Known gaps", md_json(state.get("gaps", [])),
        "## Coverage snapshot", md_json(state.get("coverage", {})),
    ]

    coverage_md = [
        "# Evidence coverage",
        "",
        "This archive is honest about evidence strength. A screenshot is never promoted to a transcript.",
        "", md_json(coverage),
        "## Evidence levels", md_json(EVIDENCE_LEVELS),
    ]

    session_lines = ["# Session index", "", f"Sessions indexed: {len(sessions.get('sessions', []))}", ""]
    for s in sessions.get("sessions", []):
        session_lines += [
            f"## {s.get('id')} — {s.get('title')}",
            "",
            f"- Status: `{s.get('status')}`",
            f"- Space: `{s.get('space')}`",
            f"- Evidence level: `{s.get('evidence_level')}`",
            f"- Branch / source: `{s.get('branch_or_source')}`",
            f"- Session file: `{s.get('session_file')}`",
            f"- Notes: {s.get('notes', '')}",
            "",
        ]
        for ref in s.get("evidence", []):
            session_lines.append(f"- Evidence: `{ref.get('kind')}` — `{ref.get('ref')}`" + (f" — {ref.get('note')}" if ref.get("note") else ""))
        session_lines.append("")

    timeline_lines = ["# Event timeline", "", "Append-only ledger. Older events are preserved; newer checkpoints are appended by `checkpoint`.", ""]
    for e in sorted(events, key=lambda x: (x.get("timestamp", ""), x.get("id", ""))):
        timeline_lines += [
            f"## `{e.get('timestamp')}` · {e.get('id')} · {e.get('kind')}",
            "",
            f"- Title: {e.get('title', '')}",
            f"- Space: `{e.get('space', 'ops')}`",
            f"- Evidence level: `{e.get('evidence_level', 'session_memory')}`",
            f"- Details: {e.get('details', '')}",
        ]
        for ref in e.get("evidence_refs", []):
            timeline_lines.append(f"- Ref: `{ref}`")
        timeline_lines.append("")

    decision_lines = ["# Decision log", "", "Append-only. Each decision carries its evidence level; rejected options stay visible.", ""]
    for d in decisions:
        decision_lines += [
            f"## `{d.get('timestamp')}` · {d.get('id')}",
            "",
            f"- Decision: {d.get('decision', '')}",
            f"- Why: {d.get('why', '')}",
            f"- Rejected: {d.get('rejected', '')}",
            f"- Evidence level: `{d.get('evidence_level')}`",
            f"- Refs: {', '.join(f'`{x}`' for x in d.get('evidence_refs', []))}",
            "",
        ]

    prompt_lines = ["# Prompt → result log", "", "Exact wording is preserved where an export or screenshot shows it; reconstructed wording is labelled.", ""]
    for p in prompts:
        prompt_lines += [
            f"## `{p.get('timestamp')}` · {p.get('id')} · {p.get('kind')}",
            "",
            f"- Evidence level: `{p.get('evidence_level')}`",
            f"- Exact-text confidence: `{p.get('exact_text_confidence')}`",
            f"- User prompt: {p.get('user_prompt', '')}",
            f"- Assistant result: {p.get('assistant_result', '')}",
            f"- Consequence: {p.get('consequence', '')}",
            f"- Refs: {', '.join(f'`{x}`' for x in p.get('evidence_refs', []))}",
            "",
        ]

    channel_lines = ["# Channel index", "", f"Active channel: `{channels.get('active_channel')}`", "", channels.get("repo_config_note", ""), ""]
    for ch in channels.get("channels", []):
        channel_lines += [
            f"## {ch.get('id')} — {ch.get('name')}",
            "",
            f"- Role: `{ch.get('role')}`",
            f"- Status: `{ch.get('status')}`",
            f"- Space: `{ch.get('space')}`",
            f"- Entrypoint: `{ch.get('entrypoint', '')}`",
            f"- Capsule: `{ch.get('capsule', '')}`",
            f"- Next action: `{ch.get('next_action', '')}`",
            "",
        ]
    for doc in channels.get("channels", [{}])[0].get("source_docs", []):
        channel_lines.append(f"- Source: `{doc}`")
    channel_lines.append("")

    by_level = {}
    for f in manifest.get("files", []):
        by_level[f.get("evidence_level", "unknown")] = by_level.get(f.get("evidence_level", "unknown"), 0) + 1
    manifest_md = [
        "# Evidence manifest summary",
        "",
        f"- Generated at: `{manifest.get('generated_at')}`",
        f"- Head: `{manifest.get('head')}`",
        f"- Files: {len(manifest.get('files', []))}",
        "",
        md_json(by_level),
        "Full machine-readable hashes are in `EVIDENCE_MANIFEST.json`.",
    ]

    return {
        C / "STATE.md": "\n".join(state_md) + "\n",
        C / "COVERAGE.md": "\n".join(coverage_md) + "\n",
        C / "SESSION_INDEX.md": "\n".join(session_lines) + "\n",
        C / "TIMELINE.md": "\n".join(timeline_lines) + "\n",
        C / "DECISION_LOG.md": "\n".join(decision_lines) + "\n",
        C / "PROMPT_RESULT_LOG.md": "\n".join(prompt_lines) + "\n",
        C / "EVIDENCE_MANIFEST.md": "\n".join(manifest_md) + "\n",
        C / "CHANNEL_INDEX.md": "\n".join(channel_lines) + "\n",
    }


def render(check=False):
    # Normalize trailing blank lines so generated ledgers do not add EOF whitespace.
    outputs = {path: content.rstrip() + "\n" for path, content in render_outputs().items()}
    changed = []
    for path, content in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                changed.append(rel(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if check:
        if changed:
            print("Render check failed; stale generated files:", ", ".join(changed))
            return 1
        print("Render check passed: generated ledgers are current.")
        return 0
    print(f"Rendered {len(outputs)} human-readable ledgers.")
    return 0


def first_key(obj, keys, default=None):
    for k in keys:
        if isinstance(obj, dict) and k in obj and obj[k] is not None:
            return obj[k]
    return default


def content_to_str(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(content_to_str(x) for x in value)
    if isinstance(value, dict):
        for k in ("text", "content", "value", "body", "message", "parts"):
            if k in value:
                return content_to_str(value[k])
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def normalize_role(role) -> str:
    r = str(role or "unknown").strip().lower().replace("-", "_").replace(" ", "_")
    if r in {"user", "human", "you"}:
        return "user"
    if r in {"assistant", "agent", "arena_agent", "ai", "model", "gpt"}:
        return "assistant"
    if r in {"system", "tool", "continuity"}:
        return r
    return r or "unknown"


def message_from_obj(obj, seq):
    role = normalize_role(first_key(obj, ["role", "author", "sender", "speaker", "from", "actor", "type"], "unknown"))
    content = content_to_str(first_key(obj, ["content", "text", "body", "message", "value", "parts"], ""))
    timestamp = first_key(obj, ["timestamp", "created_at", "date", "time", "createdAt"], None)
    return {"seq": seq, "role": role, "content": content, "timestamp": timestamp}


def parse_messages(text: str):
    warnings = []
    stripped = text.strip()
    # 1. JSON object/array export
    if stripped.startswith(("{", "[")):
        try:
            data = json.loads(stripped)
            items = None
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for k in ("messages", "conversation", "turns", "chat", "events", "items", "data", "transcript"):
                    if isinstance(data.get(k), list):
                        items = data[k]
                        break
                if items is None and any(k in data for k in ("role", "content", "text", "message")):
                    items = [data]
            if items is not None:
                msgs = [message_from_obj(o, i + 1) for i, o in enumerate(items) if isinstance(o, dict)]
                if msgs:
                    return msgs, "json", warnings
                warnings.append("JSON contained no message objects.")
        except json.JSONDecodeError as exc:
            warnings.append(f"JSON parse failed ({exc}); trying JSONL/text.")
    # 2. JSONL
    lines = [l for l in text.splitlines() if l.strip()]
    if lines and all(l.lstrip().startswith(("{", "[")) for l in lines[: min(10, len(lines))]):
        msgs, ok = [], True
        for i, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    msgs.append(message_from_obj(obj, i))
                else:
                    ok = False
                    break
            except json.JSONDecodeError:
                ok = False
                break
        if ok and msgs:
            return msgs, "jsonl", warnings
    # 3. Markdown / prefixed plain text
    pat = re.compile(
        r"^\s*(?:#{1,6}\s*)?(?:\*\*)?(user|human|assistant|agent|arena[\s_-]?agent|system|tool|continuity)(?:\*\*)?\s*[:\-\u2013\u2014]?\s*(.*)$",
        re.I,
    )
    msgs, current = [], None
    for line in text.splitlines():
        m = pat.match(line)
        if m:
            if current:
                msgs.append(current)
            current = {"seq": len(msgs) + 1, "role": normalize_role(m.group(1)), "content": m.group(2).rstrip(), "timestamp": None}
        elif current is not None:
            current["content"] += "\n" + line
    if current:
        msgs.append(current)
    if msgs:
        return msgs, "prefixed_text", warnings
    warnings.append("No structured messages detected; raw text preserved as one unknown-role message. Manual review required.")
    return [{"seq": 1, "role": "unknown", "content": text, "timestamp": None}], "raw_text", warnings


def update_sessions_index(entry):
    idx = load_json(SESSIONS)
    sessions = idx.get("sessions", [])
    for i, s in enumerate(sessions):
        if s.get("id") == entry["id"]:
            sessions[i] = entry
            break
    else:
        sessions.append(entry)
    idx["sessions"] = sessions
    dump_json(SESSIONS, idx)


def import_chat(args):
    src = pathlib.Path(args.file).resolve()
    if not src.is_file():
        raise SystemExit(f"Not a file: {src}")
    raw_bytes = src.read_bytes()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    session_dir = SOURCES / args.session_id
    raw_dir = session_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / src.name
    if dest.exists() and sha256_file(dest) != raw_sha:
        dest = raw_dir / f"{src.stem}__{raw_sha[:8]}{src.suffix}"
    if src.is_relative_to(INBOX.resolve()):
        shutil.move(str(src), str(dest))
    else:
        shutil.copy2(src, dest)

    is_binary = src.suffix.lower() in BINARY_EXTS
    warnings = []
    if is_binary:
        messages = []
        parser = "binary_preserved_unparsed"
        warnings.append("Binary/archive source preserved byte-for-byte; no transcript normalization attempted.")
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = ""
    else:
        try:
            text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw_bytes.decode("latin-1")
            warnings.append("Decoded with latin-1 fallback; verify original encoding.")
        messages, parser, parse_warnings = parse_messages(text)
        warnings.extend(parse_warnings)

    normalized = session_dir / "normalized.jsonl"
    normalized.write_text("\n".join(json.dumps(m, ensure_ascii=False) for m in messages) + ("\n" if messages else ""), encoding="utf-8")
    norm_sha = sha256_file(normalized)

    metadata = {
        "schema_version": "1.0.0",
        "session_id": args.session_id,
        "title": args.title,
        "kind": args.kind,
        "source": args.source,
        "source_id": args.source_id,
        "source_url": args.source_url,
        "space": args.space,
        "branch": args.branch,
        "evidence_level": args.evidence_level,
        "coverage": args.coverage,
        "notes": args.notes,
        "imported_at": utcnow(),
        "parser": parser,
        "message_count": len(messages),
        "role_counts": {r: sum(1 for m in messages if m.get("role") == r) for r in sorted({m.get("role", "unknown") for m in messages})},
        "warnings": warnings,
        "raw_path": rel(dest),
        "raw_sha256": raw_sha,
        "raw_bytes": len(raw_bytes),
        "normalized_path": rel(normalized),
        "normalized_sha256": norm_sha,
        "normalized_bytes": normalized.stat().st_size,
    }
    dump_json(session_dir / "metadata.json", metadata)

    session_md = [
        f"# {args.title}", "",
        f"- Session ID: `{args.session_id}`",
        f"- Evidence level: `{args.evidence_level}`",
        f"- Coverage: `{args.coverage}`",
        f"- Source: {args.source}" + (f" (`{args.source_id}`)" if args.source_id else ""),
        f"- Raw: `{rel(dest)}` · `{len(raw_bytes)}` bytes · SHA-256 `{raw_sha}`",
        f"- Normalized: `{rel(normalized)}` · `{len(messages)}` messages · SHA-256 `{norm_sha}`",
        f"- Parser: `{parser}`", "",
        "## Notes", args.notes or "None.", "",
        "## Warnings",
    ]
    session_md += [f"- {w}" for w in warnings] or ["- None."]
    session_md += ["", "The raw file is authoritative. The normalized file is a derived convenience view; never quote it as more complete than the raw export.", ""]
    (SESSIONS_DIR / f"{args.session_id}.md").write_text("\n".join(session_md), encoding="utf-8")

    entry = {
        "id": args.session_id,
        "title": args.title,
        "status": "imported",
        "space": args.space,
        "evidence_level": args.evidence_level,
        "branch_or_source": args.branch or args.source,
        "session_file": f"docs/continuity/sessions/{args.session_id}.md",
        "notes": args.notes,
        "evidence": [
            {"kind": "file", "ref": rel(dest), "note": "raw bytes"},
            {"kind": "file", "ref": rel(normalized), "note": "derived normalized messages"},
            {"kind": "file", "ref": rel(session_dir / "metadata.json"), "note": "import metadata"},
        ],
    }
    update_sessions_index(entry)

    event = {
        "id": f"evt-import-{args.session_id}-{utcnow().replace(':', '').replace('-', '')}",
        "timestamp": utcnow(),
        "kind": "transcript_import",
        "title": f"Imported {args.title}",
        "space": args.space,
        "evidence_level": args.evidence_level,
        "details": f"Preserved {len(raw_bytes)} raw bytes and {len(messages)} normalized messages; coverage={args.coverage}.",
        "evidence_refs": [rel(dest), rel(normalized), rel(session_dir / "metadata.json")],
    }
    append_jsonl(EVENTS, event)
    state = load_json(STATE)
    state["updated_at"] = utcnow()
    state["last_event_id"] = event["id"]
    dump_json(STATE, state)

    refresh()
    render()
    print(json.dumps({"ok": True, "session_id": args.session_id, "raw_sha256": raw_sha,
                      "messages": len(messages), "parser": parser, "coverage": args.coverage,
                      "warnings": warnings}, ensure_ascii=False, indent=2))


def checkpoint(args):
    event = {
        "id": args.id or f"evt-{utcnow().replace(':', '').replace('-', '')}",
        "timestamp": args.timestamp or utcnow(),
        "kind": args.kind,
        "title": args.title,
        "space": args.space,
        "evidence_level": args.evidence_level,
        "details": args.details,
        "evidence_refs": args.ref or [],
    }
    append_jsonl(EVENTS, event)
    state = load_json(STATE)
    state["updated_at"] = event["timestamp"]
    state["last_event_id"] = event["id"]
    if args.status:
        state.setdefault("active_task", {})["status"] = args.status
    if args.next_action:
        state.setdefault("active_task", {})["next_action"] = args.next_action
    dump_json(STATE, state)
    refresh()
    render()
    print(f"Checkpoint appended: {event['id']}")


def validate():
    errors, warnings = [], []
    for rp in REQUIRED_FILES:
        if not (ROOT / rp).is_file():
            errors.append(f"missing required file: {rp}")
    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        return 1

    try:
        state = load_json(STATE)
        coverage = load_json(COVERAGE)
        sessions = load_json(SESSIONS)
        manifest = load_json(MANIFEST)
        events = read_jsonl(EVENTS)
        decisions = read_jsonl(DECISIONS)
        prompts = read_jsonl(PROMPTS)
        channels = load_json(CHANNELS_INDEX)
        cfg = load_json(ROOT / "config/continuity.json")
    except Exception as exc:
        print("VALIDATION FAILED: cannot parse archive:", exc)
        return 1

    for key in ("schema_version", "repo", "branch", "head_at_capture", "active_task", "active_channel", "channel_context", "claims", "gaps"):
        if key not in state:
            errors.append(f"STATE.json missing {key}")
    claims = state.get("claims", {})
    for key, value in claims.items():
        if value is not False:
            errors.append(f"claim {key} must remain false until real evidence is imported; got {value!r}")
    if not state.get("gaps"):
        errors.append("STATE.json gaps must not be empty while full Arena exports are missing")
    if not coverage.get("gaps"):
        errors.append("COVERAGE.json gaps must not be empty while full Arena exports are missing")
    if coverage.get("verbatim_transcripts", {}).get("full_arena_export_available") is not False:
        errors.append("COVERAGE must not claim the full Arena export is available")

    active = state.get("active_channel")
    if not active:
        errors.append("STATE.json missing active_channel")
    if channels.get("active_channel") != active:
        errors.append("CHANNEL_INDEX.json active_channel does not match STATE.json")
    if cfg.get("active_channel") != active:
        errors.append("config/continuity.json active_channel does not match STATE.json")
    channel_map = {c.get("id"): c for c in channels.get("channels", [])}
    if active and active not in channel_map:
        errors.append(f"active channel {active} missing from CHANNEL_INDEX.json channels")
    else:
        entry = channel_map.get(active, {})
        for key in ("entrypoint", "capsule", "state", "playbook", "workflow", "next_action", "easy_resume", "rejections", "evidence"):
            rp = entry.get(key)
            if rp and not (ROOT / rp).is_file():
                errors.append(f"active channel {active} missing {key}: {rp}")
        for doc in entry.get("source_docs", []):
            if not (ROOT / doc).is_file():
                errors.append(f"active channel source doc missing: {doc}")

    known_refs = {f["path"] for f in manifest.get("files", [])}
    external_refs = set()
    for r in sessions.get("external_refs", []):
        if isinstance(r, dict) and r.get("id"):
            external_refs.add(str(r["id"]))
        elif isinstance(r, str):
            external_refs.add(r)
    for f in manifest.get("files", []):
        p = ROOT / f["path"]
        if not p.is_file():
            errors.append(f"manifest file missing: {f['path']}")
            continue
        if p.stat().st_size != f.get("bytes"):
            errors.append(f"manifest size mismatch: {f['path']}")
        if sha256_file(p) != f.get("sha256"):
            errors.append(f"manifest hash mismatch: {f['path']}")

    for s in sessions.get("sessions", []):
        if not (ROOT / s.get("session_file", "")).is_file():
            errors.append(f"session file missing: {s.get('id')} -> {s.get('session_file')}")
        for ref in s.get("evidence", []):
            r = ref.get("ref")
            if ref.get("kind") == "file" and r not in known_refs:
                errors.append(f"session {s.get('id')} references unknown file {r}")
            if ref.get("kind") == "external" and str(r) not in external_refs:
                warnings.append(f"session {s.get('id')} external ref {r} not listed in external_refs")

    for ledger_name, rows in (("EVENTS", events), ("DECISIONS", decisions), ("PROMPTS", prompts)):
        ids = [r.get("id") for r in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"{ledger_name}.jsonl contains duplicate ids")

    inbox_files = [p for p in INBOX.iterdir() if p.is_file() and p.name not in {"README.md", ".gitkeep"}]
    if inbox_files:
        errors.append("unimported files in chat_exports/inbox: " + ", ".join(p.name for p in inbox_files))

    head = repo_head()
    base = state.get("head_at_capture")
    if base:
        r = subprocess.run(["git", "merge-base", "--is-ancestor", base, head], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            warnings.append(f"head_at_capture {base} is not an ancestor of current HEAD {head}; verify history/fetch depth")

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print("VALIDATION PASSED")
    print(f"- repo={state.get('repo')} branch={state.get('branch')} head={head}")
    print(f"- manifest_files={len(manifest.get('files', []))} sessions={len(sessions.get('sessions', []))} events={len(events)} decisions={len(decisions)} prompt_results={len(prompts)}")
    print(f"- verbatim_transcript_sessions={coverage.get('verbatim_transcripts', {}).get('imported_sessions')} (full Arena export=false)")
    print(f"- active_channel={active} channels={len(channels.get('channels', []))} channel_files={coverage.get('counts', {}).get('channel_files')}")
    for w in warnings:
        print(" - warning:", w)
    return 0


def prompt_context(channel_id=None):
    head = repo_head()
    branch = git("branch", "--show-current")
    state = load_json(STATE)
    channels = load_json(CHANNELS_INDEX)
    active = channels.get("active_channel") or state.get("active_channel") or "monarch-cam"
    requested = channel_id or active
    entry = next((c for c in channels.get("channels", []) if c.get("id") == requested), None)
    if entry is None:
        requested = active
        entry = next((c for c in channels.get("channels", []) if c.get("id") == active), {})
    capsule_path = ROOT / entry.get("capsule", "docs/continuity/channels/monarch-cam/EASY_RESUME.md")
    capsule = capsule_path.read_text(encoding="utf-8")
    ctx = {
        "{{BRANCH}}": branch,
        "{{HEAD}}": head,
        "{{TREE_URL}}": commit_tree_url(head),
        "{{ACTIVE_CHANNEL}}": requested,
        "{{CHANNEL_NAME}}": entry.get("name", requested),
        "{{CHANNEL_START}}": entry.get("entrypoint", ""),
        "{{CHANNEL_ENTRYPOINT}}": entry.get("entrypoint", ""),
        "{{CHANNEL_STATE}}": entry.get("state", ""),
        "{{CHANNEL_CAPSULE}}": capsule,
        "{{RECOVERY_COMMAND}}": "python3 tools/continuity.py recover",
    }
    return ctx


def fill_prompt(text, ctx, include_capsule=True):
    if include_capsule:
        text = text.replace("{{CHANNEL_CAPSULE}}", ctx["{{CHANNEL_CAPSULE}}"])
    for key, value in ctx.items():
        if key == "{{CHANNEL_CAPSULE}}":
            continue
        text = text.replace(key, value)
    return text


def bootstrap_text(channel_id=None):
    text = (C / "NEW_CHAT_PROMPT.md").read_text(encoding="utf-8")
    return fill_prompt(text, prompt_context(channel_id))


def channel_text(channel_id=None):
    ctx = prompt_context(channel_id)
    capsule = ctx["{{CHANNEL_CAPSULE}}"]
    for key, value in ctx.items():
        if key != "{{CHANNEL_CAPSULE}}":
            capsule = capsule.replace(key, value)
    return capsule


def resume(channel_id=None):
    rc = validate()
    print("\n" + "=" * 72 + "\n")
    print("COPY-PASTE THIS INTO THE NEW CHAT:\n")
    print(bootstrap_text(channel_id))
    print("=" * 72)
    return rc


def recover():
    state = load_json(STATE)
    expected = state.get("branch")
    branch = git("branch", "--show-current")
    if expected and branch != expected:
        raise SystemExit(f"Refusing to recover: current branch {branch} is not {expected}")
    refspec = f"+refs/heads/{branch}:refs/remotes/origin/{branch}"
    try:
        git("fetch", "origin", refspec)
        git("merge", "--ff-only", "--quiet", f"origin/{branch}")
    except RuntimeError as exc:
        print("Recovery merge failed. Back up stale untracked drafts to /tmp, restore .gitignore, run `git clean -fd -e deliverables`, then retry.")
        raise SystemExit(str(exc))
    print(f"Recovered {branch} to {repo_head()}. Run `python3 tools/continuity.py resume`.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Monarch continuity OS")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("resume", help="validate and print the exact new-chat bootstrap")
    p.add_argument("--channel", default="", help="channel id to embed; defaults to active channel")
    sub.add_parser("validate", help="validate archive integrity and honesty flags")
    sub.add_parser("refresh", help="rebuild evidence manifest and coverage counts")
    p = sub.add_parser("render", help="regenerate human-readable ledgers")
    p.add_argument("--check", action="store_true", help="fail if generated ledgers are stale")
    p = sub.add_parser("bootstrap", help="print the pasteable new-chat prompt with HEAD pinned")
    p.add_argument("--channel", default="", help="channel id to embed; defaults to active channel")
    p = sub.add_parser("channel", help="print the active channel easy-resume capsule")
    p.add_argument("channel_id", nargs="?", default="", help="optional channel id")
    sub.add_parser("recover", help="fetch and fast-forward a stale checkout")

    p = sub.add_parser("import-chat", help="preserve a raw chat/export and normalize it")
    p.add_argument("file")
    p.add_argument("--session-id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--source", default="user-provided export")
    p.add_argument("--source-id", default="")
    p.add_argument("--source-url", default="")
    p.add_argument("--space", default="ops")
    p.add_argument("--branch", default="")
    p.add_argument("--kind", default="transcript", choices=["transcript", "event_log", "archive", "other"])
    p.add_argument("--evidence-level", default="verbatim_transcript",
                   choices=["verbatim_transcript", "verbatim_event_log", "connected_app_record", "repo_evidence", "screenshot_only", "session_memory", "gap"])
    p.add_argument("--coverage", default="partial", choices=["complete", "partial"])
    p.add_argument("--notes", default="")

    p = sub.add_parser("checkpoint", help="append a continuity checkpoint")
    p.add_argument("--id", default="")
    p.add_argument("--timestamp", default="")
    p.add_argument("--kind", default="checkpoint")
    p.add_argument("--title", required=True)
    p.add_argument("--space", default="ops")
    p.add_argument("--evidence-level", default="session_memory")
    p.add_argument("--details", required=True)
    p.add_argument("--ref", action="append", default=[])
    p.add_argument("--status", default="")
    p.add_argument("--next-action", default="")

    args = ap.parse_args()
    if args.cmd == "resume":
        return resume(args.channel or None)
    if args.cmd == "validate":
        return validate()
    if args.cmd == "refresh":
        refresh()
        return 0
    if args.cmd == "render":
        return render(check=args.check)
    if args.cmd == "bootstrap":
        print(bootstrap_text(args.channel or None))
        return 0
    if args.cmd == "channel":
        print(channel_text(args.channel_id or None))
        return 0
    if args.cmd == "recover":
        return recover()
    if args.cmd == "import-chat":
        import_chat(args)
        return 0
    if args.cmd == "checkpoint":
        checkpoint(args)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
