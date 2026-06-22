#!/usr/bin/env bash
# Bump semver, build, validate, commit dist, tag, and GitHub-release.
# Used by .github/workflows/publish.yml on every merge to main.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMMIT_MSG="[automated release]"

if [[ "${SKIP_BUMP:-}" != "1" ]]; then
  echo "Bumping pack patch version..."
  python3 variants/lcgo-diorama/scripts/pack_version.py --bump-patch
fi

VERSION="$(python3 variants/lcgo-diorama/scripts/pack_version.py --print semver)"
TAG="$(python3 variants/lcgo-diorama/scripts/pack_version.py --print tag)"
LABEL="$(python3 variants/lcgo-diorama/scripts/pack_version.py --print label)"

echo "Building ${LABEL}..."
./scripts/build_pack.sh

echo "Validating..."
python3 scripts/validate_pack.py

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

git add variants/lcgo-diorama/VERSION dist/ download/
if git diff --staged --quiet; then
  echo "Nothing to commit after build — skipping release push."
  exit 0
fi

git commit -m "Release ${TAG} ${COMMIT_MSG}

Automated pack publish: manifest ${LABEL}, dist artifacts refreshed."

git tag -a "${TAG}" -m "Lara Croft GO Diorama ${TAG}"

git push origin HEAD:main
git push origin "${TAG}"

gh release create "${TAG}" \
  --title "Lara Croft GO Diorama ${TAG}" \
  --notes "Install \`Lara_Croft_GO_Diorama.mcpack\` on Minecraft Bedrock 1.21+.

Activate under **Settings → Global Resources** (or per-world resource packs).

**Download:** attached \`.mcpack\` resource pack." \
  dist/Lara_Croft_GO_Diorama.mcpack

echo "Published ${TAG}"
