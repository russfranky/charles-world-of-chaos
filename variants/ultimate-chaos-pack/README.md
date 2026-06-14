# Ultimate Chaos Build Pipeline

Builds the **unified** Brindal & Grayson Cow World add-on:

1. Cowify 4600+ textures, mobs, sounds, behavior
2. Merge Brindal & Grayson custom cows (`merge_custom_cows.py`)
3. Package → `dist/brindal-grayson-cow-pack.mcaddon`

## Build

```bash
# From repo root (recommended)
./scripts/build-mcaddon.sh

# Or chaos pipeline only
pip3 install -r ../../requirements.txt
python3 scripts/build_all.py --rebuild-textures
python3 scripts/validate_pack.py
```

## Output

| File | Description |
|------|-------------|
| `dist/brindal-grayson-cow-pack.mcaddon` | Full add-on — install this |
| `dist/brindal-grayson-cow-pack.mcpack` | Visual-only fallback |

## Optional: Venice AI textures

```bash
export VENICE_API_KEY='your-key'
python3 scripts/venice_generate_textures.py --category entity
python3 scripts/build_all.py --rebuild-textures --venice
```

See [VENICE_PROMPTS.md](../../VENICE_PROMPTS.md).

## Resource pack UUID

```
d36a0504-4533-4271-b115-a49c53b7bc97
```
