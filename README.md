# Brindal & Grayson Cow Pack

Minecraft Bedrock Edition add-ons for **Brindal** (daughter) and **Grayson** (son) on iPad.

This repo contains **two add-ons** — pick the one that fits your play style:

| Add-on | File | Best for | What it does |
|--------|------|----------|--------------|
| **Custom Cows** | `dist/custom-cows.mcaddon` | **Kids / everyday play** | Adds Brindal Cow and Grayson Cow as friendly custom mobs. Vanilla game stays normal. |
| **Ultimate Chaos** | `dist/ultimate-chaos.mcaddon` | **Maximum silliness** | Cowifies *everything* — textures, sounds, mobs. Zombies become cows. Blocks look like cow hide. |

> **Recommendation for Brindal & Grayson:** Start with **Custom Cows**. Try Ultimate Chaos when you want total cow madness (needs experimental toggles).

## Quick Install (iPad)

### Custom Cows (recommended)

1. [Download custom-cows.mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/custom-cows.mcaddon)
2. Safari → tap download → **Open in Minecraft**
3. Create or edit a world → activate both packs
4. Find Brindal and Grayson cows in plains/forest biomes, or summon them:

```
/summon bgcow:brindal_cow
/summon bgcow:grayson_cow
```

### Ultimate Chaos

1. [Download ultimate-chaos.mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/ultimate-chaos.mcaddon)
2. Safari → **Open in Minecraft**
3. Create a **NEW** world with:
   - **Holiday Creator Features** ON
   - **Beta APIs** ON
4. Activate both resource and behavior packs

Visual-only fallback (no behavior/scripts): [ultimate-chaos.mcpack](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/ultimate-chaos.mcpack)

## Repository Structure

```
brindal-grayson-cow-pack/
├── resource_packs/brindal_grayson_cow_rp/   # Custom Cows — resource pack
├── behavior_packs/brindal_grayson_cow_bp/   # Custom Cows — behavior pack
├── variants/ultimate-chaos-pack/            # Ultimate Chaos — full pipeline
│   ├── scripts/                             #   build_all.py, cowify_*.py, etc.
│   ├── pack/                                #   built RP (gitignored)
│   └── behavior_pack/                       #   built BP (gitignored)
├── scripts/build-mcaddon.sh                 # Builds BOTH → dist/
├── dist/
│   ├── custom-cows.mcaddon                  # Custom Cows distributable
│   ├── ultimate-chaos.mcaddon               # Ultimate Chaos full add-on
│   └── ultimate-chaos.mcpack                # Ultimate Chaos visual-only
├── docs/                                    # Install & development guides
├── CONTRIBUTING.md
└── LICENSE
```

## Build from Source

```bash
pip3 install -r requirements.txt
./scripts/build-mcaddon.sh
```

This produces all three files in `dist/`. See [docs/installation.md](docs/installation.md) and [variants/ultimate-chaos-pack/README.md](variants/ultimate-chaos-pack/README.md) for details.

## Custom Cows — Entities

| Entity | Identifier | Description |
|--------|-----------|-------------|
| Brindal Cow | `bgcow:brindal_cow` | Brown cow with white spots — for Brindal |
| Grayson Cow | `bgcow:grayson_cow` | Gray cow with dark spots — for Grayson |

Both support milking, breeding, aging, and cross-breeding.

## Ultimate Chaos — Stats

- 4,600+ cow-hide textures (blocks, items, entities, GUI, UI)
- 170+ client entity overrides → all mobs look like cows
- 120+ behavior entities transform to cows on spawn
- Mob sounds redirected to cow moos
- Script API backup cowifier

## Requirements

- Minecraft Bedrock Edition 1.21.0+
- Custom Cows: no experiments required
- Ultimate Chaos: Holiday Creator Features + Beta APIs

## Ultimate Chaos — Venice AI textures (optional)

Featured mob/block/UI textures can be generated via [Venice AI](https://venice.ai) for higher-quality comedy art:

```bash
export VENICE_API_KEY='your-key'   # see .env.example — never commit keys
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --category entity
python3 variants/ultimate-chaos-pack/scripts/build_all.py --rebuild-textures --venice
```

See [VENICE_PROMPTS.md](VENICE_PROMPTS.md) for all prompts and model recommendations.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Use the `bgcow:` namespace for custom identifiers.

## License

MIT — see [LICENSE](LICENSE).
