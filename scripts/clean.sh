#!/usr/bin/env bash
# Remove local build artifacts (dist/ is committed for release installs).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VARIANT="$ROOT/variants/sunlit-diorama"

echo "Removing build outputs..."
rm -rf \
  "$VARIANT/build" \
  "$VARIANT/Sunlit_Diorama.mcpack" \
  "$ROOT/download/diorama_mc_output"

echo "Clean complete. Rebuild with: ./scripts/build_pack.sh"
