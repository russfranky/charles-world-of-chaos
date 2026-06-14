# Installation Guide

## One add-on — one download

Install **`brindal-grayson-cow-pack.mcaddon`**. It includes everything: cow chaos, Brindal Cow, and Grayson Cow.

## iPad

1. [Download brindal-grayson-cow-pack.mcaddon](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-cow-pack.mcaddon)
2. Transfer via AirDrop, Files, or email
3. Tap → **Open in Minecraft**
4. Create a **NEW** world:
   - Holiday Creator Features: **ON**
   - Beta APIs: **ON**
   - Activate both **Brindal & Grayson Cow World** packs
5. Explore — or summon the kids' cows:

```
/summon bgcow:brindal_cow
/summon bgcow:grayson_cow
```

## Visual-only fallback

If experiments cause issues, use [brindal-grayson-cow-pack.mcpack](https://github.com/russfranky/brindal-grayson-cow-pack/raw/main/dist/brindal-grayson-cow-pack.mcpack) (textures only, no mob transforms).

## Build locally

```bash
pip3 install -r requirements.txt
./scripts/build-mcaddon.sh
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Packs don't appear | Re-import `.mcaddon`; restart Minecraft |
| Missing textures | Activate **both** resource and behavior packs |
| Mobs aren't cows | Enable experiments; create a **new** world |
| Brindal/Grayson cows missing | Run `/summon bgcow:brindal_cow` — they won't be transformed like other mobs |
| Import failed | Requires Minecraft Bedrock 1.21.0+ |
