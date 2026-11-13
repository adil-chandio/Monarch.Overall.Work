# monarch-temple-3d

**artifacts-pending** · 480/480 frames (100%) · updated 2026-11-13T05:59:30.616Z

> Mafia temple 3D — 480 frames, 20s, 1280x720, 14/14 QC; final MP4 to Drive then YouTube

## Resume here

```bash
bash scripts/render-all.sh   # re-render only if frames are missing; otherwise encode + upload
```

LESSON from 2026-11-13: the previous attempt finished all 480 frames and a 12.6 MB MP4, then went idle without uploading. The reset took everything. This time: upload the MP4 to Drive the moment ffmpeg exits, run 'job.mjs uploaded' with the drive_id, and only then pause.

## Artifacts

_none yet_

## Log

- `05:56` started: Mafia temple 3D — 480 frames, 20s, 1280x720, 14/14 QC; final MP4 to Drive then YouTube
- `05:56` 480/480 frames + 20s MP4 verified in the other session's sandbox; that sandbox is gone, so the file must be re-produced and uploaded
- `05:57` ledger now pushes itself; verified
- `05:59` hardened: pause now refuses when the ledger is not committed AND pushed
