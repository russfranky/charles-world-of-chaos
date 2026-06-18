#!/usr/bin/env bash
# Append learnings that survive git revert (from pi-autoresearch learnings-journal).
set -euo pipefail

readonly LEARNINGS_FILE=".auto/learnings.md"

run_number()     { jq -r '.run_entry.run' <<<"$1"; }
run_status()     { jq -r '.run_entry.status' <<<"$1"; }
run_metric()     { jq -r '.run_entry.metric' <<<"$1"; }
run_hypothesis() { jq -r '.run_entry.asi.hypothesis // "-"' <<<"$1"; }
run_desc()       { jq -r '.run_entry.description // "-"' <<<"$1"; }

input="$(cat)"
file="$(jq -r '.cwd' <<<"$input")/$LEARNINGS_FILE"
mkdir -p "$(dirname "$file")"
printf '%s run=%s status=%s mcaddon_kb=%s | %s | hyp: %s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "$(run_number "$input")" \
  "$(run_status "$input")" \
  "$(run_metric "$input")" \
  "$(run_desc "$input")" \
  "$(run_hypothesis "$input")" >>"$file"
