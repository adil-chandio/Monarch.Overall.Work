# YouTube idea-validation standard — user-requested upgrade

## Decision and scope

The user's requested improvement is accepted: a scientifically interesting idea is not automatically a validated audience opportunity. Future recommendations must distinguish **creative promise**, **scientific verification**, **observed public performance**, and **actual audiovisual review**. None implies the others.

The Homotherium cub remains a **provisional promising candidate**, not a proven million-view winner. The earlier recommendation was based on primary scientific reading and a limited indexed packaging scan. The new observations below improve that evidence but do not complete validation.

## What was actually checked in this turn

- Inspected repository `yt_intel` API/reverse/forensic tooling and the existing Actions workflow.
- Checked credential presence without displaying values: no recognised YouTube key was present in the local environment; no root `.env`/`.env.local` file was reported by the presence check.
- GitHub secret-list access returned HTTP 403, so remote secret configuration remains **unknown**, not proven absent.
- Attempted the existing topic workflow on the current session branch with topic `Homotherium frozen cub`, limit 30, order `viewCount`, comments_max 1. Dispatch returned **HTTP 403: Resource not accessible by integration**. No new API job was created by this attempt.
- YouTube connector lookup returned unsupported. This is separate from the repository's custom API tooling.
- Directly fetched five public YouTube watch pages. Read the returned metadata and transcripts to the extent stated below. These page-extracted counts have no verified freshness timestamp and were **not** independently checked against Data API v3. Do not call them exact live API measurements.
- The Shorts-path fetch for `-DF7Ll_2U90` returned a malformed-request error page; its standard watch page subsequently returned metadata and transcript. Do not treat an error page as a successful video review.

## Page-reported observations — not API receipts

| Channel / video | Duration | Views reported by fetched page | Transcript scope in this turn |
|---|---:|---:|---|
| Dr Ben Miles — World's First Saber-tooth Tiger Cub Discovered in Permafrost | 0:59 | 613,621 | Entire returned transcript read; no continuous audiovisual playback. |
| 7 Days of Science — Sabre-Toothed Cat Mummy Found Frozen in Ice | 10:41 | 134,472 | First returned transcript chunk only; remainder not opened. |
| Nature's Compendium — We got the first Saber Tooth Cat Mummy in History before GTA 6 | 7:45 | 30,429 | First returned transcript chunk only; remainder not opened. |
| Museum of Science — 35,000-Year-Old Saber-Toothed Cub Found | 0:53 | 10,517 | Entire returned transcript read; no continuous audiovisual playback. |
| EDÜCLECTIC — Saber Toothed Tiger Cub Was Found In Siberia. What Does This Mean? | 3:32 | 2,563 | Entire returned transcript read; no continuous audiovisual playback. |

Sources, in table order:

- https://www.youtube.com/watch?v=-DF7Ll_2U90
- https://www.youtube.com/watch?v=Asl5qSPrNN8
- https://www.youtube.com/watch?v=ye0uSjuARmU
- https://www.youtube.com/watch?v=PeEAZ8ZTlcg
- https://www.youtube.com/watch?v=zDtRyuPxQA8

No million-view example was established in **this small sample**. This does not establish that none exists. Search selection, upload age, channel baseline and different formats prevent a causal comparison. Thumbnail URLs were returned but their pixels were not opened/analysed in this turn. No comments, audience retention curves, CTR or competitor private analytics were obtained.

### Transcript-level observations, not proven causes of performance

- The Dr Ben Miles transcript leads with the specific cub/discovery, then age and comparative anatomical details, adds humour and ends with other frozen finds/an open question.
- The Museum of Science transcript starts with an audience greeting/question and includes a permafrost definition before listing anatomical differences.
- Nature's Compendium supplies chapters putting the broader saber-toothed-cat explanation before its mummy-features section at 2:35. Those are published chapter boundaries, not measured scene cuts or retention events.
- These differences can generate **testable storytelling hypotheses**, not statements that humour, a definition, title wording or category caused the view counts.
- Retrieved transcripts have obvious recognition errors in scientific names. Verify against audio before quoting or attributing an apparent scientific error to a creator. Independently check factual claims against the original paper; do not copy an automated transcript into our script.

