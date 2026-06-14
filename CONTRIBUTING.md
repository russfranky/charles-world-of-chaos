# Contributing

Thank you for helping improve the Brindal & Grayson Cow Pack.

## Two add-ons, two code paths

| Add-on | Source location | Build output |
|--------|----------------|--------------|
| **Custom Cows** | `resource_packs/`, `behavior_packs/` | `dist/custom-cows.mcaddon` |
| **Ultimate Chaos** | `variants/ultimate-chaos-pack/` | `dist/ultimate-chaos.mcaddon` |

Edit the appropriate location for your change. Run `./scripts/build-mcaddon.sh` from the repo root to rebuild both.

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-change`
3. Make changes in the correct pack folder
4. Test in Minecraft Bedrock on iPad or Windows
5. Open a pull request

## Conventions

- **Namespace**: Use `bgcow:` for custom identifiers
- **UUIDs**: Never change existing manifest UUIDs after release
- **Custom Cows**: Entity JSON in `behavior_packs/brindal_grayson_cow_bp/`, textures in `resource_packs/brindal_grayson_cow_rp/`
- **Ultimate Chaos**: Modify scripts in `variants/ultimate-chaos-pack/scripts/`; run `validate_pack.py` after changes
- **Venice AI textures**: Set `VENICE_API_KEY`, edit `variants/ultimate-chaos-pack/prompts/venice_prompts.json`; never commit API keys

## Testing Checklist

### Custom Cows
- [ ] Brindal and Grayson cows spawn in animal biomes
- [ ] Spawn eggs in creative inventory
- [ ] Milking, breeding, and aging work
- [ ] Textures render correctly

### Ultimate Chaos
- [ ] `validate_pack.py` passes
- [ ] Blocks/items have cow-hide textures
- [ ] Mobs appear as cows and make cow sounds
- [ ] Non-cow mobs transform on spawn (needs experiments)

## Reporting Issues

Use the [GitHub issue tracker](https://github.com/russfranky/brindal-grayson-cow-pack/issues) with Minecraft version, platform, and which add-on you're using.
