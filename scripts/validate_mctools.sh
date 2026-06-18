#!/usr/bin/env bash
# Run Microsoft Minecraft Creator Tools (MCTools) cooperative add-on validation.
# Gracefully skips when Node/npx or npm network fetch is unavailable (CI-safe).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MCADDON="$ROOT/dist/brindal-grayson-cow-pack.mcaddon"
MCTOOLS=(npx --yes @minecraft/creator-tools)
OUT="$ROOT/out/mctools-validate"

skip() {
  echo "SKIP: MCTools not available — $1"
  exit 0
}

if [[ ! -f "$MCADDON" ]]; then
  echo "Building pack (missing dist/brindal-grayson-cow-pack.mcaddon)..."
  "$ROOT/scripts/build-mcaddon.sh"
fi

if ! command -v node >/dev/null 2>&1; then
  skip "Node.js not installed"
fi

if ! command -v npx >/dev/null 2>&1; then
  skip "npx not found"
fi

echo "Ensuring @minecraft/creator-tools is reachable..."
if ! "${MCTOOLS[@]}" -v >/dev/null 2>&1; then
  skip "could not run @minecraft/creator-tools (network or npm issue)"
fi

mkdir -p "$OUT"

echo "Running MCTools cooperative add-on validation on: $MCADDON"
echo "Command: ${MCTOOLS[*]} --if \"$MCADDON\" -o \"$OUT\" --offline --yes validate addon"
echo ""

set +e
"${MCTOOLS[@]}" \
  --if "$MCADDON" \
  -o "$OUT" \
  --offline \
  --yes \
  validate addon
code=$?
set -e

if [[ $code -eq 0 ]]; then
  echo ""
  echo "MCTools: PASS — cooperative add-on validation"
  exit 0
fi

echo ""
echo "MCTools: FAIL (exit $code) — see errors above; HTML report in $OUT/"
exit 1
