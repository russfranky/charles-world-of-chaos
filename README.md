# Cel Band Pack

A **Minecraft Bedrock 1.21+ resource pack** built from converted cel-band textures — not procedurally generated at build time.

| What | Description |
|------|-------------|
| **Texture pack** | Committed PNG overrides in `variants/cel-band/pack/` |
| **Build** | Zips those assets into `Cel_Band_Pack.mcpack` |
| **Level converter** | Maps tile JSON to Bedrock `/setblock` placements |

---

## Install

**[Cel_Band_Pack.mcpack](https://github.com/russfranky/charles-world-of-chaos/releases/latest/download/Cel_Band_Pack.mcpack)**

1. Import the `.mcpack` on your device.
2. **Settings → Global Resources** → activate **Cel Band Pack**.
3. Open any Bedrock 1.21+ world.

Or build locally:

```bash
./scripts/build_pack.sh
```

---

## Visual system

Converted block textures replace vanilla surfaces with four cel bands:

| Band | Block | Use |
|------|-------|-----|
| Lit cream | `calcite` | Top faces |
| Warm sand | `stone` | Lit sides |
| Warm brown | `deepslate` | Shadow sides |
| Deep shadow | `bedrock` | Cave floors |

Gold, emerald, and copper blocks use converted relic palettes. Items and UI chrome are included in the pack source.

---

## Adding or updating textures

1. Place converted PNGs under `variants/cel-band/pack/textures/`.
2. Update `variants/cel-band/pack/manifest.json` only if name or version changes.
3. Run `./scripts/build_pack.sh`.

The build does not synthesize textures — it packages what is already in `pack/`.

---

## Level conversion

Tile-based level JSON converts to Bedrock placements:

```bash
python3 variants/cel-band/scripts/convert_level.py \
  --level variants/cel-band/levels/sample_level.json \
  --origin 100,64,200 \
  --output download/
```

The sample **Cave of Snakes** level ships in `download/sample_level.json`.

---

## Repository layout

| Path | Role |
|------|------|
| `variants/cel-band/pack/` | Converted textures + manifest (24 files; see `docs/WORKFLOW.md`) |
| `scripts/preflight_check.py` | Pre-import structural validation (from Archive 2) |
| `docs/TRADEMARK_AUDIT.md` | Franchise term inventory and redaction guide |
| `variants/cel-band/scripts/assemble_pack.py` | Zip pack → `.mcpack` |
| `variants/cel-band/scripts/convert_level.py` | Level JSON → setblock / mcfunction |
| `dist/Cel_Band_Pack.mcpack` | Shipped distributable |
| `download/` | Release bundle mirror |

---

## Documentation

- [Installation](docs/installation.md)
- [Development](docs/development.md)
- [Voxel spec PDF](download/Voxel_Spec.pdf)

---

## License

MIT — see [LICENSE](LICENSE).

This project is not affiliated with or endorsed by Mojang Studios.
