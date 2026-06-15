# Pack UUIDs

**Never change shipped UUIDs after release** — existing worlds will break.

## Unified add-on (what players install)

Built into `dist/brindal-grayson-cow-pack.mcaddon`:

| Pack | Header UUID | Role |
|------|-------------|------|
| Resource pack | `d36a0504-4533-4271-b115-a49c53b7bc97` | Shipped RP — textures, sounds, UI |
| Behavior pack | `26cbe6c2-9ac3-464e-a6cd-08bfef85c38d` | Shipped BP — custom cows, script API |

Defined in `variants/ultimate-chaos-pack/scripts/common.py` and written by `personalize_pack.py`.

## Source-only custom cow packs

Editable in `resource_packs/brindal_grayson_cow_rp/` and `behavior_packs/brindal_grayson_cow_bp/`. These are **merged at build time** — not installed alone.

| Pack | Header UUID |
|------|-------------|
| Custom RP source | `c409dd16-412b-422a-9496-e1335c9f3ed5` |
| Custom BP source | `26cbe6c2-9ac3-464e-a6cd-08bfef85c38d` (same BP header as unified) |

The script module UUID in the unified BP reuses `c409dd16-...` — intentional, not a copy-paste mistake.

## Verify

```bash
python3 variants/ultimate-chaos-pack/scripts/validate_pack.py
```

Checks that the built RP header UUID is `d36a0504-4533-4271-b115-a49c53b7bc97`.
