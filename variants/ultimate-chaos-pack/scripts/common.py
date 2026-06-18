"""Shared utilities for Brindal & Grayson Cow World build pipeline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import json5

VARIANT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = VARIANT_ROOT.parent.parent
CUSTOM_RP = REPO_ROOT / "resource_packs" / "brindal_grayson_cow_rp"
VANILLA_SRC = VARIANT_ROOT / "vanilla_src"
VANILLA_RP = VANILLA_SRC / "resource_pack"
VANILLA_BP = VANILLA_SRC / "behavior_pack"
PACK_RP = VARIANT_ROOT / "pack"
PACK_BP = VARIANT_ROOT / "behavior_pack"
DIST = REPO_ROOT / "dist"

# Fixed UUIDs — do not change after release (breaks existing worlds)
RP_HEADER_UUID = "d36a0504-4533-4271-b115-a49c53b7bc97"
RP_MODULE_UUID = "a89a9ce3-6524-415c-8929-fd71b12346aa"
BP_HEADER_UUID = "26cbe6c2-9ac3-464e-a6cd-08bfef85c38d"
BP_DATA_MODULE_UUID = "4a1b4f7f-01f1-4f5b-9997-b173c9b901b0"
BP_SCRIPT_MODULE_UUID = "c409dd16-412b-422a-9496-e1335c9f3ed5"

PACK_NAME_RP = "Brindal & Grayson Cow World"
PACK_NAME_BP = "Brindal & Grayson Cow World BP"

COW_IDENTIFIERS = {
    "minecraft:cow",
    "minecraft:mooshroom",
    "bgcow:brindal_cow",
    "bgcow:grayson_cow",
}

SKIP_TEXTURE_PREFIXES = (
    "textures/entity/cow/",
    "textures/entity/",
)

SKIP_ENTITY_FILES = {
    "cow.entity.json",
    "mooshroom.entity.json",
    "brindal_cow.entity.json",
    "grayson_cow.entity.json",
}

TRANSFORM_GROUP = "bgcow:transform_to_cow"

PACK_ICON_NAMES = ("pack-icon.png", "pack_icon.png")
PACK_ICON_SIZE = 128


def find_custom_pack_icon() -> Path | None:
    """Custom in-game pack icon from brindal_grayson_cow_rp source."""
    for name in PACK_ICON_NAMES:
        path = CUSTOM_RP / name
        if path.exists():
            return path
    return None


def load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json5.load(f)


def save_json(path: Path, data: dict | list, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def copy_vanilla_rp(dest: Path = PACK_RP) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(VANILLA_RP, dest)


def copy_vanilla_bp(dest: Path = PACK_BP) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(VANILLA_BP, dest)


def entity_id_from_filename(filename: str) -> str:
    base = filename.replace(".entity.json", "").replace(".json", "")
    return f"minecraft:{base}"
