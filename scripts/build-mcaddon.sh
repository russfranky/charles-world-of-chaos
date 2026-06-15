#!/usr/bin/env bash
# Build the unified Brindal & Grayson Cow World add-on
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
CHAOS="$ROOT/variants/ultimate-chaos-pack"

mkdir -p "$DIST"

echo "=============================================="
echo " Brindal & Grayson Cow World — unified build"
echo "=============================================="

if [[ ! -d "$ROOT/behavior_packs/brindal_grayson_cow_bp" ]]; then
  echo "Error: Custom cow source packs missing in behavior_packs/ and resource_packs/" >&2
  exit 1
fi

if [[ -f "$ROOT/requirements.txt" ]]; then
  pip3 install -r "$ROOT/requirements.txt" -q 2>/dev/null || true
fi

VENICE_FLAG=""
if [[ "${VENICE_TEXTURES:-}" == "1" ]]; then
  if [[ -n "${VENICE_API_KEY:-}" || -n "${VENICE_INFERENCE_KEY:-}" ]]; then
    echo "VENICE_TEXTURES=1: generating featured AI textures"
    VENICE_FLAG="--venice"
  else
    echo "Warning: VENICE_TEXTURES=1 but no API key set — skipping texture generation" >&2
  fi
fi

VENICE_AUDIO_FLAG=""
if [[ "${VENICE_AUDIO:-}" == "1" ]]; then
  if [[ -n "${VENICE_API_KEY:-}" || -n "${VENICE_INFERENCE_KEY:-}" ]]; then
    echo "VENICE_AUDIO=1: generating batch-1 AI audio"
    VENICE_AUDIO_FLAG="--venice-audio"
  else
    echo "Warning: VENICE_AUDIO=1 but no API key set — skipping audio generation" >&2
  fi
fi

python3 "$CHAOS/scripts/build_all.py" --rebuild-textures $VENICE_FLAG $VENICE_AUDIO_FLAG

echo ""
echo "Updating mob index for approval..."
python3 "$ROOT/scripts/generate_mob_index.py"
python3 "$ROOT/scripts/validate_mob_approvals.py"

echo ""
echo "=============================================="
echo " Build complete — dist/"
ls -lh "$DIST"/brindal-grayson-cow-pack.mcaddon "$DIST"/brindal-grayson-cow-pack.mcpack 2>/dev/null || ls -lh "$DIST"/
echo "=============================================="
echo ""
echo "  brindal-grayson-cow-pack.mcaddon — full add-on (chaos + Brindal & Grayson cows)"
echo "  brindal-grayson-cow-pack.mcpack  — visual-only (no behavior/scripts)"
