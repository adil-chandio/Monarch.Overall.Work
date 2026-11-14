# Blender Skills — hardened fork

94 Blender art-direction and production skills, forked from
[`arjun988/blender-skills`](https://github.com/arjun988/blender-skills) (MIT, v1.3.0)
and rebuilt so the pack actually holds up in use.

The upstream pack is a good idea with a structural problem: it is a catalogue of
titles. This fork fixes the four things that made it unreliable, then keeps the
catalogue.

## What was wrong, and what changed

### 48 of 95 skills were a title and one sentence

`frutiger-aero-style` was, in full, a heading and the line *"Glossy bubbles. Fresh
greens/blues. Nature + tech optimism. Soft skeuomorphic forms."* A model loading
that skill learns three adjectives and no decisions. The same was true of all
eighteen `genre-*` skills, every horror style, every 2D style, and the world packs.

**48 skills rewritten** with a structure that forces decisions:

| section | what it settles |
| --- | --- |
| Read this before you touch the scene | the three questions the skill exists to answer |
| Direction | the actual art-direction rules, specific enough to violate |
| Numbers | default values — light ratios, texel density, cover heights, dims |
| Failure modes | how this direction usually gets lost |
| Checklist | what to verify against the finished scene, not the intent |

`frutiger-aero-style` now specifies roughness 0.08–0.18 with clearcoat, IOR
1.35–1.45 for the aqua glass, a 10–30 mm bevel radius, and names the failure —
*a matte frutiger surface is a different style*. Every genre skill carries the
numbers that decide whether the level works: cover ladder 0.9 / 1.35 / 2.1 m,
crouch eye at 1.1 m, arena radius 14–22 m, telegraph ≥ 0.4 s.

### The same 269 files existed twice

`.claude/skills` and `.cursor/skills` were byte-identical copies. Every edit had to
be made twice or the tools silently diverged. There is now one canonical tree,
`skills/`, and `build.py` materialises the per-tool copies. `build.py --check`
fails if a copy has drifted.

### 94 skills and not one of them pinned the Blender API

Two mentioned a version. One mentioned `bpy`. Blender 4.0 renamed every Principled
BSDF socket (`Specular` → `Specular IOR Level`, `Clearcoat` → `Coat Weight`),
4.1 removed `use_auto_smooth`, and 4.2 replaced Eevee with Eevee Next and Filmic
with AgX. An agent following these skills on 4.x does the wrong thing and gets no
error.

`shared/references/blender-version-contract.md` is now linked from **all 94 skills**:
socket names by name and checked for existence, engine written explicitly, view
transform stated, auto-smooth replaced with Weighted Normal, and the version stamped
into the validation note so a scene is reproducible.

### Two structural defects

- `blender-director` had **two `role:` keys** in its frontmatter. A YAML loader
  keeps the last, so the orchestrator silently claimed `role: orchestrator` and
  dropped `role: specialist`. One key now.
- `dream-weirdcore-style` pointed `related-skills` at `surreal-mood`, which does not
  exist. Points at `dream-surreal-mood`.
- A `references/` directory with no `SKILL.md` sat inside the skills tree, so the
  loader had to special-case a directory that looks like a skill and is not one.
  Moved to `shared/references/` and all 13 referrers updated.

## Validation

```
$ python3 validate.py
PASS  94 skills · frontmatter, refs, links, related-skills, API contract
```

`validate.py` checks, without dependencies:

- every skill directory has a `SKILL.md` with `name` and `description`
- `name` matches the directory
- body is at least 40 non-blank lines (the anti-stub floor)
- every `related-skills` entry resolves to a real skill
- every relative markdown link resolves
- the Blender API contract is pinned
- no duplicate frontmatter keys

Both scripts are dependency-free and CI-ready. `validate.py --quiet` is exit-code
only.

## Layout

```
skills/                       canonical tree — edit here
shared/references/            nine shared references + the API contract
build.py                      materialise .claude/skills and .cursor/skills
validate.py                   structural checks
.claude-plugin/               plugin + marketplace manifests (v1.4.0)
UPSTREAM-README.md            the original readme, kept verbatim
```

## Install

**Claude Code**
```bash
cp -r skills/* /path/to/project/.claude/skills/
```

**Cursor**
```bash
cp -r skills/* /path/to/project/.cursor/skills/
```

**Kiro / Codex**
```bash
cp -r skills/* /path/to/<tool>/skills/
```

Or run `python3 build.py` and use the generated `.claude/skills` / `.cursor/skills`.

## Scope and credit

The art direction — the 94 skill subjects, the shared references, the MCP protocol —
is upstream's work, MIT licensed and credited in `LICENSE` and `UPSTREAM-README.md`.
This fork contributes the rewritten skill bodies, the shared reference layout, the
API contract, and the two build scripts.
