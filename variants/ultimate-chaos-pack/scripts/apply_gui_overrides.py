#!/usr/bin/env python3
"""Apply JSON UI, lang, and sound overrides for cow GUI (modifications-only)."""

from __future__ import annotations

import argparse
import copy
import shutil
from pathlib import Path

from common import PACK_RP, load_json, save_json

OVERRIDES = Path(__file__).resolve().parent.parent / "gui_overrides"

# Modification-only UI files — must be registered, never replace vanilla screen defs.
COW_UI_DEFS = (
    "ui/cow_start.json",
    "ui/cow_start_screen.json",
)

COW_SAY_SOUNDS = [
    {"load_on_low_memory": True, "name": "sounds/mob/cow/say1"},
    "sounds/mob/cow/say2",
    "sounds/mob/cow/say3",
    "sounds/mob/cow/say4",
]


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
        raise SystemExit("_ui_defs.json missing — cannot register cow UI modifications")
    data = load_json(defs_path)
    ui_defs = data.get("ui_defs", [])
    added = []
    for entry in COW_UI_DEFS:
        if entry not in ui_defs:
            ui_defs.append(entry)
            added.append(entry)
    if added:
        ui_defs.sort()
        data["ui_defs"] = ui_defs
        save_json(defs_path, data)
        for entry in added:
            print(f"  Registered {entry} in _ui_defs.json")


def apply_ui_overrides(*, minimal: bool = False) -> int:
    ui_src = OVERRIDES / "ui"
    if not ui_src.exists():
        return 0
    count = 0
    for src in sorted(ui_src.glob("*.json")):
        if minimal and src.name == "_global_variables.json":
            continue
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


def apply_gui_overrides(*, minimal: bool = False) -> None:
    if not PACK_RP.exists():
        raise SystemExit("pack/ not found — run build pipeline first")
    print("Applying GUI overrides...")
    apply_ui_overrides(minimal=minimal)
    apply_lang_overrides()
    if not minimal:
        apply_sound_overrides()


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply cow GUI JSON/lang/sound overrides")
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Subtitle + pack name only — vanilla UI textures, controls, and click sounds",
    )
    args = parser.parse_args()
    apply_gui_overrides(minimal=args.minimal)


if __name__ == "__main__":
    main()
