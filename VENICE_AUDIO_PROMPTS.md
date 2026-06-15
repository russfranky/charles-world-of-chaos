# Venice AI Audio Prompts — Cow World Sounds & Music

Prompts for generating custom music and sound effects for **Brindal & Grayson Cow World** via [Venice AI](https://venice.ai). Used by `variants/ultimate-chaos-pack/scripts/venice_generate_audio.py`.

## Setup

```bash
export VENICE_API_KEY='your-venice-inference-key'
# or copy .env.example → .env and source it
```

**Never commit API keys.** Rotate your key if it was ever shared in chat.

## Models (June 2026)

| Venice Model | Use for | Cost (approx) |
|--------------|---------|---------------|
| `ace-step-15` | Instrumental music loops (60s) | ~$0.03/track |
| `elevenlabs-sound-effects-v2` | Short SFX (1–22s) | ~$0.01/clip |
| `stable-audio-25` | Long ambient loops | ~$0.24/clip |
| `elevenlabs-music` | High-quality instrumental (optional) | ~$0.87/min |

Music outputs FLAC → converted to **OGG Vorbis** for Bedrock via ffmpeg.

## Usage

```bash
# List all audio IDs
python3 variants/ultimate-chaos-pack/scripts/venice_generate_audio.py --list

# Generate batch 1 (core music + iconic SFX)
python3 variants/ultimate-chaos-pack/scripts/venice_generate_audio.py --batch 1

# Specific clips
python3 variants/ultimate-chaos-pack/scripts/venice_generate_audio.py --id music_game_01,sfx_levelup

# During full build
python3 variants/ultimate-chaos-pack/scripts/build_all.py --rebuild-textures --venice-audio
```

Generated files land in `resource_packs/brindal_grayson_cow_rp/sounds/` and are merged into the pack at build time.

## Already done (manual)

| Asset | Path |
|-------|------|
| Menu music | `sounds/music/menu/Bell_At_Twilight.ogg` |

## Batch 1 — core (generate first)

| ID | Type | Bedrock key |
|----|------|-------------|
| `music_game_01` / `02` | Music | `music.game` |
| `music_creative_01` | Music | `music.game.creative` |
| `music_water_01` | Music | `music.game.water` |
| `music_nether_01` | Music | `music.game.nether` |
| `sfx_levelup` | SFX | `random.levelup` |
| `sfx_chest_open` | SFX | `random.chestopen` |
| `sfx_explode` | SFX | `random.explode` |
| `sfx_orb` | SFX | `random.orb` |
| `sfx_portal_travel` | SFX | `portal.travel` |
| `sfx_portal_trigger` | SFX | `portal.trigger` |

## Batch 2–4

See `variants/ultimate-chaos-pack/prompts/venice_audio_prompts.json` for dig/step sounds, weather, records, and biome music.

## Style anchor

> Short instrumental stinger: golden cowbells, gentle acoustic guitar, soft cartoon moo harmony, pastoral meadow, Minecraft adventure mood, no vocals.

Match the comedy tone of texture prompts in `venice_prompts.json` — silly, warm, kid-safe.

## Pipeline

1. `venice_generate_audio.py` → writes OGG into custom RP source
2. `merge_custom_cows.py` → copies `sounds/` into built pack
3. `apply_audio_overrides.py` → patches `sound_definitions.json`

Mob sounds remain algorithmically cowified via `cowify_sounds.py` (vanilla cow moos).

Cached generations: `variants/ultimate-chaos-pack/venice_audio_cache/` (gitignored).
