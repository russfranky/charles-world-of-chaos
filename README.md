<p align="center">
  <img src="docs/assets/hero-banner.png" alt="Brindal & Grayson Cow World — cow-themed fun for kids on iPad" width="100%">
</p>

# Brindal & Grayson Cow World

**A Minecraft Bedrock add-on for iPad** — built for Brindal and Grayson.

Meet two named family cows in the world, use easy chat commands for cow parties and silly fun, plus a handful of cow-themed blocks and custom menu music. Vanilla mobs and controls — no broken UI.

| | |
|---|---|
| **Brindal Cow** | Brown with white spots — spawns in the world, or type `!b` |
| **Grayson Cow** | Gray with dark spots — spawns in the world, or type `!g` |
| **First join** | Brindal & Grayson greet you with wheat to feed them |
| **Commands** | `!surprise`, `!dance`, `!moo`, `!party`, and 23 more — needs **Beta APIs** |
| **Pack size** | Lite overlay (~750 KB) — fast on iPad |

<p align="center">
  <img src="docs/assets/family-cows.png" alt="Brindal Cow and Grayson Cow" width="600">
</p>

---

## iPad install (5 minutes)

<p align="center">
  <img src="docs/assets/install-steps.png" alt="Install steps: Download, Open, New World, Play" width="900">
</p>

### Step 1 — Download

Tap this link on the iPad in **Safari**:

**[Download brindal-grayson-cow-pack.mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-cow-pack.mcaddon)**

### Step 2 — Open in Minecraft

When the download finishes, tap the file → **Open in Minecraft**. Both packs import automatically.

### Step 3 — Create a NEW world

> Important: use a **new** world, not an old one.

When creating the world, turn **ON**:

- **Holiday Creator Features** — custom Brindal & Grayson cows
- **Beta APIs** — `!moo`, `!party`, and other chat commands

Then under world settings, activate **both** packs:
- Brindal & Grayson Cow World (resource)
- Brindal & Grayson Cow World BP (behavior)

### Step 4 — Play!

Open chat and try:

```
!surprise
!moo
!party
!dance
!b
!g
```

Or type `/` and search for `bgcow:` commands.

📖 **Full install guide:** [docs/installation.md](docs/installation.md)  
🎮 **All commands:** [docs/COMMANDS.md](docs/COMMANDS.md)

---

## Fun commands

<p align="center">
  <img src="docs/assets/commands-card.png" alt="Fun commands: !moo, !party, !rain, !brindal, !grayson" width="700">
</p>

| Easy (chat) | Slash command | What happens |
|-------------|---------------|--------------|
| `!moo` | `/bgcow:moo` | Spawn a cow |
| `!b` | `/bgcow:brindal` | Brindal's cow |
| `!g` | `/bgcow:grayson` | Grayson's cow |
| `!party` | `/bgcow:party` | Cow party ring |
| `!rain` | `/bgcow:rain` | Cows fall from sky |
| `!mega` | `/bgcow:mega` | MEGA cow chaos |
| `!heal` | `/bgcow:heal` | Cow magic heal |
| `!help` | `/bgcow:help` | List all commands |

**Tip for iPad:** The `!` shortcuts are easiest — kids just type in chat, no slash menu needed.

---

## Meet the cows

<p align="center">
  <img src="docs/assets/brindal-cow.png" alt="Brindal Cow" width="200">
  <img src="docs/assets/grayson-cow.png" alt="Grayson Cow" width="200">
</p>

---

## Requirements

| Requirement | Why |
|-------------|-----|
| **Minecraft Bedrock** on iPad | This is not Java Edition |
| **Version 1.21.0+** | Update the app if import fails |
| **New world** | Experiments must be set at world creation |
| **Holiday Creator Features** | Custom Brindal & Grayson cows (behavior pack) |
| **Beta APIs** | Fun commands (`!moo`, `/bgcow:party`) |

### Visual-only fallback

If experiments cause trouble, use the lighter pack (textures only, no commands):

**[brindal-grayson-cow-pack.mcpack](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-cow-pack.mcpack)**

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Commands don't work | Turn on **Beta APIs** in world settings — create a **new** world |
| Brindal/Grayson cows won't spawn | Turn on **Holiday Creator Features** — create a **new** world |
| Vanilla mobs stay normal | Expected in lite pack — kids can type `!cowify` to turn nearby mobs into cows |
| Checkerboard textures | Activate **both** resource and behavior packs |
| Packs missing | Re-download `.mcaddon`; restart Minecraft |
| Import failed | Update Minecraft to 1.21.0+ |

---

## For parents

- **[Getting Started Guide](docs/GETTING_STARTED.md)** — plain-language walkthrough
- **[Command List](docs/COMMANDS.md)** — every command explained
- **[Install Guide](docs/installation.md)** — detailed iPad steps

---

## Build from source

```bash
pip3 install -r requirements.txt
./scripts/build-mcaddon.sh                    # algorithmic + GUI
export VENICE_API_KEY='your-key'              # optional AI textures
./scripts/build-mcaddon.sh
python3 scripts/generate_docs_images.py         # regenerate README images
./scripts/clean.sh                              # remove local build artifacts
```

See [docs/development.md](docs/development.md) and [TESTING.md](TESTING.md).

---

## License

MIT — see [LICENSE](LICENSE). Minecraft assets derived from [Mojang bedrock-samples](https://github.com/Mojang/bedrock-samples).
