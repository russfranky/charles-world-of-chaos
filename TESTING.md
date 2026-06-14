# Testing Guide

## What Linux CI Can Test

| Check | Automated | Notes |
|-------|-----------|-------|
| Build pipeline completes | Yes | `build_all.py --rebuild-textures` |
| Texture count (4000+) | Yes | `validate_pack.py` |
| Entity override count (100+) | Yes | Client entities use `geometry.cow.v2` |
| BP transform count (100+) | Yes | `bgcow:transform_to_cow` component group |
| Spawn rules zeroed (50+) | Yes | Non-cow weight = 0 |
| Manifest UUID linkage | Yes | BP depends on RP UUID |
| Script API file present | Yes | `behavior_pack/scripts/main.js` |
| Package artifacts exist | Yes | `.mcaddon` and `.mcpack` in `dist/` |
| Sounds play as cow moos | No | Requires in-game testing |
| Mobs visually render as cows | No | Requires Bedrock client |
| Transform-on-spawn works | No | Requires world with BP + experiments |
| Script API cowifier | No | Requires Beta APIs enabled |
| iPad import via Safari | No | Requires physical iPad |

## What Requires iPad / macOS Testing

### iPad (primary target)

1. Download `.mcaddon` from GitHub raw URL or AirDrop from Mac
2. Open in Minecraft → verify both packs import
3. Create new world:
   - Holiday Creator Features: **ON**
   - Beta APIs: **ON**
   - Both packs: **activated**
4. Verify:
   - [ ] Blocks/items have cow-hide textures
   - [ ] Diamond block shows "B", gold block shows "G"
   - [ ] Zombies, creepers, etc. appear as cows
   - [ ] Mobs make cow sounds
   - [ ] Non-cow mobs transform to cows on spawn
   - [ ] Only cows spawn naturally (no zombies, etc.)

### macOS Minecraft Bedrock

Same as iPad. Development pack paths:

```
~/Library/Containers/com.mojang.MinecraftBedrock/Data/Documents/games/com.mojang/
├── development_behavior_packs/brindal_grayson_cow_bp/
└── development_resource_packs/pack/
```

Copy `behavior_pack/` and `pack/` from the repo after building.

## CI Artifacts

Every push to `main` uploads:
- `brindal-grayson-ultimate-cow.mcaddon`
- `brindal-grayson-ultimate-cow-pack.mcpack`

Download from the Actions tab → latest workflow run → Artifacts.

## Manual Validation Commands

```bash
# Count cowified textures
find pack/textures -name '*.png' | wc -l

# Count entity overrides
grep -rl 'geometry.cow.v2' pack/entity/ | wc -l

# Count BP transforms
grep -rl 'bgcow:transform_to_cow' behavior_pack/entities/ | wc -l

# Check dist sizes
ls -lh dist/
```

## Known Limitations

- Linux CI cannot run Minecraft Bedrock
- Texture cowification is algorithmic (tiled cow-hide), not hand-painted
- Some complex mobs may have visual glitches when forced to cow geometry
- Script API requires Beta APIs experimental toggle
