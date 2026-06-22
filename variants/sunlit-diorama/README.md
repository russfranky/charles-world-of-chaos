# Sunlit Diorama — Bedrock 1.21+

Sunlit outdoor diorama aesthetic for Minecraft Bedrock: warm stone, Holstein spots, four-step cel bands, ink outlines.

## Quick start

```bash
# From repository root
./scripts/build_pack.sh

# Or run the generator directly
python3 variants/sunlit-diorama/scripts/diorama_mc_tool.py --mode all \
  --output variants/sunlit-diorama/build
```

## Cel bands (builder reference)

| Band | Block | Use |
|------|-------|-----|
| Lit cream | `calcite` | Sunlit tops |
| Warm sand | `stone` | Lit sides |
| Warm brown | `deepslate` | Shadow sides |
| Deep shadow | `bedrock` | Cave floors |

## Files

| Path | Role |
|------|------|
| `scripts/diorama_mc_tool.py` | Texture generator, pack assembler, voxel converter |
| `levels/sample_level.json` | Cave of Snakes sample level |
| `VERSION` | Pack semver |
| `../download/` | Release bundle (populated by `build_pack.sh`) |

Install: import `dist/Sunlit_Diorama.mcpack` → **Settings → Global Resources**.
