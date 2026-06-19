# Marketplace store marketing assets

Scaffold for **Brindal & Grayson Cow Ranch** world template SKU. Final art and screenshots are captured on iPad — this folder holds specs, copy drafts, and a procedural key-art placeholder.

## Required assets

| Asset | Size | Format | Status |
|-------|------|--------|--------|
| **Key art / store tile** | 800×450 | PNG or JPEG | Stub: [`key_art_stub_800x450.png`](key_art_stub_800x450.png) — replace before submission |
| **Screenshots** | 1920×1080 | PNG or JPEG | See [`SCREENSHOT_CHECKLIST.md`](SCREENSHOT_CHECKLIST.md) — not captured yet |
| **World icon** (template picker) | 800×450 | JPEG | Export with world template; see [`worlds/brindal_grayson_ranch/`](../worlds/brindal_grayson_ranch/) |
| **Trailer / animated GIF** | — | MP4 or GIF | Optional; still open |
| **Store copy** | — | English text | Draft: [`STORE_COPY.md`](STORE_COPY.md) |

## Description copy placeholders

Use [`STORE_COPY.md`](STORE_COPY.md) as the source of truth until copy is pasted into partner portal fields:

- **Title** — short product name (≤ ~30 chars ideal)
- **Subtitle** — one-line hook
- **Description** — 2–3 sentences + feature bullets
- **Changelog** — version line for first release (add when SKU locks)

## Regenerating key art stub

Procedural placeholder only — not submission quality:

```bash
python3 scripts/generate_marketing_stub.py
```

Output: `marketing/key_art_stub_800x450.png`

## Related docs

- [docs/MARKETPLACE.md](../docs/MARKETPLACE.md) — Phase 5 store package checklist
- [worlds/brindal_grayson_ranch/WORLD_CHECKLIST.md](../worlds/brindal_grayson_ranch/WORLD_CHECKLIST.md) — world export before screenshots
