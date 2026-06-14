#!/usr/bin/env python3
"""Merge Custom Cows (Brindal & Grayson) into the built Ultimate Chaos pack."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import PACK_BP, PACK_RP, REPO_ROOT

CUSTOM_RP = REPO_ROOT / "resource_packs" / "brindal_grayson_cow_rp"
CUSTOM_BP = REPO_ROOT / "behavior_packs" / "brindal_grayson_cow_bp"

RP_COPY = [
    ("entity/brindal_cow.entity.json", "entity/brindal_cow.entity.json"),
    ("entity/grayson_cow.entity.json", "entity/grayson_cow.entity.json"),
    ("textures/entity/brindal_cow.png", "textures/entity/brindal_cow.png"),
    ("textures/entity/grayson_cow.png", "textures/entity/grayson_cow.png"),
]

BP_COPY = [
    ("entities/brindal_cow.json", "entities/brindal_cow.json"),
    ("entities/grayson_cow.json", "entities/grayson_cow.json"),
    ("spawn_rules/brindal_cow.json", "spawn_rules/brindal_cow.json"),
    ("spawn_rules/grayson_cow.json", "spawn_rules/grayson_cow.json"),
]


def merge_lang(custom: Path, target: Path) -> None:
    if not custom.exists():
        return
    custom_lines = custom.read_text(encoding="utf-8").splitlines()
    existing = set()
    if target.exists():
        existing = {l.split("=")[0] for l in target.read_text(encoding="utf-8").splitlines() if "=" in l}
    merged = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
    for line in custom_lines:
        if not line.strip() or "=" not in line:
            continue
        key = line.split("=")[0]
        if key not in existing:
            merged.append(line)
            existing.add(key)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(merged) + "\n", encoding="utf-8")


def merge_custom_cows() -> None:
    if not CUSTOM_RP.exists() or not CUSTOM_BP.exists():
        raise FileNotFoundError(
            "Custom cow source packs not found in resource_packs/ and behavior_packs/"
        )
    if not PACK_RP.exists() or not PACK_BP.exists():
        raise FileNotFoundError("Built chaos pack not found — run build steps first")

    for src_rel, dst_rel in RP_COPY:
        src = CUSTOM_RP / src_rel
        dst = PACK_RP / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    for src_rel, dst_rel in BP_COPY:
        src = CUSTOM_BP / src_rel
        dst = PACK_BP / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    merge_lang(CUSTOM_RP / "texts/en_US.lang", PACK_RP / "texts/en_US.lang")
    merge_lang(CUSTOM_BP / "texts/en_US.lang", PACK_BP / "texts/en_US.lang")

    print("Merged Brindal & Grayson custom cows into unified pack")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge custom cows into chaos pack")
    args = parser.parse_args()
    merge_custom_cows()


if __name__ == "__main__":
    main()
