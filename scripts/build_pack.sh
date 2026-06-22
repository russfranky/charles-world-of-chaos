#!/usr/bin/env bash
# Build Sunlit Diorama resource pack and refresh distributables.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VARIANT="$ROOT/variants/sunlit-diorama"
TOOL="$VARIANT/scripts/diorama_mc_tool.py"
BUILD="$VARIANT/build"
DIST="$ROOT/dist"
DOWNLOAD="$ROOT/download"

mkdir -p "$BUILD" "$DIST" "$DOWNLOAD"

echo "=============================================="
echo " Sunlit Diorama — build"
echo "=============================================="

if [[ -f "$ROOT/requirements.txt" ]]; then
  pip3 install -r "$ROOT/requirements.txt" -q 2>/dev/null || true
fi

rm -rf "$BUILD"
mkdir -p "$BUILD"

python3 "$TOOL" --mode all --output "$BUILD"

PACK_SRC="$DOWNLOAD/Sunlit_Diorama.mcpack"
if [[ ! -f "$PACK_SRC" ]]; then
  echo "Error: expected pack at $PACK_SRC" >&2
  exit 1
fi

cp "$PACK_SRC" "$DIST/Sunlit_Diorama.mcpack"
cp "$TOOL" "$DOWNLOAD/diorama_mc_tool.py"
if [[ -f "$BUILD/sample_level.setblock" ]]; then
  cp "$BUILD/sample_level.setblock" "$DOWNLOAD/sample_level.setblock"
fi
rm -rf "$DOWNLOAD/diorama_mc_output"
cp -r "$BUILD" "$DOWNLOAD/diorama_mc_output"

echo ""
echo "=============================================="
echo " Build complete"
ls -lh "$DIST/Sunlit_Diorama.mcpack"
echo "=============================================="
