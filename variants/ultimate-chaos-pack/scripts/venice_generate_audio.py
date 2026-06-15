#!/usr/bin/env python3
"""
Generate Minecraft Bedrock audio via Venice AI and write into the custom RP source tree.

Workflow:
  1. Queue audio via Venice Audio API (music or SFX models)
  2. Poll retrieve until complete
  3. Convert to OGG Vorbis with ffmpeg
  4. Write to resource_packs/brindal_grayson_cow_rp/<pack_path>
  5. Cache raw + OGG in variants/ultimate-chaos-pack/venice_audio_cache/

Requires VENICE_API_KEY environment variable. Never commit API keys.

Usage:
  export VENICE_API_KEY='your-key'
  python3 venice_generate_audio.py --list
  python3 venice_generate_audio.py --batch 1
  python3 venice_generate_audio.py --id music_game_01,sfx_levelup
  python3 venice_generate_audio.py --batch 1 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import REPO_ROOT, VARIANT_ROOT
from venice_audio_client import VeniceAudioError, generate_audio_to_ogg, quote_audio

PROMPTS_FILE = VARIANT_ROOT / "prompts" / "venice_audio_prompts.json"
CACHE_DIR = VARIANT_ROOT / "venice_audio_cache"
CUSTOM_RP = REPO_ROOT / "resource_packs" / "brindal_grayson_cow_rp"


def load_manifest() -> dict:
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def entry_dest(entry: dict) -> Path:
    return CUSTOM_RP / entry["pack_path"]


def full_prompt(entry: dict, manifest: dict) -> str:
    suffix = manifest.get("style_suffix", "")
    prompt = entry["prompt"].strip()
    if suffix:
        combined = f"{prompt} {suffix}"
    else:
        combined = prompt
    # Venice SFX models enforce a 250-char prompt cap
    if len(combined) > 250:
        combined = combined[:247].rstrip() + "..."
    return combined


def generate_entry(entry: dict, manifest: dict, *, dry_run: bool = False, force: bool = False) -> bool:
    tex_id = entry["id"]
    if entry.get("priority") == "SKIP" or entry.get("batch") == 0:
        print(f"[skip] {tex_id} — manual or pre-existing asset")
        return True

    dest = entry_dest(entry)
    cache_ogg = CACHE_DIR / f"{tex_id}.ogg"

    if dest.exists() and not force:
        print(f"[exists] {tex_id} → {dest.relative_to(REPO_ROOT)}")
        return True
    if cache_ogg.exists() and not force:
        print(f"[cache] {tex_id} — copying cached OGG")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(cache_ogg.read_bytes())
        return True

    model = entry.get("model", "elevenlabs-sound-effects-v2")
    duration = entry.get("duration_seconds")
    prompt = full_prompt(entry, manifest)

    if dry_run:
        cost = quote_audio(model=model, duration_seconds=duration) if not dry_run else 0
        print(
            f"[dry-run] {tex_id}: model={model} duration={duration}s "
            f"→ {entry['pack_path']}"
        )
        print(f"  prompt: {prompt[:120]}...")
        return True

    try:
        cost = quote_audio(model=model, duration_seconds=duration)
        print(f"[quote] {tex_id}: ${cost:.2f}")
        print(f"[generate] {tex_id} via {model} ({duration}s)...")
        generate_audio_to_ogg(
            model=model,
            prompt=prompt,
            dest=cache_ogg,
            duration_seconds=duration,
            force_instrumental=entry.get("force_instrumental"),
            trim_seconds=duration,
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(cache_ogg.read_bytes())
        print(f"  → {dest.relative_to(REPO_ROOT)}")
        return True
    except VeniceAudioError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return False


def list_entries(manifest: dict) -> None:
    for entry in manifest.get("audio", []):
        batch = entry.get("batch", "?")
        print(
            f"{entry['id']:28} batch={batch} "
            f"{entry.get('category','?'):6} "
            f"{entry.get('sound_definition_key','')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cow-world audio via Venice AI")
    parser.add_argument("--list", action="store_true", help="List all audio prompt IDs")
    parser.add_argument("--batch", type=int, help="Generate all entries in this batch number")
    parser.add_argument("--id", help="Comma-separated audio IDs")
    parser.add_argument("--all", action="store_true", help="Generate every non-SKIP entry")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling API")
    parser.add_argument("--force", action="store_true", help="Regenerate even if file exists")
    args = parser.parse_args()

    manifest = load_manifest()
    entries = manifest.get("audio", [])

    if args.list:
        list_entries(manifest)
        return

    if args.id:
        wanted = {x.strip() for x in args.id.split(",")}
        selected = [e for e in entries if e["id"] in wanted]
    elif args.batch is not None:
        selected = [e for e in entries if e.get("batch") == args.batch]
    elif args.all:
        selected = [e for e in entries if e.get("priority") != "SKIP" and e.get("batch", 0) != 0]
    else:
        parser.error("Specify --list, --batch N, --id a,b, or --all")

    ok = 0
    for entry in selected:
        if generate_entry(entry, manifest, dry_run=args.dry_run, force=args.force):
            ok += 1

    print(f"\nDone: {ok}/{len(selected)} succeeded")
    sys.exit(0 if ok == len(selected) else 1)


if __name__ == "__main__":
    main()
