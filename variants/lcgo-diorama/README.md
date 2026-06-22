# Lara Croft GO Diorama — Bedrock 1.21+

Sunlit outdoor LC GO aesthetic for Minecraft Bedrock: warm stone, Holstein spots, four-step cel bands, ink outlines.

## Quick start

```bash
# From repository root
./scripts/build_pack.sh

# Or run the generator directly
python3 variants/lcgo-diorama/scripts/lcgo_mc_tool.py --mode all \
  --output variants/lcgo-diorama/build
```

## Cel bands (builder reference)

| Band | Block | LC GO use |
|------|-------|-----------|
| Lit cream | `calcite` | Sunlit tops |
| Warm sand | `stone` | Lit sides |
| Warm brown | `deepslate` | Shadow sides |
| Deep shadow | `bedrock` | Cave floors |

## Files

| Path | Role |
|------|------|
| `scripts/lcgo_mc_tool.py` | Texture generator, pack assembler, voxel converter |
| `levels/sample_level.json` | Cave of Snakes sample level |
| `VERSION` | Pack semver |
| `../download/` | Release bundle (populated by `build_pack.sh`) |

Install: import `dist/Lara_Croft_GO_Diorama.mcpack` → **Settings → Global Resources**.
