#!/usr/bin/env bash
# Benchmark for pi-autoresearch — outputs METRIC name=value lines.
# Runs two full builds and reports median mcaddon_kb / build_sec (fast noisy benchmark pattern).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Fast pre-check (<1s)
python3 -m py_compile \
  variants/ultimate-chaos-pack/scripts/texture_polish.py \
  variants/ultimate-chaos-pack/scripts/simulate_barn.py \
  variants/ultimate-chaos-pack/scripts/validate_pack.py \
  2>/dev/null

MCADDON="$ROOT/dist/brindal-grayson-cow-pack.mcaddon"
RUNS=2
sizes=()
times=()

for i in $(seq 1 "$RUNS"); do
  start=$(date +%s.%N)
  ./scripts/build-mcaddon.sh >/tmp/autoresearch-build-"$i".log 2>&1
  end=$(date +%s.%N)
  elapsed=$(awk -v s="$start" -v e="$end" 'BEGIN { printf "%.2f", e - s }')
  times+=("$elapsed")
  bytes=$(stat -c%s "$MCADDON")
  kb=$(awk -v b="$bytes" 'BEGIN { printf "%.2f", b / 1024 }')
  sizes+=("$kb")
done

median_of() {
  printf '%s\n' "$@" | sort -n | awk '
    { a[NR]=$1 }
    END {
      if (NR==0) { print 0; exit }
      if (NR%2) print a[(NR+1)/2]
      else print (a[NR/2] + a[NR/2+1]) / 2
    }'
}

MCADDON_KB=$(median_of "${sizes[@]}")
BUILD_SEC=$(median_of "${times[@]}")

MUSIC_KB=0
MUSIC_FILE="$ROOT/variants/ultimate-chaos-pack/pack/sounds/music/menu/Bell_At_Twilight.ogg"
if [[ -f "$MUSIC_FILE" ]]; then
  MUSIC_BYTES=$(stat -c%s "$MUSIC_FILE")
  MUSIC_KB=$(awk -v b="$MUSIC_BYTES" 'BEGIN { printf "%.2f", b / 1024 }')
fi

TEXTURE_COUNT=0
if [[ -d "$ROOT/variants/ultimate-chaos-pack/pack/textures" ]]; then
  TEXTURE_COUNT=$(find "$ROOT/variants/ultimate-chaos-pack/pack/textures" -name '*.png' | wc -l | tr -d ' ')
fi

BARN_SIM_OK=0
if python3 variants/ultimate-chaos-pack/scripts/simulate_barn.py >/dev/null 2>&1; then
  BARN_SIM_OK=1
fi

VALIDATE_OK=0
if python3 variants/ultimate-chaos-pack/scripts/validate_pack.py >/dev/null 2>&1; then
  VALIDATE_OK=1
fi

echo "METRIC mcaddon_kb=$MCADDON_KB"
echo "METRIC build_sec=$BUILD_SEC"
echo "METRIC music_kb=$MUSIC_KB"
echo "METRIC texture_count=$TEXTURE_COUNT"
echo "METRIC barn_sim_ok=$BARN_SIM_OK"
echo "METRIC validate_ok=$VALIDATE_OK"
