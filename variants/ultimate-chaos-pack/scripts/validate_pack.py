#!/usr/bin/env python3
"""Validate pack structure and counts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    COW_IDENTIFIERS,
    DIST,
    PACK_BP,
    PACK_RP,
    REPO_ROOT,
    RP_HEADER_UUID,
    TRANSFORM_GROUP,
    load_json,
)

# Expected minimums for lite overlay pack
MIN_TEXTURES = 20
MIN_CUSTOM_SPAWN_RULES = 2

CUSTOM_COW_TEXTURES = (
    "textures/entity/brindal_cow.png",
    "textures/entity/grayson_cow.png",
)
CUSTOM_COW_ENTITIES = (
    "entity/brindal_cow.entity.json",
    "entity/grayson_cow.entity.json",
)

COW_UI_DEFS = (
    "ui/cow_start.json",
    "ui/cow_start_screen.json",
)

MIN_START_SCREEN_BYTES = 10_000
MAX_MCADDON_BYTES = 1_500_000


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
        description = bp.get("header", {}).get("description", "")
        if "beta api" not in description.lower():
            errors.append("BP manifest description must mention Beta APIs")

    return errors


def validate_dist_size() -> list[str]:
    errors = []
    mcaddon = DIST / "brindal-grayson-cow-pack.mcaddon"
    if mcaddon.exists() and mcaddon.stat().st_size > MAX_MCADDON_BYTES:
        errors.append(
            f"MCADDON too large: {mcaddon.stat().st_size:,} bytes > {MAX_MCADDON_BYTES:,}"
        )
    return errors


def validate_gui_lang() -> list[str]:
    errors = []
    lang_path = PACK_RP / "texts" / "en_US.lang"
    if not lang_path.exists():
        errors.append("Missing pack/texts/en_US.lang")
        return errors
    text = lang_path.read_text(encoding="utf-8").lower()
    if "menu.moo_world_subtitle" not in text:
        errors.append("Missing menu.moo_world_subtitle in RP lang")
    elif "beta api" not in text or "ranch bell" not in text:
        errors.append("Title subtitle must mention Beta APIs and Ranch Bell")
    return errors


def validate_script_api() -> list[str]:
    errors = []
    script = PACK_BP / "scripts" / "main.js"
    if not script.exists():
        return errors
    text = script.read_text(encoding="utf-8")
    for marker in ("loadBarn", "tryBreed", "BARN_KEY", "onBellTap", "catchWildCow", "showBarnMenu"):
        if marker not in text:
            errors.append(f"Script API missing reliability helper: {marker}")
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
        bp_path = PACK_BP / "entities" / name
        if not bp_path.exists():
            errors.append(f"Missing custom cow behavior: entities/{name}")
            continue
        data = load_json(bp_path)
        groups = data.get("minecraft:entity", {}).get("component_groups", {})
        if TRANSFORM_GROUP in groups:
            errors.append(f"Custom cow must not have {TRANSFORM_GROUP}: entities/{name}")
    return errors


def validate_json_files() -> list[str]:
    """Parse-check JSON and validate required top-level keys."""
    errors: list[str] = []

    for path in sorted(PACK_RP.rglob("*.json")):
        rel = path.relative_to(PACK_RP)
        try:
            data = load_json(path)
        except Exception as exc:
            errors.append(f"Invalid JSON {rel}: {exc}")
            continue

        if path.name == "manifest.json":
            if not isinstance(data, dict) or "format_version" not in data:
                errors.append(f"manifest.json missing format_version: {rel}")
            elif "header" not in data or "modules" not in data:
                errors.append(f"manifest.json missing header/modules: {rel}")
        elif path.name.endswith(".entity.json"):
            if "minecraft:client_entity" not in data and "minecraft:attachable" not in data:
                errors.append(
                    f"RP entity missing minecraft:client_entity or attachable: {rel}"
                )

    entities_dir = PACK_BP / "entities"
    if entities_dir.exists():
        for path in sorted(entities_dir.glob("*.json")):
            rel = path.relative_to(PACK_BP)
            try:
                data = load_json(path)
            except Exception as exc:
                errors.append(f"Invalid JSON {rel}: {exc}")
                continue
            if "minecraft:entity" not in data:
                errors.append(f"BP entity missing minecraft:entity: {rel}")

    for path in sorted(PACK_BP.rglob("*.json")):
        if path.parent == entities_dir:
            continue  # already checked
        rel = path.relative_to(PACK_BP)
        if path.name == "manifest.json":
            try:
                data = load_json(path)
            except Exception as exc:
                errors.append(f"Invalid JSON {rel}: {exc}")
                continue
            if not isinstance(data, dict) or "format_version" not in data:
                errors.append(f"manifest.json missing format_version: {rel}")
            elif "header" not in data or "modules" not in data:
                errors.append(f"manifest.json missing header/modules: {rel}")
            continue
        try:
            load_json(path)
        except Exception as exc:
            errors.append(f"Invalid JSON {rel}: {exc}")

    return errors


def validate_ui() -> list[str]:
    errors = []
    defs_path = PACK_RP / "ui" / "_ui_defs.json"
    if defs_path.exists():
        ui_defs = load_json(defs_path).get("ui_defs", [])
        for entry in COW_UI_DEFS:
            if entry not in ui_defs:
                errors.append(f"Missing UI def registration: {entry}")
    else:
        errors.append("Missing pack/ui/_ui_defs.json")

    for rel in COW_UI_DEFS:
        if not (PACK_RP / rel).exists():
            errors.append(f"Missing cow UI file: {rel}")

    start_screen = PACK_RP / "ui" / "start_screen.json"
    if start_screen.exists() and start_screen.stat().st_size < MIN_START_SCREEN_BYTES:
        errors.append(
            f"start_screen.json looks truncated ({start_screen.stat().st_size} bytes) "
            "— use cow_start_screen.json modifications instead"
        )

    if not (PACK_RP / "textures").exists():
        errors.append("Missing pack/textures/")
    elif not (PACK_RP / "pack_icon.png").exists():
        errors.append("Missing pack_icon.png")

    return errors


def count_custom_spawn_rules(spawn_dir: Path) -> int:
    if not spawn_dir.exists():
        return 0
    return sum(1 for p in spawn_dir.glob("*.json") if "brindal" in p.name or "grayson" in p.name)


def validate_barn_simulation() -> list[str]:
    """Run offline Cow Barn flow simulation (mirrors script_api/main.js)."""
    import subprocess

    script = REPO_ROOT / "variants/ultimate-chaos-pack/scripts/simulate_barn.py"
    if not script.exists():
        return []
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        tail = (result.stdout + result.stderr).strip().splitlines()[-5:]
        return [f"Barn simulation failed: {' | '.join(tail)}"]
    return []


def validate() -> bool:
    print("Validating Brindal & Grayson Cow World pack...")
    errors = validate_manifests()
    errors.extend(validate_custom_cows())
    errors.extend(validate_gui_lang())
    errors.extend(validate_script_api())
    errors.extend(validate_barn_simulation())
    errors.extend(validate_ui())
    errors.extend(validate_json_files())
    errors.extend(validate_dist_size())

    textures = count_pngs(PACK_RP / "textures")
    custom_spawns = count_custom_spawn_rules(PACK_BP / "spawn_rules")
    script = PACK_BP / "scripts" / "main.js"

    stats = {
        "textures": textures,
        "custom_spawn_rules": custom_spawns,
        "script_api": script.exists(),
    }

    print("Stats:")
    for key, val in stats.items():
        print(f"  {key}: {val}")

    if textures < MIN_TEXTURES:
        errors.append(f"Too few textures: {textures} < {MIN_TEXTURES}")
    if custom_spawns < MIN_CUSTOM_SPAWN_RULES:
        errors.append(f"Too few custom spawn rules: {custom_spawns} < {MIN_CUSTOM_SPAWN_RULES}")
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
