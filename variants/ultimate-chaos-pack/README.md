# Charles' World of Chaos — Build Pipeline

Builds the **unified** add-on shipped as `dist/brindal-grayson-cow-pack.mcaddon` (product name in Minecraft: **Charles' World of Chaos**).

## Pipeline

1. Cowify 4600+ textures, mobs, sounds, behavior
2. Merge custom cow entities (`merge_custom_cows.py`) — Spot Cow & Storm Cow
3. Cow GUI textures + JSON UI/lang/sounds (`cowify_gui.py`, `apply_gui_overrides.py`)
4. Optional Venice AI featured textures (`--venice`)
5. Package → `dist/`

## Build

```bash
# From repo root (recommended)
./scripts/build-mcaddon.sh

# Or pipeline only
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
./scripts/build-mcaddon.sh   # auto-enables --venice when key is set
```

See [VENICE_PROMPTS.md](../../VENICE_PROMPTS.md).

## GUI overrides

Source files live in `gui_overrides/` (not in built `pack/`). Applied at build by `apply_gui_overrides.py`.

## Resource pack UUID

```
d36a0504-4533-4271-b115-a49c53b7bc97
```

See [docs/UUIDS.md](../../docs/UUIDS.md).
