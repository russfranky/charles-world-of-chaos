# Autoresearch: Brindal & Grayson Cow World

## Objective

Shrink and polish the **lite overlay** Bedrock pack without breaking Cow Barn gameplay, custom cows, or parent install flow. Every iteration must stay iPad-friendly (**~250 KB target**, hard cap 1.5 MB in validation).

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

- `./.auto/checks.sh` must pass before any `keep` experiment (includes `validate_marketplace.py`)
- Mob approvals: shipped mobs stay approved in `docs/mob-index/mob-approvals.json`
- Beta APIs + HCF requirements unchanged in manifests/docs
- No new pip deps without justification

## What's Been Tried

### Baseline (main, post PR #22 autoresearch setup)

- ~713 KB mcaddon (`mcaddon_kb=712.97`), menu music ~575 KB raw

### Experiment 1 — KEEP (audio + icon + zip)

- `optimize_audio.py`: mono 44.1kHz 64k vorbis menu music (~588→336 KB)
- Pack icon: 128px palette-quantized PNG (was 256px full-color)
- `compresslevel=9` on mcaddon/mcpack zips
- **Result: mcaddon_kb=395** (−318 KB, ~45%), all checks pass

### Experiment 2 — KEEP (music trim + icon sync)

- Menu music trimmed to **28s** loop @ 48k mono (still loops in title screen)
- Sync polished RP `pack_icon.png` → behavior pack after texture polish
- **Result: mcaddon_kb=228** (−167 KB vs exp 1), music_kb≈173

### Key wins (merged)

- Lite overlay vs full vanilla copy (−95 MB)
- Texture polish pipeline (alpha → quantize → dither → despeckle → edge-snap)
- Cow Barn simulation fixes (pen deadlock, deployed-cow trap, hunger persist)
- ActionForm barn menu (marketplace-style UX)

### Dead ends

- Chat `!command` loop for kids — replaced by tap-to-play bell + feed bag
- Play-ready bureaucratic gate — user rejected
- Full Venice entity/GUI ship in lite build — too heavy for iPad

### Experiment 3 — KEEP (herd picker + tiny BP icon)

- mcaddon_kb≈217

### Experiment 4 — KEEP (rank-up titles + menu hints)

- mcaddon_kb stable ~217

### Experiment 5 — KEEP (kid textures + item icons)

- `cowify_kid_textures.py` — procedural grass/dirt/bread + Feed Bag wheat + Ranch Bell icons
- `baked_textures/` committed cache (CI uses without Venice API)
- Removed empty `item_texture.json` overlay (vanilla atlas merge)
- **Result: mcaddon_kb≈218**, texture_count=36

### Experiment 6 — KEEP (more baked blocks)

- Cow-spot cobblestone + crafting table top in `baked_textures/`
- mcaddon_kb stable ~217.5

### Experiment 7 — KEEP (stone + chest + marketplace validator)

- `cowify_kid_textures.py`: baked `stone.png` + `chest_front.png` (cow-spot ranch chest)
- `validate_marketplace.py` wired into `.auto/checks.sh` (no JSON UI, custom items, script refs)
- **Result: mcaddon_kb≈217.75**, texture_count=36, marketplace compliance pass

### Marketplace polish (PR #29, parallel track)

- `docs/MARKETPLACE.md` living checklist
- Real `bgcow:ranch_bell` / `bgcow:feed_bag` items; lang-only pack branding (no JSON UI)

### Next ideas (backlog)

- Hubzz-3d-pipeline stage alignment when repo is accessible
- World template stub with experiments locked ON (Marketplace Phase 3)
- MCTools cooperative add-on validation run
- Further music trim (shorter loop) if parents want sub-350 KB
