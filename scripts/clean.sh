#!/usr/bin/env bash
# Remove local build artifacts (dist/ is committed for release installs).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VARIANT="$ROOT/variants/lcgo-diorama"

echo "Removing build outputs..."
rm -rf \
  "$VARIANT/build" \
  "$VARIANT/Lara_Croft_GO_Diorama.mcpack" \
  "$ROOT/download/lcgo_mc_output"

echo "Clean complete. Rebuild with: ./scripts/build_pack.sh"
