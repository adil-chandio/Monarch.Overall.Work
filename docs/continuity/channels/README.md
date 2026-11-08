# Channel continuity — one-command resume

This directory makes channel work easy to inherit in a new Arena chat. The active channel workstream is **Monarch Cam**.

- Root shortcut: `MONARCH_CAM.md`
- Channel start: `channels/monarch-cam/00_START_HERE.md`
- Copy-paste capsule: `channels/monarch-cam/EASY_RESUME.md`
- Machine state: `channels/monarch-cam/CHANNEL_STATE.json`
- Exact next action: `channels/monarch-cam/NEXT_ACTION.md`
- Full playbook: `channels/monarch-cam/PLAYBOOK.md`
- Production workflow: `channels/monarch-cam/WORKFLOW.md`
- Rejections/dead ends: `channels/monarch-cam/REJECTIONS.md`
- Commits/runs/hashes: `channels/monarch-cam/EVIDENCE.md`

`python3 tools/continuity.py resume` now embeds the active channel capsule automatically. `python3 tools/continuity.py channel` prints only that capsule. A new chat does not need the user to explain “yeh aise karna hai”.

## Three-channel note

The owner describes Monarch Cam as one of the three channels. `config/channels.json` currently carries three legacy publishing slots: `Monarch Lab`, `Mindful Momentum`, `Curious Miles`. Monarch Cam also has its own live YouTube channel `@Monarch-Cam` and the `production/monarch-cam/` tree. Until the owner explicitly renames a config slot, continuity treats Monarch Cam as the **active channel workstream** and preserves the legacy config unchanged. Do not delete, rename, or invent a fourth config slot. This mismatch is an explicit gap in `CHANNEL_INDEX.json`, `STATE.json` and `GAPS.md`.

## Recovery

If `AGENTS.md`, `tools/continuity.py` or `docs/continuity/` are missing, the workspace is a stale checkout. Use root `RECOVER.md` / `python3 tools/continuity.py recover` before any production work.
