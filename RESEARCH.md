# Research Notes

## Source Material

- [Mojang bedrock-samples](https://github.com/Mojang/bedrock-samples) — vanilla RP/BP cloned at build time
- [Bedrock Wiki — Pack Structure](https://wiki.bedrock.dev/documentation/pack-structure)
- [Microsoft Learn — Behavior Packs](https://learn.microsoft.com/en-us/minecraft/creator/documents/behaviorpack)
- [Microsoft Learn — Script API](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/)

## Cowification Strategy

### Textures (RP)
Replace all PNG textures (except `textures/entity/cow/`) with tiled cow-hide patterns sampled from `cow_v2.png`. Small icons (≤32px) blend 15% original for shape readability.

### Entity Models (RP)
Override client entity JSON for every mob except cow/mooshroom:
- `geometry.cow.v2` (+ warm/cold/baby variants)
- Cow textures and animations
- `controller.render.cow.v3`

### Sounds (RP)
Redirect all `entity_sounds.entities.*` events to `mob.cow.say`, `mob.cow.hurt`, `mob.cow.death`, `mob.cow.step`.

### Behavior (BP)
1. **Transform on spawn**: Add `minecraft:transformation` → `minecraft:cow` via `bgcow:transform_to_cow` component group triggered on `minecraft:entity_spawned`
2. **Zero spawn rules**: Set `minecraft:weight.default` to 0 for all non-cow entities
3. **Loot tables**: Replace entity loot with cow loot (beef + leather)

### Script API (BP)
Backup `entitySpawn` handler that removes non-cow mobs and spawns cows at the same location. Requires Beta APIs.

## iPad Requirements

- Minecraft Bedrock 1.21.0+
- Holiday Creator Features (for behavior pack transforms)
- Beta APIs (for Script API backup)
- Both packs must be active in world settings

## UUID Stability

Resource pack header UUID is fixed at `d36a0504-4533-4271-b115-a49c53b7bc97`. Never change after release — existing worlds reference this UUID.

## Alternative Approaches Considered

| Approach | Pros | Cons | Chosen? |
|----------|------|------|---------|
| RP-only (textures + models) | Safe, no experiments | Mobs still behave as originals | Fallback `.mcpack` |
| BP transform on spawn | Everything becomes real cows | Needs experiments | Yes |
| Script API cowifier | Catches edge cases | Needs Beta APIs | Yes (backup) |
| Replace vanilla cow.json | Simpler | Doesn't affect other mobs | No |
