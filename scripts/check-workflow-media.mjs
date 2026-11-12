#!/usr/bin/env node
/**
 * check-workflow-media.mjs — finds workflows that commit media to Git.
 *
 * This is the mechanism behind the repo's growth. 42 workflows run `git commit`.
 * 20 of them `git add production/extinct-life/<film>` (or an mp4 by name) — which sweeps inspection
 * stills and evidence frames straight into history on every run.
 *
 * A workflow that produces media should upload it (Actions artifact or Drive),
 * not commit it. This script measures the gap and reports it. It does not edit
 * workflows: each one has its own verification, and silently rewriting 20 of
 * them is how you break a pipeline that was working.
 *
 *   node scripts/check-workflow-media.mjs           # report
 *   node scripts/check-workflow-media.mjs --json    # machine-readable
 *   node scripts/check-workflow-media.mjs --strict  # exit 1 if any remain (for CI opt-in)
 */
import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");
const WF_DIR = resolve(ROOT, ".github/workflows");
const POLICY = JSON.parse(readFileSync(resolve(ROOT, "config/media-policy.json"), "utf8"));

const MEDIA_EXT = /\.(mp4|mov|webm|mkv|m4v|wav|mp3|flac|m4a|aac|ogg|opus|aiff|png|jpe?g|webp|gif|psd|exr|tif|tiff|blend|blend1|glb|gltf|fbx|obj|usd|usdz|zip|7z|bundle)$/i;

/** Folders that are known to hold media, so `git add <folder>` sweeps it in. */
const MEDIA_DIRS = [
  "production/extinct-life/review-v",
  "production/extinct-life/film-",
  "production/extinct-life/homotherium-short",
  "production/extinct-life/longform-mammoth",
  "public/thumbnails",
  "public/showreel",
  "public/proof",
  "docs/research/assets",
  "gpu-engine/keyframes",
];

const files = readdirSync(WF_DIR).filter((f) => f.endsWith(".yml") || f.endsWith(".yaml"));

const committing = [];
const mediaCommitting = [];
const perFile = new Map();

for (const file of files) {
  const text = readFileSync(resolve(WF_DIR, file), "utf8");
  const adds = [...text.matchAll(/git add\s+([^\n|&;]+)/g)].map((m) => m[1].trim());
  const commits = /git commit\b/.test(text);

  if (commits) committing.push(file);
  if (!adds.length) continue;

  const hits = [];
  for (const add of adds) {
    for (const token of add.split(/\s+/).filter(Boolean)) {
      const clean = token.replace(/^["']|["']$/g, "");
      const isMediaExt = MEDIA_EXT.test(clean);
      const isMediaDir = MEDIA_DIRS.some((d) => clean.startsWith(d));
      if (isMediaExt || isMediaDir) hits.push(clean);
    }
  }
  if (hits.length) {
    mediaCommitting.push(file);
    perFile.set(file, [...new Set(hits)]);
  }
}

/* ---------- report ---------- */

if (process.argv.includes("--json")) {
  console.log(JSON.stringify({
    total_workflows: files.length,
    workflows_that_commit: committing.length,
    workflows_that_commit_media: mediaCommitting.length,
    detail: Object.fromEntries(perFile),
  }, null, 2));
} else {
  const RED = "\x1b[31m", YEL = "\x1b[33m", GRN = "\x1b[32m", DIM = "\x1b[2m", RST = "\x1b[0m";
  console.log(`\nworkflow media audit — ${files.length} workflows\n`);
  console.log(`  run \`git commit\`                  ${committing.length}`);
  console.log(`  …and \`git add\` a media path      ${mediaCommitting.length}  ${mediaCommitting.length ? RED + "← these regrow the repo" + RST : GRN + "clean" + RST}`);
  console.log(`  policy said (2026-11-13)          ${POLICY.workflow_handoff?.count_now ?? "?"}\n`);

  if (mediaCommitting.length) {
    console.log(`${YEL}workflows that push media into Git${RST}`);
    for (const [file, paths] of [...perFile].sort()) {
      console.log(`  ${file}`);
      for (const p of paths.slice(0, 3)) console.log(`    ${DIM}git add ${p}${RST}`);
      if (paths.length > 3) console.log(`    ${DIM}… +${paths.length - 3} more paths${RST}`);
    }
    console.log(`
${DIM}fix per workflow: replace \`git add <media folder>\` with an upload step —
  actions/upload-artifact (keeps 90 days, free) or a Drive upload.
  Keep the JSON/CSV/MD outputs committed: those are the measurements.
  Never commit the frames.${RST}
`);
  }
}

if (process.argv.includes("--strict") && mediaCommitting.length > 0) {
  process.exit(1);
}
