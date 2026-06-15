# Venice AI Prompts — "Everything Is Cow" Minecraft Skins

Prompts for generating featured textures for **Brindal & Grayson Cow World** via [Venice AI](https://venice.ai). Used by `variants/ultimate-chaos-pack/scripts/venice_generate_textures.py`.

Algorithmic cow-hide (`build_cow_pack.py`) covers all 4,600+ textures. Venice overrides **65 featured** textures listed in `venice_prompts.json` for higher-quality comedy art on key mobs, blocks, items, GUI, and panoramas. The full template catalog for batch expansion lives in `venice_prompt_catalog.json`.

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
# List all texture IDs (65 featured)
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --list

# Generate featured mobs only
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --category entity

# Specific textures
python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --id zombie,creeper,pack_icon

# Full Venice pass during build (auto-enabled when VENICE_API_KEY is set)
./scripts/build-mcaddon.sh
# or explicitly:
python3 variants/ultimate-chaos-pack/scripts/build_all.py --rebuild-textures --venice
```

## Master prompt template

```
[OBJECT DESCRIPTION], Minecraft pixel art texture, flat shading, no anti-aliasing,
limited color palette, cow-themed (black and white Holstein patches, pink udder accents),
seamless tileable, crisp pixel edges, no background noise
```

Do **not** put pixel dimensions in the text prompt — set `width`/`height` in API params only.

## Style anchor (generate first)

> A lineup of five Minecraft mobs (zombie, creeper, skeleton, spider, pig) all wearing ridiculous handmade cow costumes. Each costume is slightly different and badly fitting. They stand in a row on a Minecraft grass block stage. One holds a sign saying "We are ALL cows now."

Reference this output's palette and comedy tone for consistency.

## Featured manifest (`venice_prompts.json`)

| Category | Count | Examples |
|----------|-------|----------|
| **entity** | 27 | zombie, creeper, warden, brindal_cow, grayson_cow |
| **block** | 15 | stone, ores, grass, netherrack, furnace, chest |
| **item** | 9 | steak, milk bucket, diamond, bow |
| **gui** | 4 | pack icon, hotbar, heart, crosshair |
| **environment** | 2 | sun, moon |
| **panorama** | 6 | panorama_0–5 (full title-screen cubemap) |

See `python3 variants/ultimate-chaos-pack/scripts/venice_generate_textures.py --list` for the full ID list.

### Mob entity textures (64×64 UV sheets)

Comedy tone: mobs in **badly fitting cow costumes**, not literal cow replacements.

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
| Wither skeleton | Charcoal cow bones, horned cow skull |
| Guardian | Cow-spotted fish, giant dopey cow eye |
| Slime | Cow face trapped inside green gel |
| Pillager | Cow-print bandit outfit, femur crossbow |
| Ravager | Bull with enormous horns and cowbell saddle |
| Warden | Bioluminescent Holstein spots, glowing cow nose |
| Breeze | Swirling cow-print wind spirit |
| Wither boss | Three cow skull heads |
| Brindal / Grayson | Kids in cow onesies with B/G crowns |

### Block textures (16×16)

Stone/ore family, grass, netherrack, soul sand, end stone, cobblestone, TNT ("MOO"), crafting table ("Brindal & Grayson's Workshop"), furnace (cow-nose opening), chest (cow face latch).

### Items, GUI, environment

| Asset | Size | Concept |
|-------|------|---------|
| Pack icon | 256×256 | Cows with B/G ear tags, "BRINDAL & GRAYSON'S COW WORLD" |
| Panorama | 512×512 ×6 | Hills of cows, cowbell sun, milk rivers |
| Hotbar slot | 16×16 | Cow-hide leather, lasso border |
| Sword / pickaxe / bow | 16×16 | Cow horn weapons |
| Steak / milk / bread | 16×16 | Cow-themed food icons |
| Sun | 32×32 | Golden cowbell |
| Moon | 32×32 | Swiss cheese with bite marks |
| Heart / hunger / crosshair | 9–15px | Cow-spotted HUD icons |

## Full catalog (`venice_prompt_catalog.json`)

Template definitions for all texture families — stone/ore, wood (9 types × 4 variants), nether, wool/concrete (16 colors), redstone, paintings, particles, and villager professions. Use for batch expansion:

```bash
python3 variants/ultimate-chaos-pack/scripts/expand_venice_manifest.py
```

## Pro tips

1. Generate at 1024×1024, downscale nearest-neighbor — never bilinear
2. Skin sheets may need manual UV compositing after generation
3. Batch with FLUX for style consistency across mobs
4. Use `style_preset: pixel-art` when available
5. Only upscale pack icon / panorama — never upscale 16×16 targets
6. Generate 4 variants per prompt (`n: 4` in API), pick the best

## Pipeline integration

```
build_cow_pack.py → cowify_* → personalize → merge_custom_cows → cowify_gui → Venice (--all) → package
```

Cached generations live in `variants/ultimate-chaos-pack/venice_cache/` (gitignored).
