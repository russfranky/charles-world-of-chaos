# Installation

Install **Lara Croft GO Diorama** on Minecraft Bedrock 1.21 or newer.

## Download

**[Latest release — Lara_Croft_GO_Diorama.mcpack](https://github.com/russfranky/charles-world-of-chaos/releases/latest/download/Lara_Croft_GO_Diorama.mcpack)**

Or build locally: `./scripts/build_pack.sh` → open `dist/Lara_Croft_GO_Diorama.mcpack`.

## Platform steps

### Windows / macOS

1. Double-click the `.mcpack` file (or right-click → Open with Minecraft).
2. Minecraft imports the pack automatically.
3. **Settings → Global Resources** → move **Lara Croft GO Diorama** to Active.
4. Open any world.

### iOS / iPadOS

1. Download the `.mcpack` in Safari.
2. Tap the file → **Open in Minecraft**.
3. **Settings → Global Resources** → activate the pack.
4. Open any world.

### Android

1. Download the `.mcpack`.
2. Open with Minecraft (or place in `games/com.mojang/.../resource_packs/` on some devices).
3. Activate under **Settings → Global Resources**.

## Per-world activation

Instead of global resources, you can enable the pack for a single world:

1. Edit the world → **Resource Packs**.
2. Add **Lara Croft GO Diorama** to the active list.

## Updating

Re-download the latest release `.mcpack` and import again. The pack UUID is stable across versions; newer semver replaces the previous install.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Import failed | Update Minecraft to 1.21.0+ |
| Textures unchanged | Confirm pack is in **Active** global or world resources |
| Checkerboard blocks | Pack not applied — re-import and activate |
| Java Edition | This pack is Bedrock only |

## Sample build

To place the included Cave of Snakes vignette:

```bash
python3 variants/lcgo-diorama/scripts/lcgo_mc_tool.py --mode convert \
  --level variants/lcgo-diorama/levels/sample_level.json \
  --origin 100,64,200
```

Use the generated `sample_level.setblock` commands in a command block or `/function` setup at the chosen origin.
