# Marketplace Script API Audit — Cow Barn

**Scope:** `variants/ultimate-chaos-pack/script_api/main.js` and BP manifest (`write_bp_manifest` in `personalize_pack.py`)  
**Audited:** 2026-06-18  
**Engine target:** Bedrock 1.21+ (`min_engine_version`: `[1, 21, 0]`)  
**Module deps:** `@minecraft/server` **2.0.0**, `@minecraft/server-ui` **2.0.0**

---

## Executive summary

Cow Barn uses **Scripting V2 (2.0.0)** patterns correctly for its feature set: custom slash commands, early startup registration, ActionForm menus, player dynamic properties, and entity spawn/visuals. Code quality is good — state changes are deferred with `system.run`, command handlers use read-only-safe `runFor`, and risky APIs are wrapped in try/catch.

**Marketplace blocker:** The entire **2.0.0 module dependency requires the Beta APIs experiment**. Microsoft documents Scripting V2 as experimental preview ([Scripting V2 Overview](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/v2-overview)). Phase 1 is **Audited**, not **Done**, until either (a) V2 graduates to stable without Beta, or (b) we ship a **world template** that locks Beta APIs ON (acceptable for Marketplace world templates — see [MARKETPLACE.md](MARKETPLACE.md) Phase 1).

**Separate blocker:** Custom entities (`bgcow:brindal_cow`, `bgcow:grayson_cow`) require **Holiday Creator Features (HCF)**, not Script API.

---

## Dependency versions (2.0.0)

| Module | Manifest version | Correct for features used? | Stable without Beta? |
|--------|------------------|----------------------------|----------------------|
| `@minecraft/server` | `2.0.0` | Yes — custom commands, `system.beforeEvents.startup`, V2 promise flushing | **No** — V2 requires Beta APIs toggle |
| `@minecraft/server-ui` | `2.0.0` | Yes — pairs with server 2.x | **No** — tied to V2 experiment |

**Stable alternative (future migration):** `@minecraft/server` **1.17.0** (1.21.60) + `@minecraft/server-ui` **1.3.0** cover world/events, forms, dynamic properties, and inventory without V2 — but **not** script-registered custom commands or `system.beforeEvents.startup`. A Beta-free path would drop `/bgcow:*` (parent-only today) and register logic on `world.afterEvents.worldLoad` instead.

**min_engine_version note:** Custom commands shipped in **1.21.80**. Manifest says `[1, 21, 0]`; consider bumping to `[1, 21, 80]` before store submission so unsupported clients fail clearly.

---

## APIs used

| API / pattern | Module | Usage in Cow Barn | Risk | Notes |
|---------------|--------|-------------------|------|-------|
| `world.getPlayers()` | server | Care-decay interval | **Low** | Stable 1.x pattern; works in V2 world-ready phase |
| `world.getDimension()` | server | Fallback dimension | **Low** | Stable |
| `world.beforeEvents.itemUse` + `event.cancel` | server | Ranch Bell / Feed Bag taps | **Low** | Stable event; gated on `commandsReady` |
| `world.afterEvents.playerSpawn` | server | Welcome, starter kit, reconcile deploy | **Low** | Stable; uses `initialSpawn` |
| `system.run` / `runInterval` | server | Defer UI/gameplay; 200-tick care loop | **Low** | Stable; correct deferral from command context |
| `system.beforeEvents.startup` | server | Register `/bgcow:*` commands | **High** | **V2 early execution — Beta APIs required** |
| `init.customCommandRegistry.registerCommand` | server | 4 namespaced parent commands | **High** | **Beta / V2**; requires 1.21.80+ |
| `CustomCommandStatus`, `CommandPermissionLevel` | server | Command results & permissions | **High** | Part of custom-command beta surface |
| `CustomCommandOrigin` (via `origin`) | server | `runFor` player resolution | **High** | Beta |
| `player.getDynamicProperty` / `setDynamicProperty` | server | `bgcow:barn_v1` JSON persistence | **Low** | Stable in 1.x; good Marketplace pattern |
| `player.sendMessage`, `onScreenDisplay` | server | Chat, action bar, titles | **Low** | Stable |
| `player.playSound` | server | Moo feedback | **Low** | Stable |
| `player.runCommandAsync` | server | Particles, fireworks | **Low** | Stable workaround for effects |
| `player.getComponent("minecraft:inventory")` | server | Starter kit, discovery loot | **Low** | Stable |
| `ItemStack` | server | Items, loot tables | **Low** | Stable |
| `dimension.spawnEntity` | server | Deploy cow, tutorial wild cow | **Medium** | Stable API; **custom** `bgcow:*` types need HCF |
| `dimension.getEntities` / filtered query | server | Recall, wild-cow catch | **Low** | Stable |
| `entity.nameTag`, `remove`, `location`, `typeId`, `id` | server | Labels, catch, reconcile | **Low** | Stable |
| `entity.setScale` | server | Small / chunk size visuals | **Medium** | Likely V2/beta; already try/catch + comment for older engines |
| `entity.runCommandAsync` | server | Shine/star particles on entity | **Low** | Stable |
| `ActionFormData` (title, body, button, show) | server-ui | Barn menu, herd picker | **Low** | Stable form pattern; **module** still 2.0.0 (Beta gate) |
| `console.warn` | — | Startup ready / registration failure | **Low** | Acceptable |

