# MONARCH OS — Architecture

Read in this order:

1. **[01-REPO-STRUCTURE.md](./01-REPO-STRUCTURE.md)** — the folder layout, the five spaces, the data model, the hard rules.
2. **[02-REPO-REGISTRY.md](./02-REPO-REGISTRY.md)** — all 22 GitHub repos, classified: core / satellite / asset-store / archive, plus the archive procedure.
3. **[03-SPACE-OPERATING-MODEL.md](./03-SPACE-OPERATING-MODEL.md)** — how each of the five mini spaces actually runs: pipeline, assets, scoreboard, allowed agents.
4. **[04-BUILD-WAVES.md](./04-BUILD-WAVES.md)** — the five shipping waves, each with its own verify list and rollback.

## The short version

- `Monarch.Overall.Work` is the control plane: one app, one deploy, five work domains.
- Five spaces: `yt-automation` (3 faceless channels + factory), `monarch-studio` (clients, films, sites, money), `personal-brand` (motivational + AI-BTS + portfolio accounts), `portfolio` (public proof), `ops` (money, tasks, calendar, agents, repos).
- 22 repos stay where they are, classified by role and linked through `config/repos.json`. Nothing is merged into this repo; nothing is deleted.
- Data lives in Supabase (already provisioned) and `config/*.json`. Never in JSX.
- Ships in five waves. Old URLs never break.
