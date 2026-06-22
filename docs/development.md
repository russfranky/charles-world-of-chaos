# Development

## Prerequisites

- Python 3.11+
- `pip install -r requirements.txt` (Pillow for texture generation)

## Build pipeline

```bash
./scripts/build_pack.sh
```

This script:

1. Runs `lcgo_mc_tool.py --mode all` into `variants/lcgo-diorama/build/`
2. Copies `Lara_Croft_GO_Diorama.mcpack` to `dist/` and `download/`
3. Syncs tool output (`sample_level.json`, `.setblock`, `lcgo_mc_output/`) to `download/`

Validate:

```bash
python3 scripts/validate_pack.py
```

## Generator modes

```bash
TOOL=variants/lcgo-diorama/scripts/lcgo_mc_tool.py

# Full pipeline (textures + pack + sample conversion)
python3 $TOOL --mode all --output variants/lcgo-diorama/build

# Textures only — iterate on PALETTE
python3 $TOOL --mode textures --output variants/lcgo-diorama/build

# Assemble .mcpack from existing build dir
python3 $TOOL --mode pack --output variants/lcgo-diorama/build

# Convert custom level JSON
python3 $TOOL --mode convert --level my_level.json --origin 100,64,200 \
  --output variants/lcgo-diorama/build
```

## Level JSON format

Levels are JSON objects with a `tiles` array. Each tile has:

- `x`, `z` — grid coordinates
- `y` — height offset (optional, default 0)
- `type` — one of the LC GO tile types defined in the voxel spec (e.g. `floor_lit`, `wall_shadow`, `water_mid`)

See `variants/lcgo-diorama/levels/sample_level.json` and `download/Lara_Croft_GO_MC_Voxel_Spec.pdf`.

## Versioning and release

- Semver lives in `variants/lcgo-diorama/VERSION`
- `variants/lcgo-diorama/scripts/pack_version.py --bump-patch` increments patch
- Merge to `main` triggers automated publish via `.github/workflows/publish.yml`

## Project structure

```
variants/lcgo-diorama/
  VERSION
  README.md
  levels/sample_level.json
  scripts/
    lcgo_mc_tool.py    # generator + converter
    pack_version.py    # semver helper
dist/
  Lara_Croft_GO_Diorama.mcpack
download/              # release bundle (PDFs, tool, sample outputs)
scripts/
  build_pack.sh
  validate_pack.py
  publish_pack.sh
```

## Local Minecraft testing

After building, import `dist/Lara_Croft_GO_Diorama.mcpack` into Bedrock and activate global resources. For rapid iteration, run `--mode textures` then `--mode pack` without a full `--mode all` conversion pass.
