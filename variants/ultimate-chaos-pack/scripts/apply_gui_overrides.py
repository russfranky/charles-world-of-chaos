#!/usr/bin/env python3
"""Apply JSON UI, lang, and sound overrides for cow GUI (modifications-only)."""

from __future__ import annotations

import argparse
import copy
import shutil
from pathlib import Path

from common import PACK_RP, load_json, save_json

OVERRIDES = Path(__file__).resolve().parent.parent / "gui_overrides"

COW_SAY_SOUNDS = [
    {"load_on_low_memory": True, "name": "sounds/mob/cow/say1"},
    "sounds/mob/cow/say2",
    "sounds/mob/cow/say3",
    "sounds/mob/cow/say4",
]

MENU_MUSIC_TRACK = "sounds/music/menu/Bell_At_Twilight"


def merge_json_file(src: Path, dest: Path) -> None:
    """Shallow-merge top-level keys from src into dest (for UI variable overrides)."""
    data = load_json(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        existing = load_json(dest)
        if isinstance(existing, dict) and isinstance(data, dict):
            existing.update(data)
            save_json(dest, existing)
            return
    save_json(dest, data)


def register_ui_defs() -> None:
    defs_path = PACK_RP / "ui" / "_ui_defs.json"
    if not defs_path.exists():
        return
    data = load_json(defs_path)
    ui_defs = data.get("ui_defs", [])
    entry = "ui/cow_start.json"
    if entry not in ui_defs:
        ui_defs.append(entry)
        ui_defs.sort()
        data["ui_defs"] = ui_defs
        save_json(defs_path, data)
        print(f"  Registered {entry} in _ui_defs.json")


def apply_ui_overrides() -> int:
    ui_src = OVERRIDES / "ui"
    if not ui_src.exists():
        return 0
    count = 0
    for src in sorted(ui_src.glob("*.json")):
        dest = PACK_RP / "ui" / src.name
        if src.name == "_global_variables.json":
            merge_json_file(src, dest)
        else:
            shutil.copy2(src, dest)
        count += 1
        print(f"  UI: {src.name}")
    register_ui_defs()
    return count


def apply_lang_overrides() -> int:
    lang_src = OVERRIDES / "texts" / "cow_gui.lang"
    if not lang_src.exists():
        return 0
    dest = PACK_RP / "texts" / "en_US.lang"
    dest.parent.mkdir(parents=True, exist_ok=True)
    existing = dest.read_text(encoding="utf-8").splitlines() if dest.exists() else []
    overrides: dict[str, str] = {}
    for line in lang_src.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        overrides[key] = value

    new_lines = []
    seen = set()
    for line in existing:
        if "=" in line:
            key = line.split("=", 1)[0]
            if key in overrides:
                new_lines.append(f"{key}={overrides[key]}")
                seen.add(key)
                continue
        new_lines.append(line)

    for key, value in overrides.items():
        if key not in seen:
            new_lines.append(f"{key}={value}")

    dest.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"  Lang: {len(overrides)} keys in en_US.lang")
    return len(overrides)


def apply_menu_music() -> int:
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


def apply_sound_overrides() -> int:
    path = PACK_RP / "sounds" / "sound_definitions.json"
    if not path.exists():
        return 0
    data = load_json(path)
    defs = data.get("sound_definitions", {})
    count = 0

    for name, entry in list(defs.items()):
        category = entry.get("category", "")
        if category == "ui" or name == "random.click" or name.startswith("note."):
            new_entry = copy.deepcopy(entry)
            sounds = copy.deepcopy(COW_SAY_SOUNDS)
            if isinstance(sounds[0], dict):
                sounds[0] = {**sounds[0], "volume": 0.25 if name == "random.click" else 0.35}
            new_entry["sounds"] = sounds
            defs[name] = new_entry
            count += 1

    data["sound_definitions"] = defs
    save_json(path, data)
    print(f"  Sounds: {count} UI/note events → cow moo")
    return count


def apply_gui_overrides() -> None:
    if not PACK_RP.exists():
        raise SystemExit("pack/ not found — run build pipeline first")
    print("Applying GUI overrides...")
    apply_ui_overrides()
    apply_lang_overrides()
    apply_menu_music()
    apply_sound_overrides()


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply cow GUI JSON/lang/sound overrides")
    parser.parse_args()
    apply_gui_overrides()


if __name__ == "__main__":
    main()
