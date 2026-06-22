# Lara Croft GO Diorama — Bedrock 1.21+

Sunlit outdoor LC GO aesthetic for Minecraft Bedrock: warm stone, Holstein spots, 4-step cel bands, ink outlines.

## Deliverables (`/download/`)

| File | Description |
|------|-------------|
| `Lara_Croft_GO_Diorama.mcpack` | Drop-in resource pack (13 blocks, 5 items, 2 UI) |
| `Lara_Croft_GO_MC_Voxel_Spec.pdf` | Full technical specification |
| `lcgo_mc_tool.py` | Python generator + voxel converter |
| `sample_level.json` | 12×12 Cave of Snakes sample level |
| `sample_level.setblock` | `/setblock` commands for in-game paste |

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
