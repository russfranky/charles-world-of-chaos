# Lara Croft GO Diorama — Bedrock 1.21+

Sunlit outdoor LC GO aesthetic for Minecraft Bedrock: warm stone, Holstein spots, 4-step cel bands, ink outlines.

## Deliverables (`/download/`)

| File | Description |
|------|-------------|
| `Lara_Croft_GO_Diorama.mcpack` | Drop-in resource pack (22 files, ~12.5 KB) |
| `Lara_Croft_GO_MC_Voxel_Spec.pdf` | Voxel spec (20 pages) |
| `Lara_Croft_GO_Diorama_Technical_Report.pdf` | Companion reverse-engineering report |
| `lcgo_mc_tool.py` | Python generator + voxel converter (canonical source) |
| `sample_level.json` | Cave of Snakes sample (45 tiles → 50 blocks) |
| `sample_level.setblock` | `/setblock` commands for in-game paste |
| `lcgo_mc_output/` | Unpacked `.mcpack` (or `unzip Lara_Croft_GO_Diorama.mcpack -d lcgo_mc_output`) |

Uploaded as `Archive.zip` (commit `f2b4584`).

## Quick start

```bash
# Regenerate everything from palette
python3 variants/lcgo-diorama/scripts/lcgo_mc_tool.py --mode all

# Textures only (iterate on PALETTE)
python3 variants/lcgo-diorama/scripts/lcgo_mc_tool.py --mode textures

# Convert custom level
python3 variants/lcgo-diorama/scripts/lcgo_mc_tool.py --mode convert \
  --level my_level.json --origin 100,64,200
```

## 4 cel bands (builder cheat sheet)

| Band | Block | LC GO use |
|------|-------|-----------|
| Lit cream | `calcite` | Sunlit tops |
| Warm sand | `stone` | Lit sides |
| Warm brown | `deepslate` | Shadow sides |
| Deep shadow | `bedrock` | Cave floors |

Install: double-click `.mcpack` → activate in **Settings → Global Resources**.
