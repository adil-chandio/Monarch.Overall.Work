#!/usr/bin/env bash
# Find a skill by keyword across every vendored pack.
#   ./scripts/find-skills.sh thumbnail
#   ./scripts/find-skills.sh "voice clone" --space yt-automation
set -euo pipefail
term="${1:?usage: find-skills.sh <keyword> [--space <id>]}"
space=""
if [[ "${2:-}" == "--space" ]]; then space="${3:-}"; fi
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -n "$space" ]]; then
  jq -r --arg s "$space" --arg t "$term" \
    '.entries[] | select(.space==$s) | select((.name+" "+.path)|ascii_downcase|contains($t|ascii_downcase)) | "\(.space)\t\(.pack)\t\(.name)\t\(.path)"' \
    "$root/docs/repo-intel/skills-index.json"
else
  jq -r --arg t "$term" \
    '.entries[] | select((.name+" "+.path)|ascii_downcase|contains($t|ascii_downcase)) | "\(.space)\t\(.pack)\t\(.name)\t\(.path)"' \
    "$root/docs/repo-intel/skills-index.json"
fi | head -40
# fallback: search skill bodies when no name/path matched
if [[ -z "$(jq -r --arg t "$term" '[.entries[]|select((.name+" "+.path)|ascii_downcase|contains($t|ascii_downcase))]|length' "$root/docs/repo-intel/skills-index.json")" || "$(jq -r --arg t "$term" '[.entries[]|select((.name+" "+.path)|ascii_downcase|contains($t|ascii_downcase))]|length' "$root/docs/repo-intel/skills-index.json")" == "0" ]]; then
  echo "--- no name match; files whose body mentions \"$term\" ---"
  grep -ril "$term" "$root/skills" --include=SKILL.md | sed "s|$root/||" | head -25
fi
