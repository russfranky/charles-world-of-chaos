# Testing Guide

## What Linux CI Can Test

| Check | Automated | Notes |
|-------|-----------|-------|
| Build pipeline completes | Yes | `./scripts/build-mcaddon.sh` |
| Lite texture count (20+) | Yes | `validate_pack.py` |
| Custom Spot/Storm cows present | Yes | Textures + entity files after merge |
| Manifest UUID linkage | Yes | BP depends on RP UUID `d36a0504-...` |
| BP manifest mentions Beta APIs | Yes | `validate_pack.py` |
| Script API file present | Yes | `behavior_pack/scripts/main.js` |
| Cow Barn script markers | Yes | `loadBarn`, `tryBreed`, `onBellTap`, etc. |
| Barn flow simulation | Yes | `simulate_barn.py` in `validate_pack.py` |
| MCADDON size under 1.5 MB | Yes | `validate_pack.py` (lite ~220 KB) |
| Package artifacts exist | Yes | `.mcaddon` and `.mcpack` in `dist/` |
| Venice AI textures | Optional | Requires `VENICE_API_KEY` locally or in CI secret |
| Sounds play as cow moos | No | Requires in-game testing |
| Script API commands | No | Requires Beta APIs enabled |
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
   - [ ] Cow title screen subtitle mentions Ranch Bell (after pack import)
   - [ ] First join auto-deploys starter cow + Ranch Bell + Feed Bag
   - [ ] Tap **Ranch Bell** → barn menu opens (Deploy, Feed, Breed, Recall, My herd)
   - [ ] **My herd** → tap a cow to switch active cow
   - [ ] Feed Bag does NOT catch your own deployed vanilla cow
   - [ ] Can catch 3rd cow (Pen rank allows 3 slots) and unlock breeding
   - [ ] Recall switches to next cow in herd
   - [ ] Tap **Feed Bag** near wild cow → cow caught into barn
   - [ ] Tap **Feed Bag** on deployed cow → hunger/mood rise
   - [ ] At 3+ cows, Breed produces calf with trait inheritance
   - [ ] New trait discovery grants loot (gold/emerald/diamond)
   - [ ] Hungry deployed cow recalls to barn (no death)
   - [ ] Spot Cow appears when deploying `spot` coat; Storm Cow for `storm`/`shine`
   - [ ] `/bgcow:help`, `/bgcow:barn`, `/bgcow:breed` work
   - [ ] Behavior-pack description in world settings mentions Beta APIs

### Beta APIs OFF (negative test)

1. Create a **new** world with Beta APIs **OFF** (Holiday Creator Features still ON)
2. Verify:
   - [ ] Ranch Bell does nothing (expected)
   - [ ] `/summon bgcow:brindal_cow` still works (Spot Cow)
   - [ ] Pack description warned about Beta APIs before creating world

### macOS Minecraft Bedrock

Same as iPad. After building, copy packs from:

```
variants/ultimate-chaos-pack/pack/          → development_resource_packs/
variants/ultimate-chaos-pack/behavior_pack/ → development_behavior_packs/
```

## CI Artifacts

Every push to `main` uploads:
- `brindal-grayson-cow-pack.mcaddon`
- `brindal-grayson-cow-pack.mcpack`

Download from **Actions** → latest workflow run → **Artifacts**.

CI builds algorithmic textures + cow GUI. Venice AI art requires `VENICE_API_KEY` (maintainer rebuild).

## Manual Validation Commands

```bash
# Full rebuild
./scripts/build-mcaddon.sh

# Validate structure + barn simulation
python3 variants/ultimate-chaos-pack/scripts/validate_pack.py
python3 variants/ultimate-chaos-pack/scripts/simulate_barn.py

# Lite sanity checks
find variants/ultimate-chaos-pack/pack/textures -name '*.png' | wc -l
grep -rl 'geometry.cow.v2' variants/ultimate-chaos-pack/pack/entity/ 2>/dev/null | wc -l
grep -rl 'bgcow:transform_to_cow' variants/ultimate-chaos-pack/behavior_pack/ 2>/dev/null | wc -l

# Check dist sizes
ls -lh dist/

# Clean build artifacts
./scripts/clean.sh
```

Expected lite counts after build:
- Textures: ~34 PNGs
- Entity geometry overrides: 0 (lite intentional)
- BP transforms (`bgcow:transform_to_cow`): 0 (lite intentional)
- MCADDON: ~700–900 KB

## Known Limitations

- Linux CI cannot run Minecraft Bedrock
- Default CI build uses algorithmic cow-hide + procedural GUI (not Venice AI)
- Lite pack does not auto-transform mobs
- Script API requires Beta APIs experimental toggle
- JSON UI modifications may need updates after major Bedrock releases
