#!/usr/bin/env python3
"""Procedural kid-visible textures — no Venice API (baked at build time)."""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from common import PACK_RP, VARIANT_ROOT

PROCEDURAL_CREATE = frozenset({
    "textures/items/ranch_bell.png",
    "textures/items/feed_bag.png",
})

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


def cowify_cobblestone(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), (120, 120, 120))
    draw = ImageDraw.Draw(img)
    random.seed(11)
    for y in range(16):
        for x in range(16):
            base = 110 + ((x * 3 + y * 5) % 4) * 8
            draw.point((x, y), fill=(base, base, base))
    for _ in range(4):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 2, 2, (90, 90, 90))
    img.save(path, optimize=True)


def cowify_crafting_table(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), (160, 110, 60))
    draw = ImageDraw.Draw(img)
    # grid lines
    for i in (5, 10):
        draw.line([(i, 2), (i, 14)], fill=(100, 65, 30))
        draw.line([(2, i), (14, i)], fill=(100, 65, 30))
    _spot(draw, 3, 3, 2, 2, CREAM)
    _spot(draw, 11, 11, 2, 2)
    img.save(path, optimize=True)


def cowify_stone(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), (125, 125, 125))
    draw = ImageDraw.Draw(img)
    random.seed(19)
    for y in range(16):
        for x in range(16):
            shade = 115 + ((x + y * 2) % 5) * 6
            draw.point((x, y), fill=(shade, shade, shade))
    for _ in range(3):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 2, 2, CREAM)
    img.save(path, optimize=True)


def cowify_chest_front(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), (140, 95, 50))
    draw = ImageDraw.Draw(img)
    # planks
    for y in range(2, 15, 4):
        draw.line([(1, y), (14, y)], fill=(110, 70, 35))
    # metal latch
    draw.rectangle([6, 6, 10, 9], fill=(170, 170, 180))
    draw.point((8, 7), fill=(90, 90, 100))
    _spot(draw, 3, 11, 2, 2, CREAM)
    _spot(draw, 11, 3, 2, 2)
    draw.point((2, 2), fill=GOLD)
    img.save(path, optimize=True)


STONE_GRAY = (125, 125, 125)
STONE_LIGHT = (200, 200, 200)
COAL = (25, 25, 25)
IRON = (190, 160, 110)
GOLD_ORE = (218, 165, 32)
DIAMOND = (92, 219, 213)
EMERALD = (45, 180, 75)


def cowify_coal_ore(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), STONE_GRAY)
    draw = ImageDraw.Draw(img)
    random.seed(23)
    for y in range(16):
        for x in range(16):
            shade = 115 + ((x + y * 2) % 5) * 6
            draw.point((x, y), fill=(shade, shade, shade))
    for _ in range(4):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, STONE_LIGHT)
    for _ in range(5):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 2, 2, COAL)
    img.save(path, optimize=True)


def cowify_iron_ore(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), STONE_GRAY)
    draw = ImageDraw.Draw(img)
    random.seed(29)
    for y in range(16):
        for x in range(16):
            shade = 115 + ((x + y * 2) % 5) * 6
            draw.point((x, y), fill=(shade, shade, shade))
    for _ in range(3):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, SPOT)
    for _ in range(2):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, CREAM)
    for _ in range(6):
        _spot(draw, random.randint(0, 13), random.randint(0, 13), 1, 1, IRON)
    img.save(path, optimize=True)


def cowify_gold_ore(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), STONE_GRAY)
    draw = ImageDraw.Draw(img)
    random.seed(41)
    for y in range(16):
        for x in range(16):
            shade = 115 + ((x + y * 2) % 5) * 6
            draw.point((x, y), fill=(shade, shade, shade))
    for _ in range(3):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, SPOT)
    for _ in range(2):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, CREAM)
    for _ in range(6):
        _spot(draw, random.randint(0, 13), random.randint(0, 13), 1, 1, GOLD_ORE)
    img.save(path, optimize=True)


