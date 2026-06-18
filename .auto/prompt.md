# Autoresearch: Brindal & Grayson Cow World

## Objective

Shrink and polish the **lite overlay** Bedrock pack without breaking Cow Barn gameplay, custom cows, or parent install flow. Every iteration must stay iPad-friendly (~750 KB target, hard cap 1.5 MB in validation).

## Metrics

- **Primary**: `mcaddon_kb` (KB, **lower** is better) — `dist/brindal-grayson-cow-pack.mcaddon` after full build
- **Secondary**: `build_sec`, `texture_count`, `barn_sim_ok` (1=pass), `validate_ok` (1=pass)

## How to Run

```bash
./.auto/measure.sh    # METRIC lines to stdout
./.auto/checks.sh     # must exit 0 before logging status=keep
python3 scripts/autoresearch/summarize.py
```

`measure.sh` runs **two** builds and reports the **median** `mcaddon_kb` / `build_sec` to reduce jitter (pi-autoresearch guidance for fast benchmarks).

## Files in Scope

| Area | Paths |
|------|--------|
| Build pipeline | `variants/ultimate-chaos-pack/scripts/*.py`, `scripts/build-mcaddon.sh` |
| Gameplay | `variants/ultimate-chaos-pack/script_api/main.js` |
| Texture polish | `texture_polish.py`, `polish_textures.py`, `optimize_pngs.py` |
| Lite staging | `prepare_lite_pack.py`, `venice_generate_textures.py` |
| Custom cows | `resource_packs/brindal_grayson_cow_rp/`, `behavior_packs/brindal_grayson_cow_bp/` |
| Dist artifact | `dist/brindal-grayson-cow-pack.mcaddon` (rebuilt each measure) |

## Off Limits

- Shipped pack UUIDs (`docs/UUIDS.md`)
- Removing Brindal/Grayson custom cows or barn persistence keys
- Re-enabling full chaos (entity model swap, auto-cowify all mobs, 95 MB vanilla copy)
- `play_ready.json` gate pattern (rejected)

## Constraints

- `./.auto/checks.sh` must pass before any `keep` experiment
- Mob approvals: shipped mobs stay approved in `docs/mob-index/mob-approvals.json`
- Beta APIs + HCF requirements unchanged in manifests/docs
- No new pip deps without justification

## What's Been Tried

### Baseline (main, post PR #21)

- ~713 KB mcaddon, Cow Barn ActionForm UI, Bayer dither texture polish
- Lite overlay only; Venice optional via `VENICE_TEXTURES=1`

### Key wins (merged)

- Lite overlay vs full vanilla copy (−95 MB)
- Texture polish pipeline (alpha → quantize → dither → despeckle → edge-snap)
- Cow Barn simulation fixes (pen deadlock, deployed-cow trap, hunger persist)
- ActionForm barn menu (marketplace-style UX)

### Dead ends

- Chat `!command` loop for kids — replaced by tap-to-play bell + feed bag
- Play-ready bureaucratic gate — user rejected
- Full Venice entity/GUI ship in lite build — too heavy for iPad

### Next ideas (backlog)

- Custom item icons for Ranch Bell / Feed Bag (not renamed vanilla items)
- Commit cached Venice PNGs for kid-visible blocks without API at CI time
- Hubzz-3d-pipeline stage alignment when repo is accessible
- Herd picker form with coat previews
