# Brindal & Grayson Cow Ranch — world template scaffold

**Status:** Scaffold only — no binary `.mcworld` / `.mctemplate` in repo (CI cannot export Bedrock worlds).

Marketplace SKU is a **world template**, not a standalone add-on download. Players get a pre-built ranch with both packs linked and experiments locked **ON**.

## What the shipped template must contain

| Requirement | Detail |
|-------------|--------|
| **Spawn & barn** | Safe flat starter pad; fenced pen or small barn near world spawn |
| **Tutorial signs** | 3–5 signs: tap Ranch Bell, use Feed Bag, catch wild cows, breed at Yard rank (3+ cows) — no chat required |
| **Starter kit** | Script API already gives Ranch Bell, Feed Bag, cookies, and one barn cow on first join — verify in-world after export |
| **Wild cow hook** | At least one wild `minecraft:cow` (or Spot/Storm spawn egg in a chest) within ~20 blocks for Feed Bag demo |
| **Both packs pre-linked** | RP `c409dd16-412b-422a-9496-e1335c9f3ed5` + BP `26cbe6c2-9ac3-464e-a6cd-08bfef85c38d` active in world settings |
| **Experiments locked ON** | **Beta APIs** (`gametest`) + **Holiday Creator Features** (`data_driven_items`) — set at world creation, then `lock_template_options: true` |
| **Engine floor** | Bedrock **1.21.0+** (`base_game_version` and pack `min_engine_version`) |
| **Store metadata** | `texts/en_US.lang` name/description; `world_icon.jpeg` 800×450 for template picker |

## Repo contents (version-controlled)

```
worlds/brindal_grayson_ranch/
├── README.md                 ← this file
├── WORLD_CHECKLIST.md        ← human build/export steps (iPad or Win10)
├── manifest.json             ← world template header stub (format_version 2)
├── level_settings.reference.json  ← experiments + pack UUIDs (NOT read by game; use at build time)
└── texts/
    ├── en_US.lang
    └── languages.json
```

After a human exports the world from Minecraft, the zip layout adds binary assets the repo does not store:

- `level.dat` — experiments and spawn; see [Bedrock Wiki — enabling experiments](https://wiki.bedrock.dev/nbt/enabling-experiments)
- `db/` — chunk database
- `resource_packs/` / `behavior_packs/` — embedded pack copies (folder names **≤10 characters** for Xbox)
- `world_resource_packs.json`, `world_behavior_packs.json` — pack linkage

Rename the final zip to `.mctemplate` for Marketplace submission tooling.

## Related docs

- [docs/MARKETPLACE.md](../../docs/MARKETPLACE.md) — Phase 3 checklist
- [docs/GETTING_STARTED.md](../../docs/GETTING_STARTED.md) — kid install path (add-on today)
- [docs/COMMANDS.md](../../docs/COMMANDS.md) — Ranch Bell / Feed Bag UX to mirror on signs
