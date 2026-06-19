# Marketplace Readiness Checklist

**Product:** Brindal & Grayson Cow Ranch — world template / cooperative add-on  
**Status:** In progress — keep this file updated until we ship or abandon Marketplace  
**Last updated:** 2026-06-18 (Phase 1 Script API audit)

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
| ☐ | Run MCTools cooperative add-on validation | **Partial — automated** via [`scripts/validate_mctools.sh`](../scripts/validate_mctools.sh) (optional CI, `continue-on-error`); **40 CADDONREQ failures** on lite build as of 2026-06-18 — see [MCTools](#mctools-manual) |
| ☐ | Remove JSON UI screen overrides | **Done** — lang-only branding via `apply_pack_lang.py` |
| ☐ | Real custom items `bgcow:ranch_bell`, `bgcow:feed_bag` | **Done** — BP items + icons; legacy bell/wheat still recognized |
| ☐ | Reduce or document Beta APIs + Holiday Creator Features | World template may lock experiments ON |
| ☑ | Script API uses stable `@minecraft/server` 2.x patterns | **Audited** — [MARKETPLACE_SCRIPT_API.md](MARKETPLACE_SCRIPT_API.md); not **Done** until Beta dependency removed or world template locks experiments |
| ☐ | No disallowed vanilla overrides (UI, core screens, click sounds) | **Done** — lang-only branding; no UI JSON or click-sound swaps in build |
| ☐ | Pack UUIDs / versioning policy for store updates | Document in release notes |

---

## Phase 2 — Art & audio (Marketplace bar)

| | Task | Notes |
|---|------|-------|
| ☐ | Professional texture pass (blocks, items, cows, icon) | Baked procedural art — stone, chest, cobble, grass, coal/iron/gold/diamond/emerald ore, netherrack, furnace, TNT (MOO + cow-tail fuse) added |
| ☐ | Visible in-world traits (horns, marks) on custom cows | **Partial** — deploy name tags (⌇/★/◆), size scale, gold-horn glow + deploy particles; texture art still TBD |
| ☐ | Menu music + SFX review (length, loudness, loop) | Trimmed lite menu track shipped |
| ☐ | Marketing key art (store tile, panorama optional) | 512+ store assets |
| ☐ | No third-party / Venice-only assets without license trail | Audit `prompts/` usage |

---

## Phase 3 — Tutorial world & kid UX

| | Task | Notes |
|---|------|-------|
| ☐ | Ship locked **world template** with barn tutorial | Scaffold: [`worlds/brindal_grayson_ranch/`](../worlds/brindal_grayson_ranch/) — human export still required |
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
| ☑ | New world + experiments ON/OFF matrix | **Done** — [TESTING.md § Experiment matrix](../TESTING.md#experiment-matrix-new-world) |
| ☐ | `.mcaddon` size under store guidance | ~217 KB lite build |
| ☐ | `validate_pack.py` + `simulate_barn.py` green in CI | Automated gate + `validate_marketplace.py` in `.auto/checks.sh` |

---

## Phase 5 — Store package

| | Task | Notes |
|---|------|-------|
| ☑ | Marketing asset scaffold | [`marketing/`](../marketing/) — README, [`STORE_COPY.md`](../marketing/STORE_COPY.md), [`SCREENSHOT_CHECKLIST.md`](../marketing/SCREENSHOT_CHECKLIST.md), key art stub |
| ☐ | English store description + changelog | Draft in [`marketing/STORE_COPY.md`](../marketing/STORE_COPY.md) — paste into partner portal |
| ☐ | Screenshots (gameplay, barn menu, cows) | Min 3–5 — checklist in [`marketing/SCREENSHOT_CHECKLIST.md`](../marketing/SCREENSHOT_CHECKLIST.md); iPad capture still open |
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

## MCTools (manual)

**Minecraft Creator Tools** ([Learn overview](https://learn.microsoft.com/en-us/minecraft/creator/documents/mctoolsoverview?view=minecraft-bedrock-stable)) is Microsoft's validator for cooperative add-ons and Marketplace sharing rules (CADDONREQ, sharing suite). It checks manifest linkage, forbidden UI overrides, loose files, namespaces, and flags experimental capabilities (Beta APIs, Holiday Creator Features).

**Automated in repo (optional CI):** [`scripts/validate_mctools.sh`](../scripts/validate_mctools.sh) builds the pack if needed, then runs the CLI. Exits **0** on pass or when Node/npx/npm fetch is unavailable (`SKIP: MCTools not available`); exits **1** when the tool runs and reports validation failures. CI runs this step with `continue-on-error: true` so flaky `npx` downloads do not block merges.

**Working CLI in this environment (2026-06-18):**

```bash
./scripts/build-mcaddon.sh   # if dist/brindal-grayson-cow-pack.mcaddon is missing
npx --yes @minecraft/creator-tools \
  --if dist/brindal-grayson-cow-pack.mcaddon \
  --offline --yes \
  validate addon
```

Notes:

- Pass the archive with `--if` / `--input-file`, not as a positional argument to `validate`.
- Use suite **`addon`** (Coop Add-On Requirements), not `main` or `default`.
- `--offline` skips vanilla web resource fetches (recommended for CI).
- Invalid: `npx @minecraft/creator-tools validate dist/foo.mcaddon` — treats the path as the suite name.

**Latest automated run (lite `.mcaddon`, v0.17.2):** tool **ran**; exit **4** with **40 errors** — mainly CADDONREQ102/104 (vanilla overlay textures not under `textures/<creatorshortname>/`), CADDONIREQ170 (`pack_scope` should be `world`). **Fixed:** CADDONREQ168 — RP manifest now declares BP dependency via `BP_HEADER_UUID` in `write_rp_manifest()` (`personalize_pack.py`). Expected for kid-download overlay layout; Marketplace submission will need namespace/pack restructuring.

**`pack_scope` (CADDONIREQ170):** not set on the lite `.mcaddon` RP manifest — cooperative add-ons are world-agnostic overlays. `header.pack_scope: world` belongs on the **world template** scaffold ([`worlds/brindal_grayson_ranch/`](../worlds/brindal_grayson_ranch/)) when that SKU ships, not on the kid-download `.mcaddon`.

**Manual fallback:**

1. **Web:** Zip the submission set (or upload `.mcaddon`) at [mctools.dev](https://mctools.dev) → **Inspector** → rule suite **Coop Add-On Requirements** (and **Sharing** before store upload). Processing stays in the browser.
2. **CLI:** same command as above, or `./scripts/validate_mctools.sh`.

We rely on `validate_marketplace.py` + iPad playtests for day-to-day CI gates; MCTools is informational until the pack passes CADDONREQ.

---

## Current blockers (living list)

1. **Beta APIs** — Cow Barn still requires Script API experimental toggle for new worlds.
2. **Holiday Creator Features** — Custom `bgcow:` entities require HCF in new worlds.
3. **Art quality** — Procedural/baked textures below Marketplace visual bar.
4. **No world template (binary)** — Add-on only today. **Partial:** repo scaffold at [`worlds/brindal_grayson_ranch/`](../worlds/brindal_grayson_ranch/) (manifest, checklist, experiments reference); `.mctemplate` must be built/exported on iPad or Win10 — see `WORLD_CHECKLIST.md`.
5. **Partner account** — No publisher path confirmed in repo.

---

## Progress log

| Date | Change |
|------|--------|
| 2026-06-15 | Phase 1 start: `bgcow:ranch_bell` / `bgcow:feed_bag`, removed JSON UI from build, `apply_pack_lang.py` |
| 2026-06-18 | Build-time cel/toon bake in `texture_polish.py` (luminance bands + ink outlines; no in-game shaders) |
| 2026-06-18 | Autoresearch exp 8: baked coal_ore + iron_ore kid textures (cow-spot ore blocks) |
| 2026-06-18 | Autoresearch exp 9: baked netherrack + furnace_front off/on kid textures (cow-spot nether + lit nose) |
| 2026-06-18 | Autoresearch exp 10: baked gold_ore + diamond_ore + emerald_ore kid textures (cow-spot ore blocks) |
| 2026-06-18 | Phase 3 scaffold: `worlds/brindal_grayson_ranch/` (README, WORLD_CHECKLIST, manifest stub, experiments reference); `validate_world_scaffold.py` in checks |
| 2026-06-18 | Phase 2 traits: deploy name tags + scale + gold-horn glow/particles on custom cows (`always_show` nameable) |
| 2026-06-18 | Phase 4: experiment matrix in TESTING.md; MCTools note; marketplace validator checks Beta APIs + cow UI |
| 2026-06-18 | Phase 1: Script API stability audit — [MARKETPLACE_SCRIPT_API.md](MARKETPLACE_SCRIPT_API.md); V2 2.0.0 + custom commands require Beta APIs |
| 2026-06-18 | Phase 1: MCTools CLI wired — `scripts/validate_mctools.sh`; optional CI step; 41 CADDONREQ failures on lite build |
| 2026-06-18 | Phase 1: CADDONREQ168 fixed — RP→BP manifest dependency in `write_rp_manifest()`; MCTools lite `.mcaddon` **40 errors** (was 41) |
| 2026-06-18 | Phase 5 scaffold: [`marketing/`](../marketing/) — store copy draft, screenshot checklist, procedural key art stub |

---

## Related docs

- [GETTING_STARTED.md](GETTING_STARTED.md) — kid install path
- [MARKETPLACE.md](MARKETPLACE.md) — **Marketplace readiness checklist** (in progress)
- [TESTING.md](../TESTING.md) — manual QA
- [docs/mob-index/MOB_INDEX.md](mob-index/MOB_INDEX.md) — mob approvals
- [development.md](development.md) — build pipeline
- [worlds/brindal_grayson_ranch/](../worlds/brindal_grayson_ranch/) — Marketplace world template scaffold (Phase 3)
- [marketing/](../marketing/) — store marketing asset scaffold (Phase 5)
