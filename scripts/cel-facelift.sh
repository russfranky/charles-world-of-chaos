#!/usr/bin/env bash
# Venice AI cel/toon texture facelift — requires VENICE_API_KEY in .env or environment.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

if [[ -z "${VENICE_API_KEY:-}" && -z "${VENICE_INFERENCE_KEY:-}" ]]; then
  echo "Error: set VENICE_API_KEY in .env or environment" >&2
  echo "  cp .env.example .env   # then edit with your Venice inference key" >&2
  exit 1
fi

export VENICE_TEXTURES=1
exec "$ROOT/scripts/build-mcaddon.sh" --venice-force
