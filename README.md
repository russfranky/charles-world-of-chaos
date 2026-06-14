# Brindal & Grayson Ultimate Cow Pack

An aggressively cow-themed Minecraft Bedrock Edition add-on for iPad — built for Brindal and Grayson. Everything looks, sounds, and (via behavior pack) **becomes** cows.

## Quick Install (iPad)

1. Download the full add-on:
   **[brindal-grayson-ultimate-cow.mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-ultimate-cow.mcaddon)**
2. Open in Safari → tap download → **Open in Minecraft**
3. Create a **NEW** world with:
   - **Holiday Creator Features** enabled
   - **Beta APIs** enabled
4. Activate both the resource pack and behavior pack in world settings

## What It Does

| Layer | Effect |
|-------|--------|
| **Resource pack** | 4,600+ textures replaced with cow-hide patterns; all mobs render as cows |
| **Sounds** | Mob sounds redirected to cow moos (unused mob audio pruned) |
| **Behavior pack** | Non-cow mobs transform into cows on spawn; non-cow spawn rules zeroed |
| **Script API** | Backup cowifier catches anything the behavior pack misses |

### Personal touches
- Pack icon and name for Brindal & Grayson
- Custom painting
- Diamond block textured with **"B"**
- Gold block textured with **"G"**

## Repository Structure

```
brindal-grayson-cow-pack/
├── pack/                    # Built resource pack (gitignored)
├── behavior_pack/           # Built behavior pack (gitignored)
├── dist/                    # Distributables (committed after build)
│   ├── brindal-grayson-ultimate-cow.mcaddon      # Full add-on (RP + BP + Script)
│   └── brindal-grayson-ultimate-cow-pack.mcpack  # Visual-only fallback
├── scripts/                 # Build pipeline
│   ├── build_all.py         # Full pipeline orchestrator
│   ├── build_cow_pack.py    # Texture cowification
│   ├── cowify_entity_models.py
│   ├── cowify_sounds.py
│   ├── cowify_behavior_entities.py
│   ├── personalize_pack.py
│   ├── package_mcpack.py
│   ├── package_mcaddon.py
│   ├── prune_sounds.py
│   └── validate_pack.py
├── vanilla_src/             # Cloned at build time (gitignored)
├── docs/                    # See TESTING.md, RESEARCH.md
├── requirements.txt
└── .github/workflows/ci.yml
```

## Build from Source

```bash
pip3 install -r requirements.txt

# Clone vanilla assets
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/Mojang/bedrock-samples.git vanilla_src
cd vanilla_src && git sparse-checkout set resource_pack behavior_pack && cd ..

# Full build
python3 scripts/build_all.py --rebuild-textures

# Validate
python3 scripts/validate_pack.py
```

## Resource Pack UUID

```
d36a0504-4533-4271-b115-a49c53b7bc97
```

The behavior pack manifest depends on this UUID.

## Visual-Only Fallback

If Script API or behavior pack causes issues on your device, use the resource-only pack:

**[brindal-grayson-ultimate-cow-pack.mcpack](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-ultimate-cow-pack.mcpack)**

## License

MIT — see [LICENSE](LICENSE). Minecraft assets derived from [Mojang bedrock-samples](https://github.com/Mojang/bedrock-samples).
