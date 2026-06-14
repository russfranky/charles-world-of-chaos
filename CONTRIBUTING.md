# Contributing

Thank you for helping improve Brindal & Grayson Cow World.

## One unified add-on

Everything builds into a single distributable:

| Source | Role |
|--------|------|
| `variants/ultimate-chaos-pack/scripts/` | Main build pipeline (textures, sounds, behavior) |
| `resource_packs/brindal_grayson_cow_rp/` | Custom cow RP source — merged at build |
| `behavior_packs/brindal_grayson_cow_bp/` | Custom cow BP source — merged at build |
| `dist/brindal-grayson-cow-pack.mcaddon` | Final output |

Run `./scripts/build-mcaddon.sh` from the repo root.

## Conventions

- **Namespace**: `bgcow:` for custom identifiers
- **UUIDs**: Never change manifest UUIDs after release
- **Custom cows**: Edit `resource_packs/` and `behavior_packs/`; `merge_custom_cows.py` overlays them into the built pack
- **Chaos pipeline**: Edit `variants/ultimate-chaos-pack/scripts/`
- **Venice AI**: `VENICE_API_KEY` env var — never commit keys

## Testing Checklist

- [ ] `validate_pack.py` passes
- [ ] Blocks/items have cow-hide textures
- [ ] Mobs appear as cows and make cow sounds
- [ ] Brindal and Grayson cows spawn and are NOT transformed away
- [ ] `/summon bgcow:brindal_cow` and `bgcow:grayson_cow` work
- [ ] iPad import via Safari works

## Reporting Issues

[GitHub Issues](https://github.com/russfranky/brindal-grayson-cow-pack/issues) — include Minecraft version, platform, and steps to reproduce.
