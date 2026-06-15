#!/usr/bin/env python3
"""Add behavior-pack cow transformation, zero spawn rules, and cowify loot tables."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from common import (
    COW_IDENTIFIERS,
    PACK_BP,
    TRANSFORM_GROUP,
    copy_vanilla_bp,
    entity_id_from_filename,
    load_json,
    save_json,
)

COW_LOOT_TABLE = "loot_tables/entities/cow.json"


def add_cow_transform(data: dict, identifier: str) -> bool:
    if identifier in COW_IDENTIFIERS:
        return False

    entity = data.setdefault("minecraft:entity", {})
    groups = entity.get("component_groups") or {}
    entity["component_groups"] = groups
    events = entity.get("events") or {}
    entity["events"] = events

    if TRANSFORM_GROUP in groups:
        return False

    groups[TRANSFORM_GROUP] = {
        "minecraft:transformation": {"into": "minecraft:cow"}
    }

    spawn_event = events.get("minecraft:entity_spawned", {})
    if isinstance(spawn_event, dict) and "sequence" in spawn_event:
        spawn_event["sequence"].append({
            "add": {"component_groups": [TRANSFORM_GROUP]}
        })
    elif isinstance(spawn_event, dict) and spawn_event:
        events["minecraft:entity_spawned"] = {
            "sequence": [
                copy.deepcopy(spawn_event),
                {"add": {"component_groups": [TRANSFORM_GROUP]}},
            ]
        }
    else:
        events["minecraft:entity_spawned"] = {
            "add": {"component_groups": [TRANSFORM_GROUP]}
        }

    return True


def zero_spawn_rule(path: Path) -> bool:
    data = load_json(path)
    rules = data.get("minecraft:spawn_rules", {})
    desc = rules.get("description", {})
    identifier = desc.get("identifier", "")

    if identifier in COW_IDENTIFIERS:
        return False

    conditions = rules.get("conditions", [])
    changed = False
    for cond in conditions:
        weight = cond.get("minecraft:weight", {})
        if weight.get("default", 0) != 0:
            weight["default"] = 0
            changed = True
    if changed:
        save_json(path, data)
    return changed


def cowify_loot_table(path: Path) -> bool:
    data = load_json(path)
    # Replace with cow loot reference pattern
    pools = data.get("pools", [])
    if not pools:
        return False

    cow_loot = load_json(PACK_BP / COW_LOOT_TABLE) if (PACK_BP / COW_LOOT_TABLE).exists() else None
    if cow_loot and path.name != "cow.json":
        save_json(path, copy.deepcopy(cow_loot))
        return True
    return False


def cowify_behavior(rebuild: bool = False, *, transform_mobs: bool = False) -> dict[str, int]:
    if rebuild or not PACK_BP.exists():
        copy_vanilla_bp()

    entity_count = 0
    entities_dir = PACK_BP / "entities"
    if transform_mobs:
        for path in sorted(entities_dir.glob("*.json")):
            data = load_json(path)
            identifier = (
                data.get("minecraft:entity", {})
                .get("description", {})
                .get("identifier", entity_id_from_filename(path.name))
            )
            if add_cow_transform(data, identifier):
                save_json(path, data)
                entity_count += 1

    spawn_count = 0
    spawn_dir = PACK_BP / "spawn_rules"
    for path in sorted(spawn_dir.glob("*.json")):
        if zero_spawn_rule(path):
            spawn_count += 1

    loot_count = 0
    if transform_mobs:
        loot_dir = PACK_BP / "loot_tables" / "entities"
        if loot_dir.exists():
            for path in sorted(loot_dir.glob("*.json")):
                if path.name == "cow.json":
                    continue
                if cowify_loot_table(path):
                    loot_count += 1

    stats = {
        "entities_transformed": entity_count,
        "spawn_rules_zeroed": spawn_count,
        "loot_tables_cowified": loot_count,
    }
    print(f"Behavior pack: {stats}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Cowify behavior pack entities")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument(
        "--transform-mobs",
        action="store_true",
        help="Transform all mobs into cows on spawn (off by default — too chaotic)",
    )
    args = parser.parse_args()
    cowify_behavior(rebuild=args.rebuild, transform_mobs=args.transform_mobs)


if __name__ == "__main__":
    main()
