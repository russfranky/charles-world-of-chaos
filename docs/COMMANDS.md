# Cow Barn — Commands & Controls

**No typing needed** — kids tap items in their bag. Parents can use slash commands if they want.

## Play without typing (best for kids)

| What to do | What happens |
|------------|--------------|
| **Tap Ranch Bell** in your bag | Opens the **barn menu** — Deploy, Feed, Breed, Recall, or pick from **My herd** |
| **Tap Feed Bag** (wheat) on your cow | Feeds active cow — raises hunger & mood |
| **Tap Feed Bag near a wild cow** (within 5 blocks) | Catches the cow into your barn |
| **Just play** | Hunger/mood decay over time — feed your herd! |

On first join you get a **Ranch Bell**, **Feed Bag**, cookies, and one starter cow in your barn.

### Ranch Bell menu

Tap the bell to open a menu:

1. **Deploy my cow** — spawn your active cow beside you
2. **Feed my cow** — feed your active cow
3. **Breed cows** — breed two happy adults (needs Yard rank: 3+ cows)
4. **Recall / next cow** — send deployed cow back and switch to the next one
5. **My herd** — tap any cow in a list to make it active (great for kids!)

The action bar shows your barn rank, herd size, and catalog progress.

---

## Cow Barn basics

- Your herd lives in a **barn** saved on your player — up to 3 cows at Pen rank, more as you grow
- Cows have **traits**: coat, horns, size, mark — new combos unlock **catalog entries** and **real loot** (gold, emerald, diamond, diamond block…)
- **Breed** two adults with hunger 40+ and mood 55+ to get offspring with inherited (and sometimes mutated) traits
- Hungry deployed cows **recall to the barn** automatically — they don't die

### Barn ranks

| Cows in barn | Rank | Max slots |
|--------------|------|-----------|
| 1–2 | Pen | 3 |
| 3–5 | Yard | 6 |
| 6–9 | Ranch | 10 |
| 10–17 | Spread | 18 |
| 18+ | Legend | 30 |

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
| `/bgcow:next` | Switch to your next cow |

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
