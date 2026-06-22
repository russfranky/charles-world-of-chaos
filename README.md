# Sunlit Diorama

A **Minecraft Bedrock 1.21+ resource pack** with a sunlit outdoor diorama look: warm stone surfaces, Holstein spot accents, four-step cel bands, and ink outlines.

| | |
|---|---|
| **Pack type** | Global resource pack (`.mcpack`) |
| **Engine** | Bedrock 1.21.0+ |
| **Size** | ~11 KB |
| **Tooling** | Python generator + voxel level converter |

---

## Install

### Option A — Latest release

Download the attached `.mcpack` from [GitHub Releases](https://github.com/russfranky/charles-world-of-chaos/releases/latest):

**[Sunlit_Diorama.mcpack](https://github.com/russfranky/charles-world-of-chaos/releases/latest/download/Sunlit_Diorama.mcpack)**

1. Open the file on your device (or import via Minecraft).
2. Go to **Settings → Global Resources** and activate **Sunlit Diorama**.
3. Load any Bedrock world — block textures update immediately.

### Option B — Build from source

```bash
pip3 install -r requirements.txt
./scripts/build_pack.sh
```

The pack is written to `dist/Sunlit_Diorama.mcpack`.

See [docs/installation.md](docs/installation.md) for platform-specific steps.

---

## Visual system

Four cel bands map to vanilla blocks for builder-friendly placement:

| Band | Block | Use |
|------|-------|-----|
| Lit cream | `calcite` | Sunlit tops |
| Warm sand | `stone` | Lit sides |
| Warm brown | `deepslate` | Shadow sides |
| Deep shadow | `bedrock` | Cave floors / underhangs |

Holstein spot masks and ink outlines are baked into block textures. Relic blocks (gold, emerald, copper) use warm bronze and jade tones from the diorama palette.

---

## Deliverables

| Path | Description |
|------|-------------|
| `dist/Sunlit_Diorama.mcpack` | Shipped resource pack |
| `download/` | Release bundle (pack, tool, sample level, voxel spec PDF) |
| `variants/sunlit-diorama/` | Source of truth for the generator and sample level |
| `variants/sunlit-diorama/scripts/diorama_mc_tool.py` | Texture generator + voxel converter |

### Sample level

`download/sample_level.json` is a Cave of Snakes vignette (45 tiles → 50 block placements). Convert or paste into a world:

```bash
python3 variants/sunlit-diorama/scripts/diorama_mc_tool.py --mode convert \
  --level variants/sunlit-diorama/levels/sample_level.json \
  --origin 100,64,200
```

Outputs `/setblock` commands (`sample_level.setblock`) and an `.mcfunction` file.

---

## Documentation

- [Installation guide](docs/installation.md)
- [Development guide](docs/development.md)
- [Voxel spec PDF](download/Voxel_Spec.pdf) — tile types and palette rules

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| Minecraft Bedrock 1.21.0+ | Not Java Edition |
| Python 3.11+ | For local builds (`Pillow`) |

---

## License

MIT — see [LICENSE](LICENSE).

This project is not affiliated with or endorsed by Mojang Studios.
