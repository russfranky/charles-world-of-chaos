# Venice AI Prompts — "Everything Is Cow" Minecraft Skins

Prompts for generating Ultimate Chaos featured textures via [Venice AI](https://venice.ai). Used by `variants/ultimate-chaos-pack/scripts/venice_generate_textures.py`.

## Setup

```bash
export VENICE_API_KEY='your-venice-inference-key'
# or copy .env.example → .env and source it
```

**Never commit API keys.** Rotate your key if it was ever shared in chat.

## Model recommendations (June 2026)

| Venice Model | Use for | Why |
|--------------|---------|-----|
| `flux-2-pro` (FLUX) | Mob skins, blocks, items | Best prompt adherence, pixel grid, text |
| `venice-sd35` | Backup / alt style | Exact width×height sizing |
| `lustify-sdxl` | Cartoony cow variants | More whimsical comedy |
| `gpt-image-2` | Pack icon, panoramas | Great text rendering |

**Strategy:** Generate at 1024×1024, downscale with **nearest-neighbor** to 16/32/64/128/256/512. AI produces garbage at native 64×64.

Always append: *flat pixel art, hard edges, no anti-aliasing, no gradients, solid color blocks, Minecraft style*

## Usage

```bash
# List all texture IDs
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --list

# Generate featured mobs only
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --category entity

# Specific textures
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --id zombie,creeper,pack_icon

# Full Venice pass during build
python3 variants/ultimate-chaos-pack/scripts/build_all.py --rebuild-textures --venice
```

## Style anchor (generate first)

> A lineup of five Minecraft mobs (zombie, creeper, skeleton, spider, pig) all wearing ridiculous handmade cow costumes. Each costume is slightly different and badly fitting. They stand in a row on a Minecraft grass block stage. One holds a sign saying "We are ALL cows now."

Reference this output's palette and comedy tone for consistency.

## Mob entity textures (64×64 UV sheets)

See `variants/ultimate-chaos-pack/prompts/venice_prompts.json` for the machine-readable manifest with exact `pack_path` targets.

| Mob | Concept |
|-----|---------|
| Zombie | Holstein bodysuit, pink udder, horns through rotting head |
| Creeper | Milk carton body, "MOO-BOOM" label, daisy in mouth |
| Skeleton | Cow bones, cow skull, femur bow, cowbell necklace |
| Spider | Fluffy cow-print fur, hooves on 8 legs, cowbell anklets |
| Enderman | Tall spotted cow, purple cow eyes, top hat |
| Blaze | Cheddar cow head, spinning butter rods |
| Ghast | Mozzarella cow head, sad eyes, "moo" speech bubble |
| Witch | Cow in witch hat, milk potion |
| Pig | Bad cow disguise, "I AM COW" sign |

## Block textures (16×16)

| Block | Concept |
|-------|---------|
| Stone | Fossilized cow spots, hoof print |
| Dirt | Cow-print patches, buried cowbell |
| Diamond ore | Glowing blue cowbells in stone |
| TNT | "MOO" label, cow spots, tail fuse |
| Crafting table | "Brindal & Grayson's Workshop" |

## GUI / environment / items

| Asset | Size | Concept |
|-------|------|---------|
| Pack icon | 256×256 | Cows with B/G ear tags, "BRINDAL & GRAYSON'S COW WORLD" |
| Panorama | 512×512 | Hills of cows, cowbell sun, milk rivers |
| Hotbar slot | 16×16 | Cow-hide leather, lasso border |
| Sword / pickaxe | 16×16 | Cow horn weapons |
| Sun | 32×32 | Golden cowbell |
| Moon | 32×32 | Swiss cheese with bite marks |

## Pro tips

1. Generate at 1024×1024, downscale nearest-neighbor — never bilinear
2. Skin sheets may need manual UV compositing after generation
3. Batch with FLUX for style consistency across mobs
4. Use `style_preset: pixel-art` when available
5. Only upscale pack icon / panorama — never upscale 16×16 targets

## Pipeline integration

Algorithmic cow-hide (`build_cow_pack.py`) covers all 4600+ textures. Venice overrides **featured** textures listed in `venice_prompts.json` for higher-quality comedy art on key mobs, blocks, and UI.

Cached generations live in `variants/ultimate-chaos-pack/venice_cache/` (gitignored).
