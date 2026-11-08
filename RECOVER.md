# Stale checkout recovery — MONARCH OS

If `AGENTS.md`, `tools/continuity.py`, or `docs/continuity/` are missing, or `git rev-parse HEAD` is an old commit, the workspace is a stale checkout. Do **not** restart work from there.

Run this on `arena/390292fc-monarch-overall-work`:

```bash
git fetch origin '+refs/heads/arena/390292fc-monarch-overall-work:refs/remotes/origin/arena/390292fc-monarch-overall-work' && git merge --ff-only origin/arena/390292fc-monarch-overall-work && python3 tools/continuity.py resume
```

If stale untracked drafts block the merge, back them up to `/tmp` first, then:

```bash
git checkout -- .gitignore
git clean -fd -e deliverables
```

Then rerun the fetch/merge command above. After the files exist, the shorter command is:

```bash
python3 tools/continuity.py recover && python3 tools/continuity.py resume
```

Never switch, rename, or push another branch. Do not delete `deliverables/` or the repository `.git` directory.
