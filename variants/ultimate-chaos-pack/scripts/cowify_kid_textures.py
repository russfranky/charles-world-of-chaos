#!/usr/bin/env python3
"""Procedural kid-visible textures — no Venice API (baked at build time)."""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from common import PACK_RP, VARIANT_ROOT

BAKED_DIR = VARIANT_ROOT / "baked_textures"

# Cow palette
BROWN = (101, 67, 33)
SPOT = (40, 25, 12)
CREAM = (245, 222, 179)
GOLD = (218, 165, 32)
GRASS = (86, 125, 39)
GRASS_LIGHT = (106, 156, 49)
DIRT = (134, 96, 67)
DIRT_DARK = (110, 76, 48)
WHEAT = (218, 180, 58)


def _spot(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, color=SPOT) -> None:
    draw.ellipse([x, y, x + w, y + h], fill=color)


def cowify_grass_top(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), GRASS)
    draw = ImageDraw.Draw(img)
    for x in range(16):
        for y in range(16):
            if (x + y) % 3 == 0:
                draw.point((x, y), fill=GRASS_LIGHT)
    random.seed(42)
    for _ in range(5):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 3, 2)
    for _ in range(3):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 2, 2, CREAM)
    img.save(path, optimize=True)


def cowify_dirt(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), DIRT)
    draw = ImageDraw.Draw(img)
    for y in range(16):
        shade = DIRT_DARK if y % 4 == 0 else DIRT
        for x in range(16):
            draw.point((x, y), fill=shade)
    random.seed(7)
    for _ in range(6):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3)
    # tiny bell in corner
    draw.rectangle([12, 12, 15, 15], fill=GOLD)
    draw.point((13, 13), fill=(80, 60, 10))
    img.save(path, optimize=True)


def cowify_bread(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([3, 5, 13, 12], radius=2, fill=(210, 160, 90))
    draw.rounded_rectangle([4, 6, 12, 11], radius=1, fill=(230, 185, 110))
    _spot(draw, 6, 7, 2, 2, CREAM)
    _spot(draw, 9, 8, 2, 2)
    img.save(path, optimize=True)


def draw_feed_bag(path: Path) -> None:
    """Wheat item → Feed Bag look for hotbar."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Burlap sack
    draw.polygon([(4, 6), (12, 6), (13, 13), (3, 13)], fill=(180, 140, 90))
    draw.line([(4, 6), (12, 6)], fill=(140, 100, 60), width=1)
    # Wheat tufts
    for x in (5, 8, 11):
        draw.line([(x, 3), (x, 6)], fill=WHEAT, width=1)
        draw.point((x - 1, 2), fill=GRASS_LIGHT)
        draw.point((x + 1, 2), fill=GRASS_LIGHT)
    draw.rectangle([6, 8, 10, 10], fill=CREAM)
    draw.point((8, 9), fill=BROWN)
    img.save(path, optimize=True)


def draw_ranch_bell(path: Path) -> None:
    """Village bell item → golden Ranch Bell."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([7, 2, 9, 4], fill=(90, 60, 20))
    draw.polygon([(4, 5), (12, 5), (13, 12), (3, 12)], fill=GOLD)
    draw.rectangle([4, 6, 12, 11], fill=(255, 215, 80))
    _spot(draw, 6, 7, 2, 2)
    draw.ellipse([7, 11, 9, 13], fill=(60, 40, 10))
    img.save(path, optimize=True)


def apply_kid_textures(pack_rp: Path = PACK_RP, *, refresh_baked: bool = False) -> int:
    count = 0
    jobs: list[tuple[str, object]] = [
        ("textures/blocks/grass_top.png", cowify_grass_top),
        ("textures/blocks/dirt.png", cowify_dirt),
        ("textures/items/bread.png", cowify_bread),
        ("textures/items/wheat.png", draw_feed_bag),
        ("textures/items/villagebell.png", draw_ranch_bell),
    ]
    for rel, fn in jobs:
        path = pack_rp / rel
        baked = BAKED_DIR / rel
        if baked.exists() and not refresh_baked:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(baked, path)
            print(f"  baked [{rel}]")
            count += 1
            continue
        if not path.exists():
            print(f"  skip missing {rel}")
            continue
        fn(path)
        baked.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, baked)
        print(f"  procedural [{rel}]")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply procedural kid-visible cow textures")
    parser.add_argument("--pack", type=Path, default=PACK_RP)
    parser.add_argument("--refresh-baked", action="store_true", help="Regenerate baked_textures cache")
    args = parser.parse_args()
    print("Kid textures (baked cache or procedural)...")
    n = apply_kid_textures(args.pack, refresh_baked=args.refresh_baked)
    print(f"Done: {n} texture(s)")


if __name__ == "__main__":
    main()