**Not used (good for review):** `@minecraft/server-gametest`, JSON UI overrides, `world.afterEvents.worldInitialize` (V1), block/item custom components in script, `runCommand` (sync), scoreboards, structure APIs.

---

## Beta / experimental patterns flagged

| Pattern | Why it may fail review | Mitigation |
|---------|------------------------|------------|
| **`@minecraft/server` 2.0.0** | Entire V2 stack listed as experimental preview | World template locks **Beta APIs ON**; document in store copy |
| **`system.beforeEvents.startup`** | Early execution; V2-only registration hook | Required for custom commands; no stable equivalent |
| **Script custom commands** (`/bgcow:*`) | Beta since 1.21.80 | Optional parent path — could remove for Beta-free SKU |
| **`entity.setScale`** | Not on stable Entity doc surface; may change | Non-critical cosmetic; try/catch already; could move scale to entity JSON |
| **HCF custom entities** | Not Script API — experiment for `bgcow:*` mobs | World template locks **HCF ON**; vanilla `minecraft:cow` fallback exists |

---

## What still requires Beta APIs — and why

| Requires Beta? | Feature | Reason |
|----------------|---------|--------|
| **Yes** | Script module load at all | Manifest declares `@minecraft/server` / `@minecraft/server-ui` **2.0.0** (Scripting V2) |
| **Yes** | `/bgcow:help`, `/bgcow:barn`, `/bgcow:breed`, `/bgcow:next` | Custom commands register only via `system.beforeEvents.startup` + `CustomCommandRegistry` (V2 beta) |
| **Yes** | Ranch Bell menu when `commandsReady === false` guard | Without Beta, startup registration fails → join hint (`BETA_APIS_HINT`) → item taps no-op |
| **No** (Script) | ActionForm menus, barn save, breed logic, item handlers | Same *code* uses stable-style APIs, but **won't run** without V2 module load |
| **No** (Script) | Player dynamic property `bgcow:barn_v1` | Stable API — blocked only because script doesn't load without Beta |
| **Separate: HCF** | Spot/Storm/Shine deploy, `/summon bgcow:*` | Holiday Creator Features for custom entity definitions |

Verified behavior: [TESTING.md § Experiment matrix](../TESTING.md#experiment-matrix-new-world).

---

## Recommendations before Marketplace submission

1. **World template:** Ship `.mctemplate` with **Beta APIs + HCF locked ON** (`lock_template_options: true`) — removes player burden; MCTools still flags experiments but Marketplace allows locked templates.
2. **Bump `min_engine_version`** to `[1, 21, 80]` if custom commands remain (matches custom-command ship version).
3. **Run MCTools** Coop Add-On Requirements on built `.mcaddon` / submission zip ([MARKETPLACE.md § MCTools](MARKETPLACE.md#mctools-manual)).
4. **Store copy:** Keep BP description + world settings text mentioning Beta APIs + HCF (already enforced by `validate_pack.py` / `validate_marketplace.py`).
5. **Optional Beta-free fork (Phase 2):** Downgrade to `@minecraft/server` 1.17.x, remove custom commands, move registration to `world.afterEvents.worldLoad` — kid path (bell + forms) could work without Beta; parent slash commands would go away.
6. **`entity.setScale`:** Consider BP entity `minecraft:scale` component per coat/size instead of runtime script scaling — reduces beta surface.
7. **iPad playtest:** Confirm row 1 of experiment matrix (HCF ON + Beta ON) before partner handoff.

---

## Code hygiene (audit)

- Imports: all used — no dead imports.
- Error handling: try/catch on spectator/invalid player paths; command registration logs failure; menu fallback to bell-cycle mode on form error.
- Namespace: commands use `bgcow:` prefix — correct for custom commands.
- No disallowed UI JSON — forms via Script API only ([validate_marketplace.py](../variants/ultimate-chaos-pack/scripts/validate_marketplace.py)).

---

## Related

- [MARKETPLACE.md](MARKETPLACE.md) — Phase 1 checklist
- [TESTING.md](../TESTING.md) — experiment matrix
- [Scripting V2 Overview](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/v2-overview)
- [Script module versioning](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/versioning?view=minecraft-bedrock-stable)
- [Scripting custom commands](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/custom-commands?view=minecraft-bedrock-stable)
