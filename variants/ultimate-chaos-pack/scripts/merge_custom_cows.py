#!/usr/bin/env python3
"""Merge Brindal & Grayson custom cows into the built unified pack."""

from __future__ import annotations

import argparse
import shutil
import sys
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
        raise FileNotFoundError("Built pack not found — run build steps first")

    missing = []
    for src_rel, dst_rel in RP_COPY + BP_COPY:
        src = (CUSTOM_RP if src_rel.startswith(("entity/", "textures/")) else CUSTOM_BP) / src_rel
        if not src.exists():
            missing.append(str(src))
            continue
        dst = (PACK_RP if dst_rel.startswith(("entity/", "textures/")) else PACK_BP) / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    if missing:
        print("Missing required custom cow files:", file=sys.stderr)
        for path in missing:
            print(f"  ✗ {path}", file=sys.stderr)
        raise SystemExit(1)

    merge_lang(CUSTOM_RP / "texts/en_US.lang", PACK_RP / "texts/en_US.lang")
    merge_lang(CUSTOM_BP / "texts/en_US.lang", PACK_BP / "texts/en_US.lang")

    sounds_src = CUSTOM_RP / "sounds"
    if sounds_src.exists():
        copied = 0
        for src in sounds_src.rglob("*"):
            if src.is_file():
                rel = src.relative_to(sounds_src)
                dst = PACK_RP / "sounds" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
        print(f"  Copied {copied} custom sound file(s)")

    print("Merged Brindal & Grayson custom cows into unified pack")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge custom cows into unified pack")
    parser.parse_args()
    merge_custom_cows()


if __name__ == "__main__":
    main()
