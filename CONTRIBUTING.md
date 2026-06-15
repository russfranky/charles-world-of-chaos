# Contributing

Thank you for helping improve Brindal & Grayson Cow World.

## One unified add-on

Everything builds into a single distributable:

| Source | Role |
|--------|------|
| `variants/ultimate-chaos-pack/scripts/` | Main build pipeline |
| `variants/ultimate-chaos-pack/gui_overrides/` | Cow GUI source (textures applied by `cowify_gui.py`) |
| `resource_packs/brindal_grayson_cow_rp/` | Custom cow RP — merged at build |
| `behavior_packs/brindal_grayson_cow_bp/` | Custom cow BP — merged at build |
| `dist/brindal-grayson-cow-pack.mcaddon` | Final output (committed for iPad install) |

```bash
./scripts/build-mcaddon.sh          # standard build
./scripts/clean.sh                  # remove local build artifacts
export VENICE_API_KEY='...'         # optional AI textures
./scripts/build-mcaddon.sh          # rebuilds with Venice when key set
```

## Conventions

- **Namespace**: `bgcow:` for custom identifiers
- **UUIDs**: Never change manifest UUIDs after release — see [docs/UUIDS.md](docs/UUIDS.md)
- **Custom cows**: Edit `resource_packs/` and `behavior_packs/`; register new files in `merge_custom_cows.py`
- **Pack icon**: Place `pack-icon.png` (or `pack_icon.png`, 256×256+ square PNG) in `resource_packs/brindal_grayson_cow_rp/` — used in-game and in docs
- **GUI**: Edit `gui_overrides/` only — never commit built `pack/ui/` overrides
- **Venice AI**: `VENICE_API_KEY` env var — never commit keys; CI does not run Venice by default

## Testing checklist

- [ ] `python3 variants/ultimate-chaos-pack/scripts/validate_pack.py` passes
- [ ] Brindal and Grayson cows present and NOT transformed away
- [ ] `/summon bgcow:brindal_cow` and `bgcow:grayson_cow` work
- [ ] `/bgcow:party` and `!moo` work (needs Beta APIs)
- [ ] Inventory shows cow-spot backgrounds (GUI layer)

## Reporting issues

[GitHub Issues](https://github.com/russfranky/brindal-grayson-cow-pack/issues) — include Minecraft version, platform, and steps to reproduce.
