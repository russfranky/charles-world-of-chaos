#!/usr/bin/env bash
# Full vanilla resource pack (~5k textures) + cel bake on every PNG + Venice hero art.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
CHAOS="$ROOT/variants/ultimate-chaos-pack"

mkdir -p "$DIST"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

echo "=============================================="
echo " Brindal & Grayson Cow World — FULL texture pack"
echo "=============================================="

if [[ ! -d "$ROOT/behavior_packs/brindal_grayson_cow_bp" ]]; then
  echo "Error: Custom cow source packs missing in behavior_packs/ and resource_packs/" >&2
  exit 1
fi

if [[ -f "$ROOT/requirements.txt" ]]; then
  pip3 install -r "$ROOT/requirements.txt" -q 2>/dev/null || true
fi

VENICE_FLAG=""
if [[ -n "${VENICE_API_KEY:-}" || -n "${VENICE_INFERENCE_KEY:-}" ]]; then
  echo "VENICE_API_KEY set — Venice cel facelift on all 67 manifest heroes"
  VENICE_FLAG="--venice"
else
  echo "Warning: no Venice API key — vanilla + cel polish only (no AI hero art)" >&2
fi

VENICE_FORCE_FLAG=""
if [[ "${VENICE_FORCE:-}" == "1" ]]; then
  VENICE_FORCE_FLAG="--venice-force"
fi

python3 "$CHAOS/scripts/build_all.py" --full --rebuild-textures $VENICE_FLAG $VENICE_FORCE_FLAG

echo ""
echo "Validating full pack..."
python3 "$CHAOS/scripts/validate_pack.py" --full

echo ""
echo "=============================================="
echo " Full build complete — dist/"
ls -lh "$DIST"/brindal-grayson-cow-pack-full.mcaddon "$DIST"/brindal-grayson-cow-pack-full.mcpack 2>/dev/null || ls -lh "$DIST"/
echo "=============================================="
echo ""
echo "  brindal-grayson-cow-pack-full.mcaddon — full RP (~5k cel-baked textures) + lite BP"
echo "  brindal-grayson-cow-pack-full.mcpack  — full resource pack only"
