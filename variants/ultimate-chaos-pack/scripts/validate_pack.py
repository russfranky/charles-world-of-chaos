#!/usr/bin/env python3
"""Validate pack structure and counts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    COW_IDENTIFIERS,
    PACK_BP,
    PACK_RP,
    RP_HEADER_UUID,
    TRANSFORM_GROUP,
    load_json,
)

# Expected minimums (vanilla counts may vary slightly by MC version)
MIN_TEXTURES = 4000
MIN_ENTITY_OVERRIDES = 100
MIN_BP_ENTITIES = 100
MIN_SPAWN_ZEROED = 50

CUSTOM_COW_TEXTURES = (
    "textures/entity/brindal_cow.png",
    "textures/entity/grayson_cow.png",
)
CUSTOM_COW_ENTITIES = (
    "entity/brindal_cow.entity.json",
    "entity/grayson_cow.entity.json",
)
MENU_MUSIC = "sounds/music/menu/Bell_At_Twilight.ogg"


def count_pngs(directory: Path) -> int:
    return len(list(directory.rglob("*.png"))) if directory.exists() else 0


def count_entity_overrides(entity_dir: Path) -> int:
    if not entity_dir.exists():
        return 0
    count = 0
    for path in entity_dir.glob("*.entity.json"):
        if path.name in ("cow.entity.json", "mooshroom.entity.json"):
            continue
        data = load_json(path)
        desc = data.get("minecraft:client_entity", {}).get("description", {})
        geo = desc.get("geometry", {})
        if geo.get("default") == "geometry.cow.v2":
            count += 1
    return count


def count_transformed_entities(entities_dir: Path) -> int:
    if not entities_dir.exists():
        return 0
    count = 0
    for path in entities_dir.glob("*.json"):
        data = load_json(path)
        identifier = (
            data.get("minecraft:entity", {})
            .get("description", {})
            .get("identifier", "")
        )
        if identifier in COW_IDENTIFIERS:
            continue
        groups = data.get("minecraft:entity", {}).get("component_groups", {})
        if TRANSFORM_GROUP in groups:
            count += 1
    return count


def count_zeroed_spawn_rules(spawn_dir: Path) -> int:
    if not spawn_dir.exists():
        return 0
    count = 0
    for path in spawn_dir.glob("*.json"):
        data = load_json(path)
        identifier = (
            data.get("minecraft:spawn_rules", {})
            .get("description", {})
            .get("identifier", "")
        )
        if identifier in COW_IDENTIFIERS:
            continue
        conditions = data.get("minecraft:spawn_rules", {}).get("conditions", [])
        for cond in conditions:
            if cond.get("minecraft:weight", {}).get("default", 1) == 0:
                count += 1
                break
    return count


def count_cow_sounds(sounds_path: Path) -> int:
    if not sounds_path.exists():
        return 0
    data = load_json(sounds_path)
    count = 0
    entities = data.get("entity_sounds", {}).get("entities", {})
    for name, config in entities.items():
        if name == "cow":
            continue
        text = json.dumps(config)
        if "mob.cow" in text:
            count += 1
    return count


def validate_manifests() -> list[str]:
    errors = []
    rp_manifest = PACK_RP / "manifest.json"
    bp_manifest = PACK_BP / "manifest.json"

    if not rp_manifest.exists():
        errors.append("Missing pack/manifest.json")
    else:
        rp = load_json(rp_manifest)
        if rp.get("header", {}).get("uuid") != RP_HEADER_UUID:
            errors.append(f"RP UUID mismatch (expected {RP_HEADER_UUID})")

    if not bp_manifest.exists():
        errors.append("Missing behavior_pack/manifest.json")
    else:
        bp = load_json(bp_manifest)
        deps = bp.get("dependencies", [])
        if not any(d.get("uuid") == RP_HEADER_UUID for d in deps):
            errors.append("BP missing dependency on resource pack UUID")
        modules = bp.get("modules", [])
        if not any(m.get("type") == "script" for m in modules):
            errors.append("BP missing script module")

    return errors


def validate_custom_cows() -> list[str]:
    errors = []
    for rel in CUSTOM_COW_TEXTURES:
        if not (PACK_RP / rel).exists():
            errors.append(f"Missing custom cow texture: {rel}")
    for rel in CUSTOM_COW_ENTITIES:
        if not (PACK_RP / rel).exists():
            errors.append(f"Missing custom cow entity: {rel}")
    for name in ("brindal_cow.json", "grayson_cow.json"):
        if not (PACK_BP / "entities" / name).exists():
            errors.append(f"Missing custom cow behavior: entities/{name}")
    if not (PACK_RP / MENU_MUSIC).exists():
        errors.append(f"Missing menu music: {MENU_MUSIC}")
    return errors


def validate() -> bool:
    print("Validating Brindal & Grayson Cow World pack...")
    errors = validate_manifests()
    errors.extend(validate_custom_cows())

    textures = count_pngs(PACK_RP / "textures")
    entity_overrides = count_entity_overrides(PACK_RP / "entity")
    bp_entities = count_transformed_entities(PACK_BP / "entities")
    spawn_zeroed = count_zeroed_spawn_rules(PACK_BP / "spawn_rules")
    cow_sounds = count_cow_sounds(PACK_RP / "sounds.json")
    script = PACK_BP / "scripts" / "main.js"

    stats = {
        "textures": textures,
        "entity_overrides": entity_overrides,
        "bp_transformed_entities": bp_entities,
        "spawn_rules_zeroed": spawn_zeroed,
        "cow_sound_redirects": cow_sounds,
        "script_api": script.exists(),
    }

    print("Stats:")
    for key, val in stats.items():
        print(f"  {key}: {val}")

    if textures < MIN_TEXTURES:
        errors.append(f"Too few textures: {textures} < {MIN_TEXTURES}")
    if entity_overrides < MIN_ENTITY_OVERRIDES:
        errors.append(f"Too few entity overrides: {entity_overrides} < {MIN_ENTITY_OVERRIDES}")
    if bp_entities < MIN_BP_ENTITIES:
        errors.append(f"Too few transformed entities: {bp_entities} < {MIN_BP_ENTITIES}")
    if spawn_zeroed < MIN_SPAWN_ZEROED:
        errors.append(f"Too few zeroed spawn rules: {spawn_zeroed} < {MIN_SPAWN_ZEROED}")
    if not script.exists():
        errors.append("Missing behavior_pack/scripts/main.js")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  ✗ {e}")
        return False

    print("\nVALIDATION PASSED")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate pack structure")
    args = parser.parse_args()
    sys.exit(0 if validate() else 1)


if __name__ == "__main__":
    main()
