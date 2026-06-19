# Build & export checklist — Brindal & Grayson Cow Ranch

Use **iPad** or **Windows 10/11 Bedrock**. Allow ~30–60 minutes for a first pass.

## Before you start

- [ ] Install latest `.mcaddon` from repo build (`./scripts/build-mcaddon.sh` → `dist/brindal-grayson-cow-pack.mcaddon`) or GitHub `main` artifact
- [ ] Minecraft Bedrock **1.21.0+**
- [ ] Copy `manifest.json` and `texts/` from this folder — you will merge them into the exported world zip

## 1. Create the tutorial world

1. **Play → Create New** — name it `Brindal Grayson Ranch` (internal name; store string comes from `texts/en_US.lang`)
2. **Game settings → Experiments** — turn **ON**:
   - **Holiday Creator Features** (custom `bgcow:` cows)
   - **Beta APIs** (Cow Barn scripts)
3. **Resource Packs** → activate **Brindal & Grayson Cow World**
4. **Behavior Packs** → activate **Brindal & Grayson Cow World BP**
5. **Create** and enter the world

> Experiments and pack links lock in at creation. If you forget a toggle, start a **new** world.

## 2. Build the starter ranch (Creative is fine)

- [ ] Set **world spawn** on a flat grass pad (or `/setworldspawn` after building)
- [ ] Build a small **barn or fenced pen** (10×10 minimum) at spawn
- [ ] Place **signs** (kid-readable, no slash commands):
  - "Tap the **Ranch Bell** in your bag"
  - "Use **Feed Bag** on cows — catch wild ones nearby"
  - "Get **3 cows** to unlock breeding"
- [ ] Spawn or lead at least one **wild cow** near the pen for the Feed Bag tutorial
- [ ] Optional: chest with cookies; script already grants starter items on first join — **playtest once in Survival** to confirm

## 3. Verify gameplay

- [ ] New player join: inventory has Ranch Bell, Feed Bag, starter barn cow
- [ ] Tap Ranch Bell → ActionForm menu (Deploy, Feed, Breed, Recall, My herd)
- [ ] Feed Bag catches wild cow within 5 blocks
- [ ] Quit and rejoin — barn herd persists (`bgcow:barn_v1`)
- [ ] Parent commands optional: `/bgcow:help`, `/bgcow:barn`

## 4. Export from Minecraft

**Windows:** Edit world → General → **Export World** → save as `.mcworld`

**iPad:** Limited export — prefer Win10 for template packaging, or use Files app + third-party zip tools if you have a `.mcworld` share path.

## 5. Turn export into a world template

1. Rename `*.mcworld` → `*.zip` and extract
2. Confirm `resource_packs/` and `behavior_packs/` folders exist with both packs (rename folders to **≤10 chars** if needed, e.g. `bgr_rp`, `bgr_bp`)
3. Copy from this repo folder:
   - `manifest.json` (update UUIDs only if you intentionally fork the SKU)
   - `texts/en_US.lang`, `texts/languages.json`
4. Confirm `manifest.json` has:
   - `"lock_template_options": true`
   - `"base_game_version": [1, 21, 0]`
5. Add or replace `world_icon.jpeg` (800×450 JPEG)
6. **Do not** delete `level.dat` or `db/` unless you intentionally ship a random-seed template (we want a fixed ranch — keep them)
7. Zip **inner files** (not the parent folder), rename to `brindal_grayson_ranch.mctemplate`
8. Double-click to import → **Create New → Imported Templates** → create test world

## 6. Experiments audit (optional NBT edit)

If experiments are OFF after export, open `level.dat` in [NBT Studio](https://github.com/Tryashtar/NBTStudio) and set byte tags under `experiments`:

| In-game toggle | NBT key | Value |
|----------------|---------|-------|
| Beta APIs | `gametest` | `1` |
| Holiday Creator Features | `data_driven_items` | `1` |

Also set `experiments_ever_used` and `saved_with_toggled_experiments` to `1` if present. See `level_settings.reference.json` in this folder.

## 7. Handoff back to repo

We cannot commit binary worlds in CI. After validation:

- [ ] Attach `.mctemplate` to Marketplace submission / internal drive
- [ ] Note export date and Minecraft version in [docs/MARKETPLACE.md](../../docs/MARKETPLACE.md) progress log
- [ ] Capture 3–5 screenshots (spawn, signs, barn menu, cows) for Phase 5
