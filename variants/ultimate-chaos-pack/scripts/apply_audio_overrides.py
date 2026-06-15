#!/usr/bin/env python3
"""Apply custom cow-world audio overrides into the built resource pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import PACK_RP, REPO_ROOT, load_json, save_json

PROMPTS_FILE = Path(__file__).resolve().parent.parent / "prompts" / "venice_audio_prompts.json"
CUSTOM_RP = REPO_ROOT / "resource_packs" / "brindal_grayson_cow_rp"
MENU_MUSIC_TRACK = "sounds/music/menu/Bell_At_Twilight"


def load_manifest() -> dict:
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def sound_name_from_pack_path(pack_path: str) -> str:
    return pack_path.replace("\\", "/").removesuffix(".ogg")


def build_sound_entry(entry: dict) -> dict:
    name = sound_name_from_pack_path(entry["pack_path"])
    if entry.get("category") == "music" or entry.get("stream"):
        return {
            "name": name,
            "stream": True,
            "volume": entry.get("volume", 0.30),
        }
    return {"name": name}


def collect_overrides(manifest: dict) -> dict[str, list[dict]]:
    """Group sound definition patches by key, preserving variant order."""
    grouped: dict[str, list[dict]] = {}

    for entry in manifest.get("audio", []):
        key = entry.get("sound_definition_key")
        pack_path = entry.get("pack_path")
        if not key or not pack_path:
            continue
        if entry.get("priority") == "SKIP":
            # Still apply if file exists (manual menu music)
            src = CUSTOM_RP / pack_path
            if not src.exists():
                continue
        else:
            src = CUSTOM_RP / pack_path
            if not src.exists():
                continue

        group = entry.get("sound_group", entry["id"])
        grouped.setdefault(key, [])
        grouped[key].append({
            "group": group,
            "sound": build_sound_entry(entry),
            "category": entry.get("category", "neutral"),
        })

    return grouped


def patch_sound_definitions(grouped: dict[str, list[dict]]) -> int:
    path = PACK_RP / "sounds" / "sound_definitions.json"
    if not path.exists() or not grouped:
        return 0

    data = load_json(path)
    defs = data.setdefault("sound_definitions", {})
    count = 0

    for key, items in grouped.items():
        # Deduplicate by sound name while preserving order
        seen = set()
        sounds = []
        category = items[0]["category"]
        for item in items:
            snd = item["sound"]
            name = snd["name"]
            if name in seen:
                continue
            seen.add(name)
            sounds.append(snd)

        base = defs.get(key, {})
        is_music = category == "music" or key.startswith("music.") or key.startswith("record.")
        new_entry = {
            "__use_legacy_max_distance": base.get("__use_legacy_max_distance", "true"),
            "category": "music" if is_music else base.get("category", category),
            "max_distance": base.get("max_distance"),
            "min_distance": base.get("min_distance"),
            "sounds": sounds,
        }
        defs[key] = new_entry
        count += 1
        print(f"  Audio: {key} → {len(sounds)} clip(s)")

    save_json(path, data)
    return count


def apply_menu_music() -> int:
    """Keep manual menu music override."""
    path = PACK_RP / "sounds" / "sound_definitions.json"
    music_file = PACK_RP / f"{MENU_MUSIC_TRACK}.ogg"
    if not path.exists() or not music_file.exists():
        return 0
    data = load_json(path)
    defs = data.get("sound_definitions", {})
    defs["music.menu"] = {
        "__use_legacy_max_distance": "true",
        "category": "music",
        "max_distance": None,
        "min_distance": None,
        "sounds": [
            {
                "name": MENU_MUSIC_TRACK,
                "stream": True,
                "volume": 0.30,
            }
        ],
    }
    data["sound_definitions"] = defs
    save_json(path, data)
    print(f"  Menu music: {MENU_MUSIC_TRACK}")
    return 1


def apply_audio_overrides() -> None:
    if not PACK_RP.exists():
        raise SystemExit("pack/ not found — run build pipeline first")

    manifest = load_manifest()
    grouped = collect_overrides(manifest)
    print("Applying audio overrides...")
    apply_menu_music()
    patch_sound_definitions(grouped)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply custom audio into built pack")
    parser.parse_args()
    apply_audio_overrides()


if __name__ == "__main__":
    main()
