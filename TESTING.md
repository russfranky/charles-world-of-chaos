# Testing Guide — Sunlit Diorama

## Automated (Linux CI)

| Check | Command | Notes |
|-------|---------|-------|
| Build completes | `./scripts/build_pack.sh` | Regenerates pack and download bundle |
| Pack structure | `python3 scripts/validate_pack.py` | Manifest, icon, min engine version |
| Sample level | `validate_pack.py` | ≥ 35 tiles in `sample_level.json` |
| Pack size | `validate_pack.py` | `.mcpack` ≥ 5 KB |

CI runs on every pull request to `main` and uploads `dist/Sunlit_Diorama.mcpack` as an artifact.

## Manual (in-game)

CI cannot run Minecraft Bedrock. Verify on a device after texture or manifest changes:

1. Import `dist/Sunlit_Diorama.mcpack`.
2. Activate under **Settings → Global Resources**.
3. Create or open a creative world (Bedrock 1.21+).
4. Confirm:
   - [ ] `stone`, `calcite`, `deepslate`, `bedrock` show warm cel bands
   - [ ] Gold / emerald / copper blocks use relic palette
   - [ ] Pack appears in resource list with correct name and icon
5. Optional — paste sample build:
   - Run converter with `--origin` set to a clear area
   - Execute `sample_level.setblock` commands or `diorama_level.mcfunction` in-game

## Local commands

```bash
# Full rebuild
./scripts/build_pack.sh

# Validate only (after build)
python3 scripts/validate_pack.py

# Regenerate textures without repackaging
python3 variants/sunlit-diorama/scripts/diorama_mc_tool.py --mode textures \
  --output variants/sunlit-diorama/build

# Convert a custom level JSON
python3 variants/sunlit-diorama/scripts/diorama_mc_tool.py --mode convert \
  --level my_level.json --origin 0,100,0

# Clean local build dirs
./scripts/clean.sh
```

## Release path

Merges to `main` trigger `publish.yml`: patch bump → build → validate → commit `dist/` → GitHub Release with attached `.mcpack`.

Manual tag pushes can use `release.yml` for ad-hoc releases.
