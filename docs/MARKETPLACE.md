# Marketplace Readiness Checklist

**Product:** Brindal & Grayson Cow Ranch — world template / cooperative add-on  
**Status:** In progress — keep this file updated until we ship or abandon Marketplace  
**Last updated:** 2026-06-15

---

## How to use this doc

- Check boxes when a item is **done and verified** (build + iPad playtest where noted).
- Leave unchecked items open; add notes under **Blockers** as we learn more.
- Kid download (.mcaddon from `main`) can stay ahead of Marketplace; Marketplace has stricter rules.

---

## Phase 0 — Partner & SKU

| | Task | Notes |
|---|------|-------|
| ☐ | Confirm Marketplace partner / publisher path | Required before submission |
| ☐ | Lock SKU type: **World template** “Brindal & Grayson Cow Ranch” | BP + RP bundled; not a skin-only pack |
| ☐ | Mob index approvals for shipped mobs (`bgcow:brindal_cow`, `bgcow:grayson_cow`) | See `docs/mob-index/` |

---

## Phase 1 — Technical compliance (CADDONREQ / cooperative add-on)

| | Task | Notes |
|---|------|-------|
| ☐ | Run MCTools cooperative add-on validation | No errors on submission set |
| ☐ | Remove JSON UI screen overrides | **Done** — lang-only branding via `apply_pack_lang.py` |
| ☐ | Real custom items `bgcow:ranch_bell`, `bgcow:feed_bag` | **Done** — BP items + icons; legacy bell/wheat still recognized |
| ☐ | Reduce or document Beta APIs + Holiday Creator Features | World template may lock experiments ON |
| ☐ | Script API uses stable `@minecraft/server` 2.x patterns | Audit before submission |
| ☐ | No disallowed vanilla overrides (UI, core screens, click sounds) | Lang-only pack branding OK |
| ☐ | Pack UUIDs / versioning policy for store updates | Document in release notes |

---

## Phase 2 — Art & audio (Marketplace bar)

| | Task | Notes |
|---|------|-------|
| ☐ | Professional texture pass (blocks, items, cows, icon) | Baked procedural art is placeholder |
| ☐ | Visible in-world traits (horns, marks) on custom cows | Partially done |
| ☐ | Menu music + SFX review (length, loudness, loop) | Trimmed lite menu track shipped |
| ☐ | Marketing key art (store tile, panorama optional) | 512+ store assets |
| ☐ | No third-party / Venice-only assets without license trail | Audit `prompts/` usage |

---

## Phase 3 — Tutorial world & kid UX

| | Task | Notes |
|---|------|-------|
| ☐ | Ship locked **world template** with barn tutorial | Signs, starter kit, wild cow spawn |
| ☐ | Onboarding without reading chat (ActionForm menus) | Ranch Bell menu + herd picker done |
| ☐ | Parent commands optional (`/bgcow:*`) | Hidden from kid path |
| ☐ | Save/persistence tested across sessions | `bgcow:barn_v1` dynamic property |
| ☐ | Rank-up titles and catalog progression readable | Shipped in script API |

---

## Phase 4 — QA matrix

| | Task | Notes |
|---|------|-------|
| ☐ | iPad Bedrock (primary) | User playtest |
| ☐ | Android / Windows Bedrock | Secondary |
| ☐ | Target engine: 1.21+ | `min_engine_version` in manifests |
| ☐ | New world + experiments ON/OFF matrix | Document in TESTING.md |
| ☐ | `.mcaddon` size under store guidance | ~217 KB lite build |
| ☐ | `validate_pack.py` + `simulate_barn.py` green in CI | Automated gate |

---

## Phase 5 — Store package

| | Task | Notes |
|---|------|-------|
| ☐ | English store description + changelog | |
| ☐ | Screenshots (gameplay, barn menu, cows) | Min 3–5 |
| ☐ | Trailer or animated GIF (optional) | |
| ☐ | Localization plan (ES, FR, …) | English-only today |
| ☐ | Age rating / content flags | Kid-friendly ranch sim |

---

## Phase 6 — Optional SKUs

| | Task | Notes |
|---|------|-------|
| ☐ | Skin pack (“Brindal & Grayson costumes”) | Separate SKU |
| ☐ | Mash-up bundle (world + skins + music) | After world template ships |

---

## Current blockers (living list)

1. **Beta APIs** — Cow Barn still requires Script API experimental toggle for new worlds.
2. **Holiday Creator Features** — Custom `bgcow:` entities require HCF in new worlds.
3. **Art quality** — Procedural/baked textures below Marketplace visual bar.
4. **No world template** — Add-on only today; Marketplace world needs pre-built ranch.
5. **Partner account** — No publisher path confirmed in repo.

---

## Progress log

| Date | Change |
|------|--------|
| 2026-06-15 | Phase 1 start: `bgcow:ranch_bell` / `bgcow:feed_bag`, removed JSON UI from build, `apply_pack_lang.py` |

---

## Related docs

- [GETTING_STARTED.md](GETTING_STARTED.md) — kid install path
- [MARKETPLACE.md](MARKETPLACE.md) — **Marketplace readiness checklist** (in progress)
- [TESTING.md](../TESTING.md) — manual QA
- [docs/mob-index/MOB_INDEX.md](mob-index/MOB_INDEX.md) — mob approvals
- [development.md](development.md) — build pipeline
