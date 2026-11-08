# Monarch Cam — one command

For Monarch Cam channel work, a new Arena chat only needs:

```bash
python3 tools/continuity.py resume
```

That command validates the archive and prints the commit-pinned bootstrap with the full Monarch Cam channel capsule already embedded. To print only the channel capsule:

```bash
python3 tools/continuity.py channel
```

Full channel entrypoint: `docs/continuity/channels/monarch-cam/00_START_HERE.md`.
If continuity files are missing, see `RECOVER.md`.
