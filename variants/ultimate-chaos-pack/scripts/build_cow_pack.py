#!/usr/bin/env python3
"""Cowify all resource pack textures with cow-hide patterns."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image

from common import PACK_RP, SKIP_TEXTURE_PREFIXES, VANILLA_RP, copy_vanilla_rp

COW_TEXTURE = VANILLA_RP / "textures/entity/cow/cow_v2.png"
EXCLUDE_DIRS = {"entity/cow"}
# GUI textures need precise nine-slice art — handled by cowify_gui.py only.
SKIP_TEXTURE_DIRS = {"ui", "gui"}


def should_cowify(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    for prefix in SKIP_TEXTURE_PREFIXES:
        if normalized.startswith(prefix.lstrip("/")):
            return False
    parts = Path(normalized).parts
    if parts and parts[0] in SKIP_TEXTURE_DIRS:
        return False
    if parts and parts[0] == "entity":
        # Keep vanilla mob textures; cow-hide tiling breaks mob UV sheets.
        return False
    if len(parts) >= 2 and "/".join(parts[:2]) in EXCLUDE_DIRS:
        return False
    return True


def tile_cow_pattern(cow: Image.Image, width: int, height: int, seed: int) -> Image.Image:
    """Tile cow texture across target dimensions with slight per-image variation."""
    rng = random.Random(seed)
    result = Image.new("RGBA", (width, height))
    cw, ch = cow.size

    # Slight hue shift per texture for visual variety
    r_shift = rng.randint(-15, 15)
    g_shift = rng.randint(-10, 10)
    b_shift = rng.randint(-10, 10)

    for y in range(0, height, ch):
        for x in range(0, width, cw):
            tile = cow.copy()
            if r_shift or g_shift or b_shift:
                pixels = tile.load()
                for py in range(tile.height):
                    for px in range(tile.width):
                        pr, pg, pb, pa = pixels[px, py]
                        if pa > 0:
                            pixels[px, py] = (
                                max(0, min(255, pr + r_shift)),
                                max(0, min(255, pg + g_shift)),
                                max(0, min(255, pb + b_shift)),
                                pa,
                            )
            result.paste(tile, (x, y))

    if result.size != (width, height):
        result = result.crop((0, 0, width, height))
    return result


def cowify_textures(rebuild: bool = False) -> int:
    if rebuild or not PACK_RP.exists():
        copy_vanilla_rp()
    elif not PACK_RP.exists():
        copy_vanilla_rp()

    cow = Image.open(COW_TEXTURE).convert("RGBA")
    textures_dir = PACK_RP / "textures"
    count = 0

    for png in sorted(textures_dir.rglob("*.png")):
        rel = str(png.relative_to(textures_dir))
        if not should_cowify(rel):
            continue

        try:
            original = Image.open(png).convert("RGBA")
        except Exception:
            continue

        w, h = original.size
        seed = hash(rel) & 0xFFFFFFFF
        cowified = tile_cow_pattern(cow, w, h, seed)

        # Blend 15% original for shape hints on small icons
        if w <= 32 and h <= 32:
            cowified = Image.blend(cowified, original, 0.15)

        cowified.save(png)
        count += 1

    print(f"Cowified {count} textures")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Cowify resource pack textures")
    parser.add_argument("--rebuild", action="store_true", help="Recopy vanilla before cowifying")
    args = parser.parse_args()
    cowify_textures(rebuild=args.rebuild)


if __name__ == "__main__":
    main()
