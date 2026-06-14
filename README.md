# Brindal & Grayson Cow World

One Minecraft Bedrock add-on for **Brindal** (daughter) and **Grayson** (son) on iPad.

**Everything is cows** — plus two named custom cows just for them.

| What you get | Details |
|--------------|---------|
| **Ultimate cow chaos** | 4,600+ cow-hide textures, all mobs become cows, cow moos everywhere |
| **Brindal Cow** | `bgcow:brindal_cow` — brown with white spots, named for Brindal |
| **Grayson Cow** | `bgcow:grayson_cow` — gray with dark spots, named for Grayson |
| **Personal touches** | Pack icon with B & G, diamond block "B", gold block "G" |

## Quick Install (iPad)

1. [Download brindal-grayson-cow-pack.mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-cow-pack.mcaddon)
2. Safari → tap download → **Open in Minecraft**
3. Create a **NEW** world with:
   - **Holiday Creator Features** ON
   - **Beta APIs** ON
4. Activate both resource and behavior packs

Visual-only fallback (no experiments): [brindal-grayson-cow-pack.mcpack](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-cow-pack.mcpack)

Summon the kids' cows:

```
/summon bgcow:brindal_cow
/summon bgcow:grayson_cow
```

## Fun commands

**19 commands** for Brindal & Grayson — cow parties, cow rain, healing, flying, and more!

```
/bgcow:party    /bgcow:rain    /bgcow:brindal    /bgcow:grayson
/bgcow:help     !moo           !party            !b  !g
```

Full list: [docs/COMMANDS.md](docs/COMMANDS.md)

## Why one package?

Earlier versions shipped two separate add-ons (custom cows vs. ultimate chaos). That meant two downloads, two installs, and kids had to pick one. **One `.mcaddon` is simpler** — tap once, get everything. The build pipeline merges custom cow entities into the full chaos pack automatically.

## Repository Structure

```
brindal-grayson-cow-pack/
├── resource_packs/brindal_grayson_cow_rp/   # Custom cow source (merged at build)
├── behavior_packs/brindal_grayson_cow_bp/   # Custom cow source (merged at build)
├── variants/ultimate-chaos-pack/            # Build pipeline + Venice AI prompts
│   └── scripts/                             # build_all.py, cowify_*.py, merge_custom_cows.py
├── scripts/build-mcaddon.sh                 # → dist/brindal-grayson-cow-pack.mcaddon
├── dist/
│   ├── brindal-grayson-cow-pack.mcaddon     # Full add-on (install this)
│   └── brindal-grayson-cow-pack.mcpack      # Visual-only fallback
├── docs/
├── VENICE_PROMPTS.md                        # Optional AI texture generation
└── LICENSE
```

## Build from Source

```bash
pip3 install -r requirements.txt
./scripts/build-mcaddon.sh
```

Optional Venice AI featured textures:

```bash
export VENICE_API_KEY='your-key'
python3 variants/ultimate-chaos-pack/scripts/build_all.py --rebuild-textures --venice
```

## Requirements

- Minecraft Bedrock Edition 1.21.0+
- Holiday Creator Features + Beta APIs (for full experience)

## Resource Pack UUID

```
d36a0504-4533-4271-b115-a49c53b7bc97
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
