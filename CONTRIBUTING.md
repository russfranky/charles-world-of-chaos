# Contributing

Thank you for improving **Lara Croft GO Diorama** for Minecraft Bedrock.

## Repository layout

| Path | Role |
|------|------|
| `variants/lcgo-diorama/scripts/lcgo_mc_tool.py` | Texture generator, pack assembler, voxel converter |
| `variants/lcgo-diorama/levels/` | Sample LC GO level JSON |
| `variants/lcgo-diorama/VERSION` | Pack semver (bumped on release) |
| `dist/` | Committed distributable `.mcpack` |
| `download/` | Release bundle mirrored from builds |

## Build and validate

```bash
pip3 install -r requirements.txt
./scripts/build_pack.sh
python3 scripts/validate_pack.py
./scripts/clean.sh   # remove local build dirs only
```

`./scripts/build_pack.sh` regenerates textures, assembles the `.mcpack`, and refreshes `dist/` and `download/`.

## Conventions

- **Palette changes** — edit `PALETTE` and tile mappings in `lcgo_mc_tool.py`, then rebuild.
- **Pack UUID** — do not change manifest UUIDs after a public release (in-place updates depend on them).
- **Versioning** — `variants/lcgo-diorama/VERSION` follows semver; `publish.yml` bumps patch on merge to `main`.
- **Pre-commit** — `pip install -r requirements.txt && pre-commit install`

## Pull requests

1. Run `./scripts/build_pack.sh` and `python3 scripts/validate_pack.py`.
2. Include a short description of palette, level, or tooling changes.
3. Attach in-game screenshots when texture output changes.

## Issues

Open a [GitHub Issue](https://github.com/russfranky/charles-world-of-chaos/issues) with Minecraft version, platform, and steps to reproduce.
