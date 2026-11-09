# Reliable YouTube API audit execution

## Diagnosed causes and implemented fixes

1. **Manual Actions dispatch returns HTTP 403 for this integration.** The connection can push code and read run information, but `workflow_dispatch` is not permitted. Repeatedly issuing the same dispatch command cannot fix that. The new `yt-validation-audit.yml` runs on a scoped push to the session branch, so routine research no longer depends on that permission. This does not pretend to grant or repair the integration's dispatch permission itself.
2. **The legacy topic workflow did not listen to pushes on this session branch.** The new workflow explicitly listens to `arena/ba8d901e-monarch-overall-work` and a small allowlist of request/code/test paths.
3. **Artifact downloads redirect to an Azure CDN inaccessible from this sandbox.** The first new audit ran successfully, but its artifact download failed at that transport boundary. Reports are now also published through GitHub's Contents API to exactly `production/extinct-life/research/api-results/latest.json` on this branch. GitHub artifact storage remains a secondary copy, not the only delivery mechanism.
4. **A missing local API key does not establish a missing repository secret.** Key resolution occurs on the GitHub runner using existing secret names. Values are never printed, committed or included in reports. No credentials should be supplied in chat.

## Routine research entry point

Edit `production/extinct-life/research/api-requests/next-topic.json`, commit and push **only to this session branch**. Do not routinely use `gh workflow run` while this connection lacks dispatch permission. For a repeat of identical query settings, change/add a harmless `request_id` string so the request file actually changes and the push event fires.

Request fields:

- `queries`: 1–4 nonempty strings, each at most 160 characters.
- `orders`: 1–3 entries from `relevance`, `viewCount`, `date`.
- `results_per_query`: integer 1–50; default 25.
- Optional `request_id`: an operator-supplied unique label. No secrets.

The script has an attempted-quota ceiling of 1,300 units, validates requests before networking, and never executes query text as shell code. It first checks an inexpensive API endpoint, then collects bounded searches, deduplicated video statistics and public channel context. It does not call uploads or obtain competitor private analytics.

The workflow uses `contents: write` solely to publish the public report through a fixed-path, fixed-branch code path. It does not publish a video, mutate existing film assets, auto-merge, switch branches or push through a bot checkout. The publication commit has `[skip ci]`; the result path is outside the workflow's push triggers, preventing a research loop.

## Reading a result without the artifact CDN

Read the run ID from the workflow's runs endpoint (the workflow ID was 412444855 when created). Inspect its status, then retrieve the fixed report through the repository Contents API or sync the session branch with `git pull --ff-only origin arena/ba8d901e-monarch-overall-work` when the worktree is clean. Confirm `git_commit` in the report corresponds to the source run; a previously existing `latest.json` must never be passed off as the new run's output.

**The green Actions badge alone is not research success.** Read `status` and `api_validation_passed`:

- `measured`: API preflight passed and public videos were collected.
- `empty_sample`: the requests succeeded but no videos were obtained; not proof of zero demand.
- `partial`: some search/video evidence exists, followed by a recorded failure. Do not present it as a complete sample.
- `blocked`: key/access/network dependency prevented collection; no substitute fabricated counts or stale/web results.
- `invalid_request`: schema/input failure; fix the request instead of retrying the API.

Counts carry UTC observation timestamps. Estimated attempted quota is conservative, including failed/retried calls, and is not a query of Google's actual remaining project quota. Search results are a bounded sample, not all of YouTube. Lifetime view counts are not current growth velocity.

## Error handling and regressions

- Permission/key/quota 4xx failures are recorded without repeated blind retries.
- Transient 429/5xx/network failures get at most three attempts, within the local quota ceiling.
- Error output contains only a sanitised reason/status; no API key, signed download URL or raw request URL.
- Missing statistics remain absent, never silently replaced with zero.
- Partial evidence is preserved.
- Eight offline tests cover request validation, permanent/transient failure behaviour, secret-safe error messages, partial results, missing fields, timestamps and workflow publication scope.

Run tests:

```sh
python -m unittest discover -s tests -p test_yt_validation_audit.py -v
```

These fixes remove the known dispatch/trigger/result-delivery traps from routine operation. They cannot guarantee that Google/GitHub will never change permissions, quota, service availability or schemas. New external failures must remain explicit and diagnosable, not hidden or described as successful research.

## Verified end-to-end run

Run [42677248759](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42677248759) completed successfully. Its actual report says `status: measured`, `api_validation_passed: true`, 6 searches, **121 deduplicated public videos**, **107 channels**, 13 API attempts and 607 conservatively estimated attempted quota units. No API error was recorded. The Contents API publication was successfully fetched via the session branch, not through the blocked artifact CDN.

The runner initially emitted Node-action/rolling-Ubuntu migration warnings. The workflow now pins the reviewed official action release commits (Node 24 compatible) and uses `ubuntu-24.04`, with a regression test to prevent accidentally restoring floating action tags or the rolling image.

This is public-metadata research only, not completed frame-by-frame/continuous-listening study. Follow-up comparative screening is still required. In particular, Vasuki searches also returned mythology and the broader frozen-animal searches returned unrelated material: raw million-view search hits are not automatically relevant or scientifically reliable references.
