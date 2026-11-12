# MONARCH OS — Architecture

Read in this order:

1. **[01-REPO-STRUCTURE.md](./01-REPO-STRUCTURE.md)** — the folder layout, the five spaces, the data model, the hard rules.
2. **[02-REPO-REGISTRY.md](./02-REPO-REGISTRY.md)** — all 22 GitHub repos, classified: core / satellite / asset-store / archive, plus the archive procedure.
3. **[03-SPACE-OPERATING-MODEL.md](./03-SPACE-OPERATING-MODEL.md)** — how each of the five mini spaces actually runs: pipeline, assets, scoreboard, allowed agents.
4. **[04-BUILD-WAVES.md](./04-BUILD-WAVES.md)** — the five shipping waves, each with its own verify list and rollback.
5. **[05-SPACES-OPERATING-MODEL.md](./05-SPACES-OPERATING-MODEL.md)** — the as-built space model.
6. **[06-YT-INTEL.md](./06-YT-INTEL.md)** — the research desk as it actually runs: lanes, report format, what is proven and what is still borrowed confidence.
7. **[07-MEDIA-AND-REPO-SIZE.md](./07-MEDIA-AND-REPO-SIZE.md)** — what may enter Git, where media actually lives, the measured size history, and the four guard layers. **Read before adding any video, audio, image plate, 3D model or archive.**

## The short version

- `Monarch.Overall.Work` is the control plane: one app, one deploy, five work domains.
- Five spaces: `yt-automation` (3 faceless channels + factory), `monarch-studio` (clients, films, sites, money), `personal-brand` (motivational + AI-BTS + portfolio accounts), `portfolio` (public proof), `ops` (money, tasks, calendar, agents, repos).
- 22 repos stay where they are, classified by role and linked through `config/repos.json`. Nothing is merged into this repo; nothing is deleted.
- Data lives in Supabase (already provisioned) and `config/*.json`. Never in JSX.
- Ships in five waves. Old URLs never break.
- **Git holds knowledge, not media.** `config/media-policy.json` is the rule; `scripts/media-check.mjs` enforces it; every file that lives outside Git has a row in `deliverables/INDEX.md` proving where it went. Repo target: under 1 GB, of which ~90% is text.
