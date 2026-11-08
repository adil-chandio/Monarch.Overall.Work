# Inbox — drop real Arena chat exports here

1. Export the complete chat from Arena as JSON, JSONL, Markdown, or plain text.
2. Copy the file into this directory.
3. Run `python3 tools/continuity.py import-chat` as documented in `../../IMPORT_PROTOCOL.md`.
4. The importer moves/copies the raw bytes into `../sources/<session-id>/raw/`.

Only `README.md` and `.gitkeep` may remain here afterward. `python3 tools/continuity.py validate` fails if an unimported file is left behind, so a dropped export cannot be silently forgotten.

Do not put screenshots, summaries, session-memory reconstructions, or Drive/Notion/Linear exports here and label them `verbatim_transcript`. Use the correct `--evidence-level` and `--coverage`.