## Proposed research gate before calling any idea validated

This is the intended operating standard, **not a claim that all steps below have already run**.

### 1. Bounded discovery, not “scrape all of YouTube”

Start with a manageable pool, e.g. 30–60 videos across the exact subject, adjacent extinct-life/science subjects and comparable storytelling in another niche. Sample recent and older results, large and smaller channels, high performers **and controls**. Log query, ordering, sample limits and retrieval time. Search/API coverage is incomplete; do not promise platform-wide exhaustiveness or bypass access restrictions.

### 2. Timestamped API receipts where access permits

Collect video/channel IDs, publication time, duration, public views/likes/comments and available channel context. Mark missing/hidden values as unavailable, not zero. Public Data API metadata does not expose a competitor's private CTR, retention curve or internal traffic-source analytics, and does not itself establish exact keyword search volume.

Use channel-normalised comparisons with comparable uploads, separating Shorts and long form. Lifetime views divided by age is a lifetime average, **not current velocity**. Current growth needs repeated timestamped observations. A million views alone is neither a causal explanation nor a guarantee that a new channel can reproduce it.

### 3. Select an actual review set

Choose a small set of strongest relevant candidates plus lower-performing comparators. Where authorised/accessibly playable, review complete audiovisual material, not only titles/transcripts. Log exact video IDs and coverage windows. If media is unavailable, label the analysis transcript-only or metadata-only and leave audiovisual conclusions unresolved.

### 4. Forensic teardown

For each reviewed reference, record separately:

- Title promise, specificity, omissions and correspondence to the actual payoff.
- Thumbnail subject, composition, contrast, text and title complementarity—only after opening the actual image.
- First visual action, first spoken promise, first evidence reveal and payoff timing.
- Scene changes, meaningful new events, deliberate holds and repetitions.
- Voice cadence, pauses, music/foley entrances and transitions—only where listening actually occurred.
- Transcript claim ledger with primary-source checks.
- Public comment questions, objections and repeated interests, with the sample size and sorting bias stated.
- Observed fact versus editorial interpretation versus an untested hypothesis.

No invented frame-by-frame approval, inferred retention graph or “10 exhaustive reviews” from ten model passes.

### 5. Ethical reverse-engineering

Extract a **mechanism**, not another creator's expression: e.g. question → concrete clue → escalation → explanation → satisfying payoff. Cross-niche structures such as a restoration reveal or a mystery investigation are hypotheses to adapt, not proof of a transferable viral formula.

Build a new script from independently verified sources, a new visual plan and original/licensed assets. Do not copy scripts, trace a distinctive thumbnail, lift footage/music, invent reactions, fabricate evidence or imply endorsement. Educational intent alone does not automatically grant footage/thumbnail rights.

“Reverse psychology” is not a magic growth technique. Prefer honest curiosity, expectation reversal and a delivered payoff; avoid manipulative forbidden-secret claims and withholding an answer the video promised to provide.

### 6. Originality and production-feasibility check

Explain the viewer benefit our version adds, how it differs from the sampled references, and what can actually be produced accurately. For the cub: anatomical reconstruction, missing mummy tissue, CT versus illustrative scan and cub/adult tooth development all require care. An interesting topic does not waive those gates.

### 7. Final recommendation states

- **Promising:** credible evidence and a useful creative premise.
- **Public-performance supported:** timestamped, comparable performance evidence is available, with sampling limits.
- **Reference-reviewed:** specified audiovisual coverage and packaging inspections actually completed.
- **Ready to script:** factual, original-story and production checks pass.
- **Owner-approved:** the user explicitly approves the proposal.

Do not collapse these labels into “perfect/guaranteed viral.” Even a thoroughly checked original video can underperform.

## Current next step / blocker

Do not sell the cub as a validated viral winner yet. Complete a bounded, timestamped comparative sample and actual packaging/audiovisual review, using API receipts once execution is permitted. The present GitHub integration can read run information but **could not dispatch** the research workflow; that permission/access needs attention. No API key, password or token should be pasted into chat or committed to the repository. Existing films and metadata are unchanged.
