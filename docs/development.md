# Development Guide — Charles' World of Chaos

This repo builds **Charles' World of Chaos** — one unified Bedrock add-on shipped as `dist/brindal-grayson-cow-pack.mcaddon`. See [installation.md](installation.md) for iPad setup.

> **Naming:** Product/brand = **Charles' World of Chaos**. GitHub repo slug and release filenames stay `brindal-grayson-cow-pack` for URL stability. Internal source folders (`brindal_grayson_cow_*`) are legacy paths.

## Repository layout

| Path | Purpose |
|------|---------|
| `resource_packs/brindal_grayson_cow_rp/` | Custom cow RP source (Spot/Storm) — merged at build |
| `behavior_packs/brindal_grayson_cow_bp/` | Custom cow BP source — merged at build |
| `variants/ultimate-chaos-pack/scripts/` | Main build pipeline |
| `variants/ultimate-chaos-pack/gui_overrides/` | Cow GUI textures/JSON/lang source (applied at build) |
| `variants/ultimate-chaos-pack/prompts/` | Venice AI texture manifest |
| `variants/ultimate-chaos-pack/VERSION` | Shipped semver (auto-bumped on merge to `main`) |
| `dist/` | Shipped `.mcaddon` / `.mcpack` (refreshed by publish workflow) |

Build outputs (`pack/`, `behavior_pack/`, `vanilla_src/`) are gitignored. Run `./scripts/clean.sh` to remove them.

## Build

```bash
pip3 install -r requirements.txt
./scripts/build-mcaddon.sh
```

### Automated releases

Every merge to **`main`** runs [`.github/workflows/publish.yml`](../.github/workflows/publish.yml):

1. Bump patch in `variants/ultimate-chaos-pack/VERSION`
2. Build + validate
3. Commit `VERSION` + `dist/`
4. Tag `vX.Y.Z` and create a [GitHub Release](https://github.com/russfranky/brindal-grayson-cow-pack/releases) with `.mcaddon` / `.mcpack` attached

**Do not** hand-edit `VERSION` or `dist/` in PRs — the bot owns those on `main`. Manifest names read version from `VERSION` via `pack_version.py`.

**Kid install link (always latest):**  
`https://github.com/russfranky/brindal-grayson-cow-pack/releases/latest/download/brindal-grayson-cow-pack.mcaddon`

Local dry-run (no git push):

```bash
python3 variants/ultimate-chaos-pack/scripts/pack_version.py --bump-patch
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
cowify_kid_textures.py       → baked grass/dirt/bread + Feed Bag + Ranch Bell icons
merge_custom_cows.py         → overlay custom cows + menu music
Texture polish pipeline (`texture_polish.py`, `polish_textures.py`) — post-process PNGs:
alpha cleanup → quantize → **cel/toon band bake** (luminance steps, optional ink outline) → despeckle → edge snap. All shading is baked at build time; no in-game shaders.
apply_audio_overrides.py     → menu music sound_definitions
venice_generate_textures.py  → optional AI art (--venice), downscale + polish
polish_textures.py           → alpha cleanup, quantize, despeckle all pack PNGs
optimize_audio.py            → lite menu music re-encode (ffmpeg)
optimize_pngs.py             → lossless PNG squeeze
package_mcaddon.py           → dist/
```

Texture polish (`texture_polish.py`) runs after Venice/cowify: cel/toon luminance bands + optional ink outlines baked into PNGs (no runtime shaders).

## Autoresearch loop (pi-autoresearch)

Measure → keep improvements → revert regressions. See [`.auto/README.md`](../.auto/README.md).

```bash
./.auto/measure.sh              # METRIC mcaddon_kb=… (median of 2 builds)
./.auto/checks.sh               # barn sim + validate + branding + QA registry
python3 qa/run_qa_suite.py      # updates qa/QUALITY_REGISTRY.csv
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
