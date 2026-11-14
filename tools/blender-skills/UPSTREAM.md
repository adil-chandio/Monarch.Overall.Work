# Upstream, and what changed here

- Source: https://github.com/arjun988/blender-skills
- Commit vendored: `904f095d8f36a6e72adaebb08d07f884a074743d` (2026-11-06, v1.3.0)
- Licence: MIT (see `LICENSE`) — kept verbatim, including the copyright line.
- Vendored: 94 skills, 175 reference files, the site and docs.

## Modifications in this repo

1. **`blender-director/references/mcp-integration.md` and every "executes directly in
   Blender via MCP" claim.** Upstream requires a desktop Blender with a BlenderMCP
   server on `localhost:9876`. This repo has no GUI, so the claim did not hold. The
   execution path is documented in `../../blender_local/BLENDER_LOCAL.md` (headless
   `bpy` + Cycles CPU), and the skills are used as **direction**, not as an executor.
2. **`.mcp.json` is left as upstream shipped it** (it is inert without a server); do not
   read it as a statement that MCP is connected here.
3. No skill text was rewritten. If a future pass edits a `SKILL.md`, say so here.

## Syncing

Upstream updates are pulled by re-cloning and diffing against the recorded commit:

```bash
git clone --depth 1 https://github.com/arjun988/blender-skills /tmp/bs
diff -rq /tmp/bs/.claude/skills tools/blender-skills/.claude/skills
```
