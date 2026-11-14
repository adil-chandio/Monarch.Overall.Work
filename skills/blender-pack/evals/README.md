# Skill evals

Structural validation proves a skill is well-formed. It does not prove the skill
changes what a model produces. These evals test the second thing.

Each case is a prompt plus the decisions a competent technical artist must make in
response. The scorer is deliberately mechanical: it looks for the specific numbers
and named techniques the skill exists to supply. A model that has *not* read the
skill can still produce a plausible paragraph, so plausibility is not the test —
**the presence of the skill's own numbers is.**

## Why this shape

The upstream pack could not be evaluated at all, because 48 skills contained no
claim specific enough to test. `frutiger-aero-style` said "glossy bubbles, fresh
greens"; no output can be marked wrong against that. Every rewritten skill carries
numbers precisely so it can be checked.

## Running

```bash
python3 evals/run.py            # all cases
python3 evals/run.py --case 3   # one case
```

Without a model connection the runner reports each case as `SKIP` and exits 0, so
it is safe in CI. With one, it scores.

## What a case checks

| field | meaning |
| --- | --- |
| `skill` | the skill under test |
| `prompt` | a real request that should trigger it |
| `must` | regexes that must appear — the skill's own numbers or named techniques |
| `must_not` | regexes that indicate the failure mode the skill names |

`must_not` matters as much as `must`. A response that says "roughness 0.10 with a
clearcoat" *and* "keep everything matte" has read the skill and missed the point.
