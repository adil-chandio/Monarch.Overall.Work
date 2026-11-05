# Extinct Life — successful API audit and new findings

## Verified retrieval

Run: https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42075051940

Raw public evidence: `data/extinct-life-public-api.json` (same directory). This is a public metadata/comment-sample audit, not audiovisual viewing. Original Studio analysis remains in `2026-11-05-extinct-life-forensic-audit.md`.

- API channel ID: `UC39HqOh_7b5GSh99O2b7dbg`.
- Public uploads playlist: `UU39HqOh_7b5GSh99O2b7dbg`.
- API channel statistics: 87 subscribers, 8 videos, 26,570 channel views.
- Channel creation timestamp: 2024-11-26T15:46:26.57996Z; country field US.
- Uploads playlist exhausted; 8 IDs returned; all 8 resolved to metadata; no missing IDs.
- This inventory does not reveal private/draft uploads or their status. It does not settle the visibility of the two date-named Studio rows.
- Full descriptions and duration/statistics are retrieved for all eight public records.
- The API returned no `snippet.tags` values for these eight records. Hashtags and keyword lists in descriptions are not the separate tags field. This does not prove that adding tags would improve reach.

## Public video inventory

| Video | Duration | API views | Watch URL |
|---|---:|---:|---|
| The Last Thing Dinosaurs Ever Saw 💀 | 38 s | 1,218 | https://www.youtube.com/watch?v=_gE4z5YWLuE |
| Pov: Survived T-rex Attack ☠️ | 45 s | 1,292 | https://www.youtube.com/watch?v=DHdcxPn3z2s |
| Your DNA has a 250 Million Year Old Secret… | 30 s | 1,524 | https://www.youtube.com/watch?v=N4Oj48qgRaE |
| Modern Elephant vs. Prehistoric GIANTS! | 24 s | 16,733 | https://www.youtube.com/watch?v=X0whihfTI0Y |
| Imagine seeing this in your backyard… | 23 s | 1,842 | https://www.youtube.com/watch?v=INxEsSReE4o |
| Nature’s 8-Foot… | 65 s | 1,079 | https://www.youtube.com/watch?v=_DEYK1KNavQ |
| Forget the T-Rex. Meet the “Terminator Pig.” | 50 s | 514 | https://www.youtube.com/watch?v=QGEe0CkintQ |
| Why Evolution “Deleted” This Monster… | 68 s | 2,373 | https://www.youtube.com/watch?v=67tS2yDDvcs |

Public per-video view counts sum to 26,575, versus 26,570 on the channel aggregate. Preserve this small discrepancy; different update times/scopes are possible, but the cause is not established. Do not force totals to reconcile by editing evidence.

## What the full descriptions newly establish

### 1. Last Thing Dinosaurs

Description promises the dinosaurs' last moments and says the impact flash was “brighter than 1000 suns” and “This is what really happened 66 million years ago.” It includes repeated hashtag blocks and a long comma-separated keyword list.

Editorial concern: the precise brightness analogy needs a source and observation conditions before being presented as established fact. “What really happened” should not imply certainty about a reconstructed individual animal's experience. These are claims in the description; the spoken script has not been retrieved. Keyword repetition is visible, but no causal reach penalty is established.

### 2. T-rex POV

Description explicitly states **AI-generated POV**, first-person dinosaur survival, cinematic/immersive positioning, and asks viewers to watch until the end. This confirms an AI production disclosure for this upload, not a specific tool or generation workflow and not disclosure across all uploads.

It is a survival spectacle concept, unlike the factual comparison promise of the strongest video. Treat format changes as real experimental variables. No judgment of actual motion, sound, visual continuity or payoff is justified without media.

### 3. DNA Secret

Full description identifies **Inostrancevia**, calls it a synapsid and “one of our earliest relatives,” and uses “carrying the blood of an ancient executioner.” It describes “8-inch sabers.”

Research gate: distinguish shared ancestry/related lineages from direct human ancestry; substantiate the specific measurement and timeframe. A relationship metaphor must not become an unsupported claim that humans directly descend from this genus. Caption/script verification is pending; no corrected scientific numbers are asserted here.

### 4. Elephant / Giants

Description specifically names **Deinotherium, Platybelodon and the Straight-tusked Elephant**. This confirms why Platybelodon is relevant to the video rather than just an unrelated search term. The description says “prehistoric ancestors”; check each taxon's relationship before using direct-ancestor wording. “Ancient relatives” may be safer pending sourcing.

