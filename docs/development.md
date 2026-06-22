# Development

## Prerequisites

- Python 3.11+
- `pip install -r requirements.txt` (Pillow for texture generation)

## Build pipeline

```bash
./scripts/build_pack.sh
```

This script:

1. Runs `diorama_mc_tool.py --mode all` into `variants/sunlit-diorama/build/`
2. Copies `Sunlit_Diorama.mcpack` to `dist/` and `download/`
3. Syncs tool output (`sample_level.json`, `.setblock`, `diorama_mc_output/`) to `download/`

Validate:

```bash
python3 scripts/validate_pack.py
```

## Generator modes

```bash
TOOL=variants/sunlit-diorama/scripts/diorama_mc_tool.py

# Full pipeline (textures + pack + sample conversion)
python3 $TOOL --mode all --output variants/sunlit-diorama/build

# Textures only — iterate on PALETTE
python3 $TOOL --mode textures --output variants/sunlit-diorama/build

# Assemble .mcpack from existing build dir
python3 $TOOL --mode pack --output variants/sunlit-diorama/build

# Convert custom level JSON
python3 $TOOL --mode convert --level my_level.json --origin 100,64,200 \
  --output variants/sunlit-diorama/build
```

## Level JSON format

Levels are JSON objects with a `tiles` array. Each tile has:

- `x`, `z` — grid coordinates
- `y` — height offset (optional, default 0)
- `type` — one of the tile types defined in the voxel spec (e.g. `floor_lit`, `wall_shadow`, `water_mid`)

See `variants/sunlit-diorama/levels/sample_level.json` and `download/Voxel_Spec.pdf`.

## Versioning and release

- Semver lives in `variants/sunlit-diorama/VERSION`
- `variants/sunlit-diorama/scripts/pack_version.py --bump-patch` increments patch
- Merge to `main` triggers automated publish via `.github/workflows/publish.yml`

## Project structure

```
variants/sunlit-diorama/
  VERSION
  README.md
  levels/sample_level.json
  scripts/
    diorama_mc_tool.py    # generator + converter
    pack_version.py       # semver helper
dist/
  Sunlit_Diorama.mcpack
download/                 # release bundle (PDF, tool, sample outputs)
scripts/
  build_pack.sh
  validate_pack.py
  publish_pack.sh
```

## Local Minecraft testing

After building, import `dist/Sunlit_Diorama.mcpack` into Bedrock and activate global resources. For rapid iteration, run `--mode textures` then `--mode pack` without a full `--mode all` conversion pass.
