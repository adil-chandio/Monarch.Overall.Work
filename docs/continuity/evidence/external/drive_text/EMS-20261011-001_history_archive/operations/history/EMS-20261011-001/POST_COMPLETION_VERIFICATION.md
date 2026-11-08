# Post-completion verification addendum

Task `EMS-20261011-001` completed and was archived at commit `297231d8e17e5f6c1b0cbbad300a6459a99efd31`; its active slot was reset to the repository's canonical idle state. Annotated tag `v0.2.0` points to that completion snapshot.

## Clean-checkout failure discovered after completion

- GitHub Actions run: `38090848950`
- URL: <https://github.com/adil-chandio/Monarch-Studio/actions/runs/38090848950>
- Result: failed during repository-manifest validation.
- Exact symptom: the manifest retained three paths formerly under `workflows/current/payload/` after completion had moved them into `operations/history/EMS-20261011-001/payload/`.
- Root cause: in compact sparse mode, manifest regeneration preserved every absent path still present in the pre-staging Git index. That incorrectly treated freshly moved materialized files as sparse-omitted files.

## Permanent correction

- Manifest preservation now accepts an absent prior entry only when `git ls-files -v` marks that exact path `S` (`skip-worktree`).
- Deleted or moved materialized paths are therefore removed before `git add`, while genuine sparse-omitted heavy files retain their last verified SHA-256 records.
- Validation uses the same explicit skip-worktree rule.
- A regression test asserts that every missing manifest path is genuinely marked skip-worktree.
- Push-triggered CI is scoped to `main`; release-tag pushes do not duplicate validation already completed for the tagged commit. Hourly scheduled CI and pull-request CI remain enabled.

`v0.2.0` remains an immutable historical completion snapshot. The corrected, clean-checkout-verified release is published as `v0.2.1` after the replacement CI run succeeds.
