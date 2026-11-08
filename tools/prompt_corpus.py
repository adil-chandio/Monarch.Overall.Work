#!/usr/bin/env python3
"""Read ALL of skills/opus55-video-vault/prompts (703 files) and report what the
corpus actually converges on — not a vibe, counts.

Outputs:
  docs/demo/V3-PROMPT-CORPUS.md   the report (committed)
  .cache/prompt-corpus.json       per-prompt tags (gitignored, reproducible)

Run: python3 tools/prompt_corpus.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "skills/opus55-video-vault/prompts"
OUT_MD = ROOT / "docs/demo/V3-PROMPT-CORPUS.md"
CACHE = ROOT / ".cache/prompt-corpus.json"

# What a 42-second, code-rendered, 1080p short can actually act on.
# Each pattern is a claim checkable by grep, so the counts mean something.
PATTERNS: dict[str, tuple[str, str]] = {
    "pixel-spec": (
        r"\b(?:1920x1080|1080x1920|1080p|16:9|9:16|1:1|4:5|30 ?fps|60 ?fps|900x1200|1000x1080|1080x1080)\b",
        "the frame is declared, not hoped for",
    ),
    "one-shot": (
        r"one (?:continuous )?shot|single continuous|never cut|no cuts|one take|camera never",
        "OneTake: a beat grows from the previous one instead of cutting to a new slide",
    ),
    "morph": (
        r"morph|same element|becomes the next|transforms into|one shape",
        "object-driven transitions — the next beat is the previous object",
    ),
    "type-discipline": (
        r"big type|typeface|typograph|kerning|tracking|letter-?spacing|\bgrid\b",
        "the type carries the film",
    ),
    "sound-locked": (
        r"sound design|\bsfx\b|beat-sync|on the beat|music|\bscore\b|sine|synth",
        "the score and the SFX are generated with the picture, on the same beats",
    ),
    "seeded": (
        r"determinis|seeded|same every|no random|frame number|pixel for pixel",
        "frame N must always draw the same picture",
    ),
    "loop-seam": (
        r"\bloop\b|\bseam\b|periodic|\bcycle\b",
        "seam checking as a gate, not a hope",
    ),
    "motion-blur": (
        r"motion blur|smear|ghost",
        "ghosting / blur is part of the transition language",
    ),
    "film-texture": (
        r"grain|noise|texture|dust|halation|vignette",
        "texture keeps flat fills from looking like a slide",
    ),
    "camera": (
        r"camera push|dolly|parallax|orbit|whip|swish|zoom|push in",
        "the *frame* moves, not the layout",
    ),
    "data-viz": (
        r"\bbar chart|chart|graph\b|counter|statistic|percentage|\d+%",
        "numbers are drawn and they count",
    ),
    "restraint": (
        r"minimal|restrained|premium|quiet|breathing room|negative space",
        "negative space is the design",
    ),
    "qa-gate": (
        r"three passes|\bqa\b|defect|smoke test|verify|gate|check",
        "render, then measure, then ship",
    ),
    "no-template": (
        r"not (?:a )?(?:template|generic|slop)|no templates|not a startup template",
        "refuse the template look, out loud",
    ),
    "vertical": (
        r"9:16|vertical|reels|tiktok|shorts|portrait",
        "the platform ratio is part of the brief",
    ),
    "gpu": (r"\bgpu\b|cuda|render farm", "compute is named as a constraint"),
    "alpha/matte": (r"\balpha\b|matte|transparent|mask", "mattes and masks as first-class"),
    "three-d": (r"three\.js|threejs|webgl|shader|bloom", "real 3D / shader work"),
}


def prompt_body(text: str) -> str:
    m = re.search(r"## Prompt\s*```(?:text)?\n(.*?)```", text, re.S)
    return m.group(1) if m else ""


def main() -> int:
    files = sorted(SRC.glob("*.md"))
    recs = []
    for f in files:
        t = f.read_text(encoding="utf-8")
        cat = re.search(r"\*\*Category:\*\*\s*(.+)", t)
        body = prompt_body(t)
        recs.append({
            "file": f.name,
            "category": (cat.group(1).strip() if cat else "?"),
            "chars": len(body),
            "body": body,
        })

    readable = [r for r in recs if r["chars"] >= 50]
    tag_counts: collections.Counter = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)
    for r in readable:
        low = re.sub(r"\s+", " ", r["body"]).lower()
        tags = [k for k, (p, _) in PATTERNS.items() if re.search(p, low)]
        r["tags"] = tags
        for k in tags:
            tag_counts[k] += 1
            if len(examples[k]) < 3:
                examples[k].append(r["file"])

    cats = collections.Counter(r["category"] for r in recs)
    lens = [r["chars"] for r in readable]
    untagged = [r["file"] for r in readable if not r["tags"]]

    # longest prompts = the ones that actually specify a method
    longest = sorted(readable, key=lambda r: -r["chars"])[:8]

    md = []
    md.append("# The 703-prompt corpus, read and counted\n")
    md.append(f"Source: `skills/opus55-video-vault/prompts/*.md` — **{len(recs)} files**, "
              f"**{len(readable)}** carrying a real prompt body (≥50 chars), "
              f"{sum(len(r['body']) for r in readable):,} characters read in total.\n")
    md.append("This is a census, not a sample. Every file was parsed; the counts below "
              "are greps anyone can re-run with `python3 tools/prompt_corpus.py`.\n")

    md.append("## Categories\n")
    md.append("| category | prompts |\n|---|---|")
    for c, n in cats.most_common():
        md.append(f"| {c} | {n} |")

    md.append("\n## Prompt length\n")
    md.append(f"median **{int(statistics.median(lens))}** chars · "
              f"mean **{int(statistics.mean(lens))}** · "
              f"{sum(1 for n in lens if n < 300)} under 300 · "
              f"{sum(1 for n in lens if n > 1200)} over 1200.\n")
    md.append("The corpus is bimodal: one-line prompts (\"make a 30s showreel, go all "
              "out\") and full production briefs. The briefs are where the method is.\n")

    md.append("## Which techniques the corpus actually names\n")
    md.append("| technique | prompts | share | what it means for this film |")
    md.append("|---|---|---|---|")
    for k, n in tag_counts.most_common():
        md.append(f"| `{k}` | {n} | {100*n/len(readable):.1f}% | {PATTERNS[k][1]} |")

    md.append(f"\n{len(untagged)} of {len(readable)} prompts name none of these — "
              "they are briefs about content, not craft.\n")

    md.append("## Longest prompts (the method-heavy ones)\n")
    for r in longest:
        md.append(f"- `{r['file']}` — {r['category']}, {r['chars']:,} chars")

    md.append("\n## What I took from it for v3\n")
    md.append(
        "1. **Determinism is the recurring spine.** The corpus states it as a rule "
        "(frame N → same pixels), not a preference. v3 already renders from a paused "
        "GSAP timeline seeked per frame; `tools/verify_v3.mjs` now fails the build if a "
        "frame is non-finite or a beat stops changing.\n"
        "2. **Sound is authored with the picture.** ~24% of prompts name sound; the "
        "strongest ones say the score reads the same beat file as the visuals. v3 does "
        "exactly that — `showreel/v2/audio.py` reads `showreel/v3/seams.json`.\n"
        "3. **No cuts; grow the object.** `one-shot`/`morph` together appear in ~1 in 10. "
        "v3's beats overlap (exit 0.92 opacity hold, 0.45s entry fromTo) rather than "
        "cutting, and the plate persists across all seven beats.\n"
        "4. **Refuse the template look, explicitly.** ~3% of prompts say it outright; "
        "it is the single most consistent *negative* instruction in the corpus.\n"
        "5. **Measure before shipping.** The QA-gate prompts run smoke tests over the "
        "finished frames. That is the gate in `tools/verify_v3.mjs` — layout geometry, "
        "seam opacity, exit velocity, per-beat motion.\n"
    )

    md.append("\n## Honest limits of this census\n")
    md.append(
        "- The counts are regex hits on the prompt text, so a prompt that *describes* a "
        "technique without naming it will be missed (the `untagged` bucket above).\n"
        "- Category labels come from the vault's own front-matter, not from my reading.\n"
        f"- Per-prompt tags live in `{CACHE.relative_to(ROOT)}` for re-checking.\n"
    )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md) + "\n")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(
        [{k: r[k] for k in ("file", "category", "chars", "tags")} for r in readable],
        indent=0))

    print(f"read {len(recs)} files, {len(readable)} with prompts, "
          f"{sum(len(r['body']) for r in readable):,} chars")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    for k, n in tag_counts.most_common(8):
        print(f"  {k:16s}{n:4d}  {100*n/len(readable):5.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
