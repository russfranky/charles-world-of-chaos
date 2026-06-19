#!/usr/bin/env bash
# Backpressure checks — run after every passing benchmark before logging status=keep.
# Pattern from pi-autoresearch .auto/checks.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 variants/ultimate-chaos-pack/scripts/simulate_barn.py
python3 variants/ultimate-chaos-pack/scripts/validate_pack.py
python3 variants/ultimate-chaos-pack/scripts/validate_marketplace.py
python3 scripts/validate_mob_approvals.py
python3 scripts/validate_world_scaffold.py
