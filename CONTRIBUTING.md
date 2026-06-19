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
python3 scripts/generate_mob_index.py   # refresh mob preview gallery
python3 scripts/validate_mob_approvals.py  # gate before publishing dist
```

### Mob index (approve before publish)

Visual catalog of every mob texture — custom cows plus the Venice entity catalog:

| File | Purpose |
|------|---------|
| [`docs/mob-index/index.html`](docs/mob-index/index.html) | Browser gallery (open locally or from repo) |
| [`docs/mob-index/MOB_INDEX.md`](docs/mob-index/MOB_INDEX.md) | Markdown gallery on GitHub |
| [`docs/mob-index/mob-approvals.json`](docs/mob-index/mob-approvals.json) | Set `"approved": true` per mob you sign off on |
| [`variants/ultimate-chaos-pack/shipped_mobs.json`](variants/ultimate-chaos-pack/shipped_mobs.json) | Which mob IDs are in the downloadable pack |

`./scripts/build-mcaddon.sh` regenerates the index and runs the approval check at the end.


## Conventions

- **Namespace**: `bgcow:` for custom identifiers
- **UUIDs**: Never change manifest UUIDs after release — see [docs/UUIDS.md](docs/UUIDS.md)
- **Custom cows**: Edit `resource_packs/` and `behavior_packs/`; register new files in `merge_custom_cows.py`
- **Pack icon**: Place `pack-icon.png` (or `pack_icon.png`, 256×256+ square PNG) in `resource_packs/brindal_grayson_cow_rp/` — used in-game and in docs
- **GUI**: Edit `gui_overrides/` only — never commit built `pack/ui/` overrides
- **Venice AI**: `VENICE_API_KEY` env var or `.env` file (see `.env.example`) — never commit keys
- **Releases**: tag `v*` to publish `.mcaddon` / `.mcpack` via GitHub Releases
- **Pre-commit**: `pip install -r requirements.txt && pre-commit install`

## Testing checklist

- [ ] `python3 variants/ultimate-chaos-pack/scripts/validate_pack.py` passes (or `./.auto/checks.sh`)
- [ ] `./.auto/measure.sh` — note `mcaddon_kb` if optimizing pack size
- [ ] **Mob index:** open [`docs/mob-index/index.html`](docs/mob-index/index.html) — approve shipped mobs in [`mob-approvals.json`](docs/mob-index/mob-approvals.json), then `python3 scripts/validate_mob_approvals.py`
- [ ] Brindal and Grayson cows present and NOT transformed away
- [ ] `/summon bgcow:brindal_cow` and `bgcow:grayson_cow` work
- [ ] Ranch Bell opens barn menu; Feed Bag catches wild cows (needs Beta APIs)
- [ ] `/bgcow:barn`, `/bgcow:breed`, `/bgcow:next` work for parents
- [ ] Holiday Creator Features OFF shows in-game HCF hint when deploying custom coats (negative test)
- [ ] iPad install from [latest release mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/releases/latest/download/brindal-grayson-cow-pack.mcaddon)

## Reporting issues

[GitHub Issues](https://github.com/russfranky/brindal-grayson-cow-pack/issues) — include Minecraft version, platform, and steps to reproduce.
