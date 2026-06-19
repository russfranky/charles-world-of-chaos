#!/usr/bin/env bash
# Bump semver, build, validate, commit dist, tag, and GitHub-release.
# Used by .github/workflows/publish.yml on every merge to main.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMMIT_MSG="[automated release]"

if [[ "${SKIP_BUMP:-}" != "1" ]]; then
  echo "Bumping pack patch version..."
  python3 variants/ultimate-chaos-pack/scripts/pack_version.py --bump-patch
fi

VERSION="$(python3 variants/ultimate-chaos-pack/scripts/pack_version.py --print semver)"
TAG="$(python3 variants/ultimate-chaos-pack/scripts/pack_version.py --print tag)"
LABEL="$(python3 variants/ultimate-chaos-pack/scripts/pack_version.py --print label)"

echo "Building ${LABEL}..."
./scripts/build-mcaddon.sh

echo "Validating..."
./.auto/checks.sh

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

git add variants/ultimate-chaos-pack/VERSION dist/
if git diff --staged --quiet; then
  echo "Nothing to commit after build — skipping release push."
  exit 0
fi

git commit -m "Release ${TAG} ${COMMIT_MSG}

Automated pack publish: manifest ${LABEL}, dist artifacts refreshed."

git tag -a "${TAG}" -m "Brindal & Grayson Cow World ${TAG}"

git push origin HEAD:main
git push origin "${TAG}"

gh release create "${TAG}" \
  --title "Brindal & Grayson Cow World ${TAG}" \
  --notes "Install \`brindal-grayson-cow-pack.mcaddon\` on Bedrock — updates in place if you already have an older version (same pack UUID, higher semver).

**New world required for script changes:** Holiday Creator Features + Beta APIs ON, both packs active.

**Download:** attached \`.mcaddon\` (full add-on) or \`.mcpack\` (visuals only)." \
  dist/brindal-grayson-cow-pack.mcaddon \
  dist/brindal-grayson-cow-pack.mcpack

echo "Published ${TAG}"
