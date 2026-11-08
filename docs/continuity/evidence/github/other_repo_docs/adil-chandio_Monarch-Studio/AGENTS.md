# Mandatory instructions for every Arena agent

Before doing any work in this repository:

1. Run `python3 tools/continuity.py resume`.
2. Treat `workflows/current/ACTIVE_TASK.json` and the latest checkpoint as authoritative.
3. Log the visible user message verbatim with `continuity.py log --kind user`.
4. Never restart a completed operation or discard a newer active task because an older chat summary appears.
5. Record every material action/result/error and every long-running process ID.
6. Checkpoint before/after long operations, after material results, on errors, before ending the turn, and at least every 55 minutes while active.
7. Keep permanent accepted knowledge inside the named style under `styles/`; keep only running work in `workflows/current/payload/`.
8. Do not mark remote sync complete without updating the target's `SYNC.json` entry with its real ID/result.
9. Do not commit credentials, hidden system instructions, private connector tokens or raw sensitive identity media.
10. Run `python3 tools/studio.py validate` before a milestone commit.

If a response/process stops, query the recorded process and execute the exact next action in `RESUME.md`; do not begin again from zero.

## Finish delivery; do not stop at a progress promise

- When a runnable production step remains, continue through process completion, QA, presentation and verified upload in the same turn. Do not end merely after starting a render or saying “continuing.” A real external blocker or an explicit user pause is different.
- Query the recorded process before launching anything. Use a blocking process wait, not duplicate renders or repeated short polling.
- A checkpoint or `status=done` is not the media itself. Confirm that every required artifact actually exists; ignored runtime folders, dependencies and ignored final masters can disappear on a workspace refresh.
- Before cloud delivery, protect only the critical pending-upload bytes in a bounded recovery spool that survives snapshots. Respect the workspace patch budget and per-file limits. Keep disposable caches ignored. After Drive IDs and checksums verify, return heavy media to the repository's external-storage/ignore convention; do not permanently add large masters to Git.
- Never say “presented” before `present_file` succeeds, or “uploaded/complete” before the upload returns a real ID and the remote size/checksum match. Presentation, local encode success, cloud delivery and source recovery are separate gates.
- For media tasks, persist a delivery receipt with the actual master/source IDs, hashes and URLs. If a delivered task receives only another “continue,” return/recover its verified deliverable rather than regenerating its images, voice or edit.
- Platform/service interruptions cannot be guaranteed away. The reliable promise is durable artifacts, exact resumption and truthful completion state—not unattended connector work between turns.

## WF-05 / MOTIONGO routing

When the user requests WF-05, WF5, Premium Motion Editing or MOTIONGO, load `styles/premium-motion-editing/FRESH_CHAT.md` and `data/approved-profile.json` before production. Default: V5 clean integrated typography plus accepted V6 non-caption motion improvements; **no V6 bottom caption pills or active-word lower strip**. Historical case renderers are not the new-project default. Use the registered style, current acceptance policy and source-backed lessons rather than recreating the workflow from memory.
