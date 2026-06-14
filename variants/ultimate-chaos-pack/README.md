# Ultimate Chaos Pack

The **Ultimate Chaos** variant cowifies the entire Minecraft Bedrock experience for Brindal and Grayson:

- **4,600+** textures replaced with cow-hide patterns
- **All mobs** render as cows and transform into cows on spawn
- **All mob sounds** redirected to cow moos
- Script API backup cowifier

## Build (from repo root)

```bash
./scripts/build-mcaddon.sh          # builds both variants
# or chaos only:
pip3 install -r requirements.txt
python3 variants/ultimate-chaos-pack/scripts/build_all.py --rebuild-textures
python3 variants/ultimate-chaos-pack/scripts/validate_pack.py
```

## Output

| File | Description |
|------|-------------|
| `dist/ultimate-chaos.mcaddon` | Full add-on (RP + BP + Script API) |
| `dist/ultimate-chaos.mcpack` | Visual-only fallback |

## iPad install

1. Download `dist/ultimate-chaos.mcaddon`
2. Safari → Open in Minecraft
3. **New world** with Holiday Creator Features + Beta APIs
4. Activate both resource and behavior packs

## Requirements

- Minecraft Bedrock 1.21.0+
- Holiday Creator Features (behavior transforms)
- Beta APIs (Script API backup)
- Optional: `VENICE_API_KEY` for AI-generated featured textures — see [VENICE_PROMPTS.md](../../VENICE_PROMPTS.md)

## Resource pack UUID

```
d36a0504-4533-4271-b115-a49c53b7bc97
```
