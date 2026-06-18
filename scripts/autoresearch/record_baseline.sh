#!/usr/bin/env bash
# Record baseline from measure.sh into .auto/log.jsonl (first-run helper).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Running baseline measure (2× median build)..."
output=$(./.auto/measure.sh)
echo "$output"

mcaddon_kb=$(echo "$output" | awk -F= '/^METRIC mcaddon_kb=/{print $2}')
build_sec=$(echo "$output" | awk -F= '/^METRIC build_sec=/{print $2}')
texture_count=$(echo "$output" | awk -F= '/^METRIC texture_count=/{print $2}')
barn_sim=$(echo "$output" | awk -F= '/^METRIC barn_sim_ok=/{print $2}')
validate_ok=$(echo "$output" | awk -F= '/^METRIC validate_ok=/{print $2}')

echo "Running checks..."
./.auto/checks.sh

python3 scripts/autoresearch/log_experiment.py \
  --metric "$mcaddon_kb" \
  --status keep \
  --description "Baseline measurement" \
  --metrics "{\"build_sec\":$build_sec,\"texture_count\":$texture_count,\"barn_sim_ok\":$barn_sim,\"validate_ok\":$validate_ok}"

python3 scripts/autoresearch/summarize.py