def cowify_diamond_ore(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), STONE_GRAY)
    draw = ImageDraw.Draw(img)
    random.seed(43)
    for y in range(16):
        for x in range(16):
            shade = 115 + ((x + y * 2) % 5) * 6
            draw.point((x, y), fill=(shade, shade, shade))
    for _ in range(4):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, STONE_LIGHT)
    for _ in range(2):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 2, 2, SPOT)
    for _ in range(5):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 2, 2, DIAMOND)
    img.save(path, optimize=True)


def cowify_emerald_ore(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), STONE_GRAY)
    draw = ImageDraw.Draw(img)
    random.seed(47)
    for y in range(16):
        for x in range(16):
            shade = 115 + ((x + y * 2) % 5) * 6
            draw.point((x, y), fill=(shade, shade, shade))
    for _ in range(3):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, SPOT)
    for _ in range(2):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, CREAM)
    for _ in range(6):
        _spot(draw, random.randint(0, 13), random.randint(0, 13), 1, 1, EMERALD)
    img.save(path, optimize=True)


NETHERRACK = (112, 54, 54)
NETHERRACK_DARK = (85, 38, 38)
FURNACE_STONE = (115, 115, 115)
FURNACE_DARK = (75, 75, 75)
FURNACE_GLOW = (255, 120, 40)


def cowify_netherrack(path: Path) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), NETHERRACK)
    draw = ImageDraw.Draw(img)
    random.seed(31)
    for y in range(16):
        for x in range(16):
            shade = NETHERRACK_DARK if (x + y) % 4 == 0 else NETHERRACK
            draw.point((x, y), fill=shade)
    for _ in range(5):
        _spot(draw, random.randint(0, 11), random.randint(0, 11), 3, 3, SPOT)
    for _ in range(2):
        _spot(draw, random.randint(0, 12), random.randint(0, 12), 2, 2, CREAM)
    img.save(path, optimize=True)


def cowify_furnace_front(path: Path, *, lit: bool = False) -> None:
    if not path.exists():
        return
    img = Image.new("RGBA", (16, 16), FURNACE_STONE)
    draw = ImageDraw.Draw(img)
    random.seed(37 if lit else 35)
    for y in range(16):
        for x in range(16):
            shade = 105 + ((x * 2 + y) % 4) * 8
            draw.point((x, y), fill=(shade, shade, shade))
    # cow-nose opening (dark oval)
    draw.ellipse([5, 6, 11, 12], fill=FURNACE_DARK if not lit else (40, 20, 10))
    if lit:
        draw.ellipse([6, 7, 10, 11], fill=FURNACE_GLOW)
        draw.point((8, 9), fill=(255, 200, 80))
    _spot(draw, 2, 2, 2, 2, CREAM)
    _spot(draw, 12, 13, 2, 2)
    img.save(path, optimize=True)


def apply_kid_textures(pack_rp: Path = PACK_RP, *, refresh_baked: bool = False) -> int:
    count = 0
    jobs: list[tuple[str, object]] = [
        ("textures/blocks/grass_top.png", cowify_grass_top),
        ("textures/blocks/dirt.png", cowify_dirt),
        ("textures/items/bread.png", cowify_bread),
        ("textures/items/ranch_bell.png", draw_ranch_bell),
        ("textures/items/feed_bag.png", draw_feed_bag),
        ("textures/blocks/cobblestone.png", cowify_cobblestone),
        ("textures/blocks/crafting_table_top.png", cowify_crafting_table),
        ("textures/blocks/stone.png", cowify_stone),
        ("textures/blocks/chest_front.png", cowify_chest_front),
        ("textures/blocks/coal_ore.png", cowify_coal_ore),
        ("textures/blocks/iron_ore.png", cowify_iron_ore),
        ("textures/blocks/gold_ore.png", cowify_gold_ore),
        ("textures/blocks/diamond_ore.png", cowify_diamond_ore),
        ("textures/blocks/emerald_ore.png", cowify_emerald_ore),
        ("textures/blocks/netherrack.png", cowify_netherrack),
        ("textures/blocks/furnace_front_off.png", lambda p: cowify_furnace_front(p, lit=False)),
        ("textures/blocks/furnace_front_on.png", lambda p: cowify_furnace_front(p, lit=True)),
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
        if not path.exists() and rel not in PROCEDURAL_CREATE:
            print(f"  skip missing {rel}")
            continue
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
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