There is an owner-authored question about the scariest ancient giant, with one reply counted. A top-level question by the creator is not independent proof of audience demand. The strongest evidence remains the actual Studio retention/search data and public views.

### 5. Backyard

Description identifies **Quetzalcoatlus northropi**, says 68 million years ago, and compares height with a giraffe and wingspan with a fighter jet. Each analogy needs a specified comparison/reference and a credible range; a “fighter jet” is not a unique measurement. Hashtags mix paleontology, horror, cryptid and AI art. That is a visible positioning mix, not evidence that YouTube penalized it.

### 6. Nature's 8-Foot

Description identifies **Arthropleura** and calls it a “centipede,” “500-pound, armor-plated killing machine,” and “biological error.” This needs priority scientific fact-checking of classification, mass and feeding behavior before reuse. These phrases are not validated by the API; they are the channel's published claims. No actual hunting scene or voiceover was watched in this audit.

The description offers a Titanoboa vs Terror Bird next-topic vote. Its retrieved top-level comment is creator-authored; no audience vote distribution was fetched.

### 7. Terminator Pig

Description identifies **Daeodon**, says 30 million years ago, 2,000 pounds, “fought its own kind for sport,” and claims a bowling-ball-crushing bite. These assertions need sources, especially inferred motive (“for sport”) and unquantified bite spectacle. Do not silently reuse them as established facts in automated scripts.

It repeats “biological glitch,” “deleted” and “nature doesn't usually make mistakes” language also seen elsewhere. This is a recognizable rhetorical template, but it can confuse evolutionary mechanisms with intention. The video has 514 public views; the evidence does not isolate whether script, premise, duration or visuals caused that outcome.

### 8. Evolution Deleted

Description identifies **Edestus**, introduces tooth/jaw mechanics and a scissors analogy, and again uses “biological glitch” rhetoric. Check tooth retention, biomechanics and extinction explanation against credible sources. The retrieved top-level comment is the creator asking for next topics; two replies are counted but their text was not collected.

## Comment evidence: important scope

The runner requested up to 100 top-level comments per video using the existing client. Last Thing and POV returned no top-level items; DNA returned one viewer comment (“yes”) with a reply count. Each of the other five returned one creator-authored top-level prompt. Total: six top-level records, five creator-authored and one viewer-authored. Reply bodies were not fetched. This is not a complete audience conversation analysis, and the prompts should not be passed off as unsolicited viewer demand.

## Transport problem: what was actually fixed

1. The local runtime has no injected YouTube key. Existing historical repository reports show API success on GitHub Actions; the new run also resolved an existing secret without printing its value.
2. `yt_intel.channel()` previously used HTML/RSS even with an API key. It now routes keyed requests through `channels.list` (handle lookup), paginated `playlistItems.list`, and batched `videos.list`.
3. Added explicit completeness / truncation / unresolved-ID reporting and scrubbed error details.
4. Manual workflow dispatch from this sandbox returned 403. A current-branch-only push trigger successfully started the dedicated audit instead; this did not grant or change integration permissions.
5. Artifact downloading redirected to a storage host inaccessible from the sandbox. The runner now commits only the public report to the same session branch, allowing retrieval through GitHub/git. Raw video is not committed. Artifacts remain available on the run page.
6. All eight transcript attempts returned bot-verification errors from yt-dlp. The Data API key does not authenticate public-player extraction or grant owner-authorized caption downloads. No cookies were obtained or requested, and no content-access protection was bypassed.

## Tests and repeatable use

- `python -m unittest yt_intel.channel_test`: 7 tests passed.
- Existing `python -m yt_intel.test_offline`: 87 assertions passed in the local virtual environment.
- Local API use when a server-side key is already configured:
  `python scripts/audit-yt-channel.py @extinct_life --transcripts --out .cache/yt-intel/extinct-life-audit`
- Workflow: `.github/workflows/yt-channel-audit.yml`. Push triggers restricted to this session branch and audit-file paths. No schedule and no paid service added.

## Remaining limits

Successful API metadata retrieval is not equivalent to watching eight videos. Actual shot-by-shot frames, spoken words, sound design, music licensing, burned-in captions, creative continuity and source accuracy still require accessible media and source research. The owner does not need to resupply basic channel metadata or IDs now; they have been recovered. Do not request or publish an API key in chat.
