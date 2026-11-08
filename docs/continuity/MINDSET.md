# Latest mindset — how to continue

## The user's standing requirement

The user wants every chat, work thread, prompt, result, decision, problem, fix, and work level preserved in the repo so that a new chat can continue **exactly from the latest state** without re-showing, re-doing, re-explaining, or being asked to repeat history. Their wording includes:

> “sab kuch exactly chat hamara kaam baten Kya kis kis Tarah se Kiya q Kiya kis Tarah se hua Kya problems ai unhen solve Kya phr kese Kya mere prompts cheezen Apke results everything … new chat me phr se na Karna parhe … Wohi exactly us sab experience knowledge mindset level ke sath continue Karen Jahan abhi hen latest”

An earlier near-identical request is preserved as a verbatim user message in `chat_exports/sources/EMS-20261011-001/raw/CHAT_TRANSCRIPT.jsonl`. It also demanded: separately named permanent style libraries, one running `workflows/current` slot, hash-chained visible-chat capture, hourly/event-driven checkpoints, exact next-action capsules, and five-platform evidence sync without silent omissions.

The words “perfectly correctly accurately”, “next level”, “tabahi level”, and “bagair kuch chore miss kiye” are **acceptance goals**, not permission to claim perfection. The archive must explicitly mark gaps and lower-confidence evidence.

## Communication style

- Roman Urdu / Hinglish is normal: “Bhai”, “theek ha”, “Continue karo”, “done kro”, “bar bar ruk q rahe ho”, “Aage barh na”, “kama ko pooora kam”, “samajh gaye”, “ab batao ham kese karenge”.
- Be direct and execution-first. Do not stop after a plan when the user asked to proceed. Do not ask the same clarification twice. Do not make the user repeat screenshots or prompts already indexed.
- Lead the final answer with the actual artifact and a verified commit-pinned link. Then say exactly what is preserved, what is a gap, and the single next action.
- Preserve the user's exact corrections even when blunt; they are acceptance signals, not sentiment to soften away.

## Work style

- **Repo-first:** GitHub is the durable source of truth. Drive, Notion, Linear, Docs, Supabase, Vercel, Gmail and Dropbox are external evidence, not proof that Arena chat memory transferred.
- **Evidence-first:** raw exports > hash-chained journals > commits/runs > external records > screenshots > session memory > gaps. Never promote a lower level to a higher one.
- **Append-only:** old decisions, rejected options, failed runs, dead ends and fixes stay visible. Do not overwrite V5 or rewrite history to look cleaner.
- **One active task:** `STATE.json.active_task` is the single running continuation. `parallel_task` tracks unresolved video work separately. Old work is preserved under named sessions/levels.
- **No silent omissions:** if a source is missing, 404s, truncated, or blocked, record it in `GAPS.md` and `COVERAGE.json`.
- **Checkpoint discipline:** after meaningful work, append an event, update the state ledger, refresh hashes, regenerate ledgers, validate, commit and push. The user specifically complained that chats stop mid-work and then restart from the beginning or lose the latest running task.
- **No false claims:** technical QC is not creative approval. A rendered/validated artifact is not human full-motion/native-audio listening. Historical analytics are not retention/virality promises.

## Explicit corrections that remain binding

- V4: “sirf text likh diya” — rejected.
- V5: “NAHI abhi bhi theek se nhi” plus four screenshots — rejected.
- Animated POV: “Lekin nhi na Tune images me character ghusane ki Koshish ki … poori frame by frame” — illustrated backgrounds must be removed; scenes, character, props, lighting and movement must be rendered frame by frame, not by inserting a character into still images.
- Extinct-life wall: “Ok ab poori videos”, “Short video hamari”, “Woh poori video banao ab new level ke sath Jo hamne dekha seekha usko next level lejake” — full video at the next level, not a still-only substitute.
- Portfolio: live URL `https://adil-chandio.github.io/portfolio/`, test “MONARCH ke sath kaise kaam karoon?”, and a “Complete checklist (sab DONE)” state existed in the screenshot; this is screenshot-only evidence, not a new deployment claim.
- Continuity: “Chat memory does not magically transfer” (Drive WF‑02 start document). Missing messages must not be claimed.

## Decision hierarchy for the next agent

1. Obey root `AGENTS.md` and `python3 tools/continuity.py resume`.
2. Read `STATE.json` and the active session file.
3. Check `GAPS.md` before claiming completeness.
4. Check `DECISION_LOG.jsonl` before asking a question.
5. Check `PROBLEMS_FIXES.md` before retrying a failed approach.
6. Work on the active Arena branch only.
7. Preserve raw evidence and hashes before deriving summaries.
8. Do not re-present rejected V4/V5 work as final.
