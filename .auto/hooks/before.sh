#!/usr/bin/env bash
# After N consecutive discards, suggest a structural rethink (from pi-autoresearch anti-thrash).
set -euo pipefail

readonly WINDOW_SIZE=5
readonly STREAK_THRESHOLD=5

recent_discard_count() {
  jq -c 'select(.run != null and (.type // null) != "hook")' "$1" 2>/dev/null \
    | tail -n "$WINDOW_SIZE" \
    | jq -r 'select(.status == "discard") | .run' \
    | wc -l | tr -d ' '
}

thrash_suggestions() {
  echo "⚠️ $1 consecutive discards on cow pack. Consider:"
  echo "  - Re-read .auto/prompt.md and measure.sh secondary metrics"
  echo "  - Try a different subsystem (textures vs JS vs build staging)"
  echo "  - Run: python3 scripts/autoresearch/summarize.py"
}

input="$(cat)"
cwd="$(jq -r '.cwd' <<<"$input")"
jsonl="$cwd/.auto/log.jsonl"

[[ -f "$jsonl" ]] || exit 0
streak=$(recent_discard_count "$jsonl")
[[ "$streak" -lt "$STREAK_THRESHOLD" ]] && exit 0
thrash_suggestions "$streak"
