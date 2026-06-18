# Development Guide

This repo builds **one unified add-on** — `dist/brindal-grayson-cow-pack.mcaddon`. See [installation.md](installation.md) for iPad setup.

## Repository layout

| Path | Purpose |
|------|---------|
| `resource_packs/brindal_grayson_cow_rp/` | Source for Brindal & Grayson custom cows (merged at build) |
| `behavior_packs/brindal_grayson_cow_bp/` | Behavior definitions for custom cows |
| `variants/ultimate-chaos-pack/scripts/` | Main build pipeline |
| `variants/ultimate-chaos-pack/gui_overrides/` | Cow GUI textures/JSON/lang source (applied at build) |
| `variants/ultimate-chaos-pack/prompts/` | Venice AI texture manifest |
| `dist/` | Shipped `.mcaddon` / `.mcpack` (committed for one-tap iPad install) |

Build outputs (`pack/`, `behavior_pack/`, `vanilla_src/`) are gitignored. Run `./scripts/clean.sh` to remove them.

## Build

```bash
pip3 install -r requirements.txt
./scripts/build-mcaddon.sh
```

With Venice AI featured textures (optional):

```bash
export VENICE_API_KEY='your-key'
./scripts/build-mcaddon.sh
```

## Custom cow source packs

### Resource pack (`resource_packs/brindal_grayson_cow_rp/`)

| Path | Purpose |
|------|---------|
| `entity/` | Client entity definitions (textures, animations) |
| `textures/entity/` | Cow texture PNG files |
| `texts/` | Localization |

### Behavior pack (`behavior_packs/brindal_grayson_cow_bp/`)

| Path | Purpose |
|------|---------|
| `entities/` | AI, health, breeding |
| `spawn_rules/` | Natural spawn conditions |
| `texts/` | Localization |

`merge_custom_cows.py` copies these into the built unified pack. **Do not install the source packs alone** — they lack the lite overlay textures, script API, and GUI.

## Adding a new cow variant

1. Create `behavior_packs/.../entities/new_cow.json` with identifier `bgcow:new_cow`
2. Create `resource_packs/.../entity/new_cow.entity.json`
3. Add texture at `resource_packs/.../textures/entity/new_cow.png`
4. Add spawn rules and lang strings
5. Register files in `merge_custom_cows.py` `RP_COPY` / `BP_COPY`
6. Add `bgcow:new_cow` to `COW_IDENTIFIERS` in `common.py` (exempt from transform)
7. Rebuild and test: `/summon bgcow:new_cow`

## Build pipeline

```
prepare_lite_pack.py         → stage only featured textures + custom cows
polish_textures.py --sources → polish Brindal/Grayson source PNGs
personalize_pack.py          → branding, manifests, B/G blocks
merge_custom_cows.py         → overlay custom cows + menu music
apply_gui_overrides.py       → subtitle JSON UI (minimal)
apply_audio_overrides.py     → menu music sound_definitions
venice_generate_textures.py  → optional AI art (--venice), downscale + polish
polish_textures.py           → alpha cleanup, quantize, despeckle all pack PNGs
optimize_pngs.py             → lossless PNG squeeze
package_mcaddon.py           → dist/
```

Texture polish (`texture_polish.py`) runs after Venice/downscale: alpha cleanup, palette quantize, Bayer dither, despeckle, edge-snap — similar to retro shader / 3D→pixel post pipelines (ditherpunk, hubzz-3d-pipeline).

## Autoresearch loop (pi-autoresearch)

Measure → keep improvements → revert regressions. See [`.auto/README.md`](../.auto/README.md).

```bash
./.auto/measure.sh              # METRIC mcaddon_kb=… (median of 2 builds)
./.auto/checks.sh               # barn sim + validate + mob approvals
python3 scripts/autoresearch/summarize.py
```

Works with [pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) in pi (`pi install npm:pi-autoresearch`).

## Local development workflow

### Option A: Development folders

Copy built packs after `./scripts/build-mcaddon.sh`:

```
variants/ultimate-chaos-pack/pack/          → development_resource_packs/
variants/ultimate-chaos-pack/behavior_pack/ → development_behavior_packs/
```

### Option B: Import `.mcaddon`

Rebuild and import `dist/brindal-grayson-cow-pack.mcaddon` into Minecraft.

## UUIDs

See [UUIDS.md](UUIDS.md). **Never change shipped UUIDs** after release.

## Useful commands

```
/summon bgcow:brindal_cow
/summon bgcow:grayson_cow
/bgcow:barn
/bgcow:breed
/bgcow:help
```

## References

- [Bedrock Wiki — Pack Structure](https://wiki.bedrock.dev/documentation/pack-structure)
- [Bedrock Wiki — JSON UI Best Practices](https://wiki.bedrock.dev/json-ui/best-practices)
- [Mojang Bedrock Samples](https://github.com/Mojang/bedrock-samples)
