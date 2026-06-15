# Cow Barn — Commands & Controls

**No typing needed** — kids tap items in their bag. Parents can use slash commands if they want.

## Play without typing (best for kids)

| What to do | What happens |
|------------|--------------|
| **Tap Ranch Bell** in your bag | Cycles: **DEPLOY** → **FEED** → **BREED** → **RECALL** |
| **Tap Feed Bag** (wheat) on your cow | Feeds active cow — raises hunger & mood |
| **Tap Feed Bag near a wild cow** (within 5 blocks) | Catches the cow into your barn |
| **Just play** | Hunger/mood decay over time — feed your herd! |

On first join you get a **Ranch Bell**, **Feed Bag**, cookies, and one starter cow in your barn.

### Ranch Bell cycle

Each tap advances one step:

1. **DEPLOY** — spawn your active cow beside you
2. **FEED** — feed your active cow
3. **BREED** — breed two happy adults (needs Yard rank: 3+ cows)
4. **RECALL** — send deployed cow back to the barn

The action bar shows your barn rank, herd size, catalog progress, and the **next** bell mode.

---

## Cow Barn basics

- Your herd lives in a **barn** saved on your player — up to 2 cows at Pen rank, more as you grow
- Cows have **traits**: coat, horns, size, mark — new combos unlock **catalog entries** and **real loot** (gold, emerald, diamond, diamond block…)
- **Breed** two adults with hunger 40+ and mood 55+ to get offspring with inherited (and sometimes mutated) traits
- Hungry deployed cows **recall to the barn** automatically — they don't die

### Barn ranks

| Cows in barn | Rank | Max slots |
|--------------|------|-----------|
| 1–2 | Pen | 2 |
| 3–7 | Yard | 4 |
| 8–14 | Ranch | 8 |
| 15–29 | Spread | 15 |
| 30+ | Legend | 30 |

### Custom cow types

| Trait coat | In-world look |
|------------|---------------|
| **spot** | Spot Cow (brown with white spots) |
| **storm** or **shine** | Storm Cow (gray with dark spots) |
| brown / gray | Vanilla cow |

---

## Slash commands (optional — for parents)

**Requires Beta APIs** enabled when creating the world.

| Slash command | What happens |
|---------------|--------------|
| `/bgcow:help` | Cow Barn help |
| `/bgcow:barn` | Show barn rank, herd, and catalog |
| `/bgcow:breed` | Breed your two best ready adults |

Type `/` in chat and search `bgcow:` to pick from the menu.

---

## Tips for parents

- Commands work **without traditional cheats** enabled
- Any player in the world can use them
- **Holiday Creator Features** must be ON for Spot Cow and Storm Cow to appear when deployed
- **Beta APIs** must be ON for the Cow Barn script — create a **new** world
- The behavior-pack description in Minecraft world settings also mentions the Beta APIs requirement

---

## No Script API?

If Beta APIs are off, vanilla summon still works:

```
/summon bgcow:brindal_cow
/summon bgcow:grayson_cow
```

You won't get the Cow Barn (bell, feed bag, breeding) without Beta APIs.
