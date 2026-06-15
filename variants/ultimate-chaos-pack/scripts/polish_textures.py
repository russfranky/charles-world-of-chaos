#!/usr/bin/env python3
"""Polish pack textures for crisp Minecraft pixel art (post-Venice / post-import)."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from common import CUSTOM_RP, PACK_RP, REPO_ROOT
from texture_polish import polish_image, profile_for_path

CUSTOM_ENTITY_TEXTURES = (
    CUSTOM_RP / "textures/entity/brindal_cow.png",
    CUSTOM_RP / "textures/entity/grayson_cow.png",
)


def polish_pack(pack_root: Path = PACK_RP) -> tuple[int, int]:
    if not pack_root.exists():
        raise FileNotFoundError(f"Pack not found: {pack_root}")

    count = 0
    changed = 0
    textures = pack_root / "textures"
    targets: list[Path] = []

    if textures.exists():
        targets.extend(sorted(textures.rglob("*.png")))
    icon = pack_root / "pack_icon.png"
    if icon.exists():
        targets.append(icon)

    for path in targets:
        rel = str(path.relative_to(pack_root))
        prof = profile_for_path(rel)
        before = path.read_bytes()
        img = Image.open(path).convert("RGBA")
        out = polish_image(img, prof)
        out.save(path, format="PNG")
        after = path.read_bytes()
        count += 1
        if before != after:
            changed += 1
            print(f"  polished [{prof}] {rel}")

    return count, changed


def polish_custom_sources() -> int:
    n = 0
    for path in CUSTOM_ENTITY_TEXTURES:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGBA")
        polish_image(img, "entity").save(path, format="PNG")
        print(f"  polished source {path.relative_to(REPO_ROOT)}")
        n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Polish Minecraft textures to pixel-art quality")
    parser.add_argument("--pack", type=Path, default=PACK_RP, help="Built resource pack dir")
    parser.add_argument("--sources", action="store_true", help="Also polish custom cow source PNGs")
    args = parser.parse_args()

    print("Texture polish pipeline...")
    if args.sources:
        polish_custom_sources()
    total, changed = polish_pack(args.pack)
    print(f"Done: {changed}/{total} textures updated")


if __name__ == "__main__":
    main()
