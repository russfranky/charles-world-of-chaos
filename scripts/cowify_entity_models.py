#!/usr/bin/env python3
"""Override client entity definitions to use cow geometry, textures, and animations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    PACK_RP,
    SKIP_ENTITY_FILES,
    copy_vanilla_rp,
    entity_id_from_filename,
    load_json,
    save_json,
)

COW_CLIENT_ENTITY = {
    "materials": {"default": "cow", "cold": "cow_cold"},
    "textures": {
        "default": "textures/entity/cow/cow_v2",
        "warm": "textures/entity/cow/cow_warm",
        "cold": "textures/entity/cow/cow_cold",
        "baby_default": "textures/entity/cow/cow_temperate_baby",
        "baby_cold": "textures/entity/cow/cow_cold_baby",
        "baby_warm": "textures/entity/cow/cow_warm_baby",
    },
    "geometry": {
        "default": "geometry.cow.v2",
        "warm": "geometry.cow.warm",
        "cold": "geometry.cow.cold",
        "baby": "geometry.cow.baby",
    },
    "animations": {
        "setup": "animation.cow.setup",
        "walk": "animation.quadruped.walk",
        "look_at_target": "animation.common.look_at_target",
        "baby_transform": "animation.cow.baby_transform",
    },
    "scripts": {
        "animate": [
            "setup",
            {"walk": "query.modified_move_speed"},
            "look_at_target",
        ],
        "pre_animation": [
            "t.variant = query.property('minecraft:climate_variant');",
            "v.index = (t.variant == 'temperate') ? 0 : ((t.variant == 'warm') ? 1 : 2);",
            "v.is_cold = t.variant == 'cold';",
        ],
        "scale": "query.is_baby ? 2.0 : 1.0",
    },
    "render_controllers": ["controller.render.cow.v3"],
}


def cowify_entity_file(path: Path) -> bool:
    if path.name in SKIP_ENTITY_FILES:
        return False

    data = load_json(path)
    entity = data.get("minecraft:client_entity", {})
    desc = entity.get("description", {})
    identifier = desc.get("identifier", entity_id_from_filename(path.name))

    if identifier in ("minecraft:cow", "minecraft:mooshroom"):
        return False

    # Preserve spawn_egg if present
    spawn_egg = desc.get("spawn_egg")

    new_desc = {
        "identifier": identifier,
        "min_engine_version": "1.8.0",
        **COW_CLIENT_ENTITY,
    }
    if spawn_egg:
        new_desc["spawn_egg"] = spawn_egg

    new_data = {
        "format_version": data.get("format_version", "1.10.0"),
        "minecraft:client_entity": {"description": new_desc},
    }
    save_json(path, new_data)
    return True


def cowify_entities(rebuild: bool = False) -> int:
    if rebuild or not PACK_RP.exists():
        copy_vanilla_rp()

    entity_dir = PACK_RP / "entity"
    count = 0
    for path in sorted(entity_dir.glob("*.entity.json")):
        if cowify_entity_file(path):
            count += 1

  # Also cowify attachables that are mob-related
    attachables_dir = PACK_RP / "attachables"
    if attachables_dir.exists():
        for path in sorted(attachables_dir.glob("*.json")):
            try:
                data = load_json(path)
                attachable = data.get("minecraft:attachable", {})
                desc = attachable.get("description", {})
                if "geometry" in desc:
                    desc["geometry"] = {"default": "geometry.cow.v2"}
                    desc["textures"] = COW_CLIENT_ENTITY["textures"]
                    desc["materials"] = COW_CLIENT_ENTITY["materials"]
                    save_json(path, data)
                    count += 1
            except (json.JSONDecodeError, KeyError):
                pass

    print(f"Cowified {count} client entity/attachable definitions")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Cowify client entity models")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    cowify_entities(rebuild=args.rebuild)


if __name__ == "__main__":
    main()
