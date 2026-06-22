#!/usr/bin/env python3
"""
Lara Croft GO → Minecraft Bedrock 1.21+ diorama pack builder.

Single source of truth: edit PALETTE, rerun --mode all.
Spec: variants/lcgo-diorama/docs/Lara_Croft_GO_MC_Voxel_Spec.pdf
"""

from __future__ import annotations

import argparse
import json
import random
import uuid
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

VARIANT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = VARIANT_ROOT.parent.parent
DEFAULT_LEVEL = VARIANT_ROOT / "levels" / "sample_level.json"
DEFAULT_OUTPUT = REPO_ROOT / "download" / "lcgo_mc_output"

SIZE = 16
ICON_SIZE = 256

# ─── Canonical palette (spec §2.2) ───────────────────────────────────────────

PALETTE: dict[str, tuple[int, int, int]] = {
    "lit": (0xF4, 0xE4, 0xC1),
    "light_mid": (0xD4, 0xB8, 0x96),
    "dark_mid": (0x8A, 0x6F, 0x4F),
    "shadow": (0x4A, 0x35, 0x28),
    "ink": (0x1A, 0x0F, 0x08),
    "bronze": (0xB8, 0x88, 0x4A),
    "cool_blue": (0x3D, 0x6B, 0x8A),
    "moss_lit": (0xA0, 0xB8, 0x5C),
    "moss_mid": (0x6C, 0x82, 0x44),
    "moss_dark": (0x40, 0x52, 0x28),
    "bark_lit": (0xBC, 0x90, 0x5C),
    "bark_mid": (0x8C, 0x64, 0x3C),
    "bark_dark": (0x54, 0x38, 0x20),
    "dirt_lit": (0xA0, 0x74, 0x4C),
    "dirt_mid": (0x70, 0x4C, 0x30),
    "dirt_dark": (0x44, 0x2C, 0x1C),
    "water_lit": (0x8C, 0xB2, 0xC4),
    "water_mid": (0x58, 0x8A, 0x9E),
    "water_dark": (0x30, 0x58, 0x6E),
    "gold_lit": (0xF0, 0xC6, 0x5C),
    "gold_mid": (0xC0, 0x90, 0x38),
    "gold_dark": (0x82, 0x58, 0x1C),
    "jade_lit": (0x94, 0xC4, 0x9C),
    "jade_mid": (0x5C, 0x98, 0x6E),
    "jade_dark": (0x38, 0x66, 0x48),
}

LCGO_TILE_TO_MC: dict[str, str] = {
    "floor_lit": "calcite",
    "floor_light": "stone",
    "floor_dark": "deepslate",
    "floor_shadow": "bedrock",
    "wall": "cobblestone",
    "sand": "sand",
    "wood": "oak_log",
    "leaves": "leaves",
    "water": "water",
    "gold_relic": "gold_block",
    "jade_relic": "emerald_block",
    "bronze_relic": "copper_block",
}

BLOCK_TEXTURES: dict[str, dict] = {
    "calcite": {"base": "lit", "seed": 11, "spot_count": 3},
    "stone": {"base": "light_mid", "seed": 22, "spot_count": 3},
    "deepslate": {"base": "dark_mid", "seed": 33, "spot_count": 4},
    "bedrock": {"base": "shadow", "seed": 44, "spot_count": 4},
    "sand": {"base": "lit", "seed": 55, "spot_count": 2, "min_r": 1, "max_r": 3},
    "dirt": {"base": "dirt_mid", "seed": 66, "spot_count": 3, "spot_key": "moss_dark"},
    "cobblestone": {"base": "dark_mid", "seed": 77, "spot_count": 3},
    "gold_block": {"relic": "gold"},
    "emerald_block": {"relic": "jade"},
    "copper_block": {"relic": "bronze"},
}

BLOCK_PATHS = {
    "calcite": "textures/blocks/calcite.png",
    "stone": "textures/blocks/stone.png",
    "deepslate": "textures/blocks/deepslate.png",
    "bedrock": "textures/blocks/bedrock.png",
    "sand": "textures/blocks/sand.png",
    "dirt": "textures/blocks/dirt.png",
    "log_top": "textures/blocks/log_top.png",
    "log_side": "textures/blocks/log_side.png",
    "leaves_oak": "textures/blocks/leaves_oak.png",
    "water_still_greyscale": "textures/blocks/water_still_greyscale.png",
    "gold_block": "textures/blocks/gold_block.png",
    "emerald_block": "textures/blocks/emerald_block.png",
    "copper_block": "textures/blocks/copper_block.png",
    "cobblestone": "textures/blocks/cobblestone.png",
}

ITEM_PATHS = {
    "chorus_fruit": "textures/items/chorus_fruit.png",
    "zombie_head": "textures/items/zombie_head.png",
    "iron_ingot": "textures/items/iron_ingot.png",
    "prismarine_crystals": "textures/items/prismarine_crystals.png",
    "trident": "textures/items/trident.png",
}

UI_PATHS = {
    "hotbar_start_cap": "textures/ui/hotbar_start_cap.png",
    "title": "textures/ui/title.png",
}

PACK_HEADER_UUID = "a7c3e891-4f2d-4b6e-9c1a-8d4f2e6b0a31"
PACK_MODULE_UUID = "b8d4f902-5e3e-4c7f-ad2b-9e5f3f7c1b42"


def darken(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(max(0, c - amount) for c in color)


def lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, c + amount) for c in color)


def holstein_spot_mask(
    size: int, spot_count: int, seed: int, min_r: float, max_r: float
) -> set[tuple[int, int]]:
    rng = random.Random(seed)
    spots: set[tuple[int, int]] = set()
    angles = 8
    for _ in range(spot_count):
        cx = rng.randint(2, size - 3)
        cy = rng.randint(2, size - 3)
        radii = [rng.uniform(min_r, max_r) for _ in range(angles)]
        for y in range(size):
            for x in range(size):
                dx, dy = x - cx, y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist == 0:
                    angle_idx = 0
                else:
                    import math

                    angle = math.atan2(dy, dx)
                    angle_idx = int((angle + math.pi) / (2 * math.pi) * angles) % angles
                if dist < radii[angle_idx]:
                    spots.add((x, y))
    return spots


def make_block_texture(
    base_color: tuple[int, int, int],
    *,
    spot_color: tuple[int, int, int] | None = None,
    spot_count: int = 3,
    min_r: float = 2,
    max_r: float = 5,
    outline: bool = True,
    seed: int = 0,
    noise_amount: int = 10,
) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE), base_color)
    pixels = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            n = rng.randint(-noise_amount, noise_amount)
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                max(0, min(255, r + n)),
                max(0, min(255, g + n)),
                max(0, min(255, b + max(0, n // 2))),
            )
    if spot_color is None:
        spot_color = darken(base_color, 50)
    for x, y in holstein_spot_mask(SIZE, spot_count, seed + 7, min_r, max_r):
        img.putpixel((x, y), spot_color)
    if outline:
        ink = PALETTE["ink"]
        for i in range(SIZE):
            img.putpixel((i, 0), ink)
            img.putpixel((i, SIZE - 1), ink)
            img.putpixel((0, i), ink)
            img.putpixel((SIZE - 1, i), ink)
    return img


def make_log_side_texture(seed: int = 88) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE), PALETTE["bark_mid"])
    pixels = img.load()
    for x in range(SIZE):
        shade = PALETTE["bark_lit"] if rng.random() < 0.3 else (
            PALETTE["bark_dark"] if rng.random() < 0.6 else PALETTE["bark_mid"]
        )
        for y in range(SIZE):
            pixels[x, y] = shade
        if rng.random() < 0.15:
            ky = rng.randint(2, SIZE - 3)
            for dy in range(-1, 2):
                if 0 <= ky + dy < SIZE:
                    pixels[x, ky + dy] = PALETTE["bark_dark"]
    ink = PALETTE["ink"]
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img


def make_log_top_texture(seed: int = 89) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE), PALETTE["bark_lit"])
    cx, cy = SIZE // 2, SIZE // 2
    for ring in range(1, 6):
        color = darken(PALETTE["bark_lit"], ring * 25) if ring % 2 else PALETTE["bark_mid"]
        r = ring * 2
        draw = ImageDraw.Draw(img)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color)
    pixels = img.load()
    for _ in range(24):
        x, y = rng.randint(0, SIZE - 1), rng.randint(0, SIZE - 1)
        r, g, b = pixels[x, y]
        n = rng.randint(-8, 8)
        pixels[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n // 2)))
    ink = PALETTE["ink"]
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img


def make_leaves_texture(seed: int = 90) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGBA", (SIZE, SIZE), PALETTE["moss_mid"] + (255,))
    for _ in range(8):
        cx, cy = rng.randint(1, SIZE - 2), rng.randint(1, SIZE - 2)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < SIZE and 0 <= y < SIZE:
                    img.putpixel((x, y), PALETTE["moss_lit"] + (255,))
    for _ in range(6):
        x, y = rng.randint(1, SIZE - 2), rng.randint(1, SIZE - 2)
        img.putpixel((x, y), PALETTE["ink"] + (255,))
    return img


def make_water_texture(seed: int = 91) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGBA", (SIZE, SIZE), PALETTE["water_mid"] + (200,))
    pixels = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            if y in (2, 7, 12) or (rng.random() < 0.08 and y % 3 == 0):
                pixels[x, y] = PALETTE["water_lit"] + (220,)
            elif rng.random() < 0.05:
                pixels[x, y] = PALETTE["water_dark"] + (200,)
    return img


def make_relic_block_texture(
    lit_key: str, mid_key: str, dark_key: str, accent_key: str, seed: int = 0
) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE), PALETTE[mid_key])
    lit, dark, accent = PALETTE[lit_key], PALETTE[dark_key], PALETTE[accent_key]
    for y in range(4, 12):
        for x in range(4, 12):
            img.putpixel((x, y), lit)
    for y in range(5, 11):
        if y == 5 or y == 10:
            for x in range(5, 11):
                img.putpixel((x, y), lighten(lit, 20))
    corners = [(0, 0), (SIZE - 1, 0), (0, SIZE - 1), (SIZE - 1, SIZE - 1)]
    for x, y in corners:
        img.putpixel((x, y), dark)
        if x == 0:
            img.putpixel((1, y), dark)
        if x == SIZE - 1:
            img.putpixel((SIZE - 2, y), dark)
    for _ in range(4):
        x, y = rng.randint(2, SIZE - 3), rng.randint(2, SIZE - 3)
        img.putpixel((x, y), accent)
    ink = PALETTE["ink"]
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img


def _silhouette_item(
    silhouette: list[tuple[int, int]],
    body_lit: tuple[int, int, int],
    body_mid: tuple[int, int, int],
) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ink = PALETTE["ink"] + (255,)
    for y, (x0, x1) in enumerate(silhouette):
        mid_x = (x0 + x1) // 2
        for x in range(x0, x1 + 1):
            color = (body_lit if x <= mid_x else body_mid) + (255,)
            img.putpixel((x, y), color)
        img.putpixel((x0, y), ink)
        img.putpixel((x1, y), ink)
    return img


def make_incan_bottle(seed: int = 0) -> Image.Image:
    silhouette = [
        (6, 9), (6, 9), (6, 9), (6, 9),
        (5, 10),
        (4, 11), (4, 11), (4, 11),
        (4, 11), (4, 11), (4, 11),
        (5, 10), (5, 10),
        (6, 9),
    ]
    return _silhouette_item(silhouette, PALETTE["dirt_lit"], PALETTE["dirt_mid"])


def make_jade_mask(seed: int = 0) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([3, 4, 12, 13], fill=PALETTE["jade_mid"] + (255,))
    draw.ellipse([5, 7, 7, 9], fill=PALETTE["jade_dark"] + (255,))
    draw.ellipse([9, 7, 11, 9], fill=PALETTE["jade_dark"] + (255,))
    draw.ellipse([4, 5, 11, 8], fill=PALETTE["jade_lit"] + (180,))
    return img


def make_bronze_coin(seed: int = 0) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 6, 12, 14], fill=PALETTE["gold_mid"] + (255,))
    draw.ellipse([5, 7, 11, 13], fill=PALETTE["gold_lit"] + (255,))
    draw.ellipse([7, 9, 9, 11], fill=PALETTE["gold_dark"] + (255,))
    return img


def make_crystal_shard(seed: int = 0) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon([(8, 2), (12, 10), (8, 14), (4, 10)], fill=PALETTE["water_lit"] + (255,))
    draw.polygon([(8, 4), (10, 10), (8, 12), (6, 10)], fill=PALETTE["water_mid"] + (255,))
    return img


def make_spear(seed: int = 0) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.line([(8, 2), (8, 13)], fill=PALETTE["bark_mid"] + (255,), width=2)
    draw.polygon([(8, 1), (10, 5), (6, 5)], fill=PALETTE["light_mid"] + (255,))
    draw.rectangle([6, 12, 10, 14], fill=PALETTE["bronze"] + (255,))
    return img


def make_hotbar_cap() -> Image.Image:
    img = Image.new("RGBA", (16, 16), PALETTE["bronze"] + (255,))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 15, 2], fill=PALETTE["gold_lit"] + (255,))
    return img


def make_title_bg() -> Image.Image:
    img = Image.new("RGB", (256, 64), PALETTE["shadow"])
    draw = ImageDraw.Draw(img)
    for y in range(64):
        t = y / 63
        r = int(PALETTE["shadow"][0] * (1 - t) + PALETTE["lit"][0] * t)
        g = int(PALETTE["shadow"][1] * (1 - t) + PALETTE["lit"][1] * t)
        b = int(PALETTE["shadow"][2] * (1 - t) + PALETTE["lit"][2] * t)
        draw.line([(0, y), (255, y)], fill=(r, g, b))
    draw.polygon([(128, 8), (200, 50), (56, 50)], fill=PALETTE["bronze"])
    draw.ellipse([108, 4, 148, 24], fill=PALETTE["gold_lit"])
    return img


def make_pack_icon() -> Image.Image:
    img = Image.new("RGB", (ICON_SIZE, ICON_SIZE), PALETTE["lit"])
    draw = ImageDraw.Draw(img)
    cx = ICON_SIZE // 2
    draw.polygon(
        [(cx, 40), (cx + 90, ICON_SIZE - 50), (cx - 90, ICON_SIZE - 50)],
        fill=PALETTE["bronze"],
        outline=PALETTE["ink"],
    )
    draw.ellipse([cx - 50, 30, cx + 50, 90], fill=PALETTE["gold_lit"], outline=PALETTE["ink"])
    for i in range(0, ICON_SIZE, 32):
        draw.line([(i, 0), (i, ICON_SIZE)], fill=PALETTE["light_mid"], width=1)
    return img


def generate_all_textures(out_dir: Path) -> int:
    count = 0
    blocks_dir = out_dir / "textures" / "blocks"
    items_dir = out_dir / "textures" / "items"
    ui_dir = out_dir / "textures" / "ui"
    for d in (blocks_dir, items_dir, ui_dir):
        d.mkdir(parents=True, exist_ok=True)

    for name, spec in BLOCK_TEXTURES.items():
        path_key = name if name != "cobblestone" else "cobblestone"
        rel = BLOCK_PATHS.get(path_key) or BLOCK_PATHS.get(name.replace("_block", "_block"))
        if not rel:
            continue
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if "relic" in spec:
            relic = spec["relic"]
            keys = {
                "gold": ("gold_lit", "gold_mid", "gold_dark", "bronze"),
                "jade": ("jade_lit", "jade_mid", "jade_dark", "moss_lit"),
                "bronze": ("gold_lit", "gold_mid", "gold_dark", "bronze"),
            }[relic]
            img = make_relic_block_texture(*keys, seed=spec.get("seed", 100))
        else:
            base = PALETTE[spec["base"]]
            spot = PALETTE.get(spec.get("spot_key", ""))
            img = make_block_texture(
                base,
                spot_color=spot,
                spot_count=spec.get("spot_count", 3),
                min_r=spec.get("min_r", 2),
                max_r=spec.get("max_r", 5),
                seed=spec["seed"],
            )
        img.save(dest, optimize=True)
        count += 1

    make_log_side_texture().save(blocks_dir / "log_side.png", optimize=True)
    make_log_top_texture().save(blocks_dir / "log_top.png", optimize=True)
    make_leaves_texture().save(blocks_dir / "leaves_oak.png", optimize=True)
    make_water_texture().save(blocks_dir / "water_still_greyscale.png", optimize=True)
    count += 4

    items = {
        "chorus_fruit.png": make_incan_bottle,
        "zombie_head.png": make_jade_mask,
        "iron_ingot.png": make_bronze_coin,
        "prismarine_crystals.png": make_crystal_shard,
        "trident.png": make_spear,
    }
    for fname, fn in items.items():
        fn().save(items_dir / fname, optimize=True)
        count += 1

    make_hotbar_cap().save(ui_dir / "hotbar_start_cap.png", optimize=True)
    make_title_bg().save(ui_dir / "title.png", optimize=True)
    count += 2

    make_pack_icon().save(out_dir / "pack_icon.png", optimize=True)
    count += 1
    return count


def write_manifest(out_dir: Path) -> None:
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Lara Croft GO Diorama Pack",
            "description": (
                "Sunlit outdoor LC GO aesthetic: warm stone + Holstein spots + "
                "4-step cel + ink outlines"
            ),
            "uuid": PACK_HEADER_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0],
        },
        "modules": [
            {
                "type": "resources",
                "uuid": PACK_MODULE_UUID,
                "version": [1, 0, 0],
            }
        ],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def lcgo_level_to_blocks(
    level_json: dict, origin: tuple[int, int, int] = (0, 100, 0)
) -> list[tuple[int, int, int, str]]:
    blocks: list[tuple[int, int, int, str]] = []
    base_x, base_y, base_z = origin
    for tile in level_json.get("tiles", []):
        x = base_x + tile["x"]
        y = base_y + tile.get("y", 0)
        z = base_z + tile["z"]
        tile_type = tile["type"]
        block_type = LCGO_TILE_TO_MC.get(tile_type, "stone")
        if tile_type == "wall":
            blocks.append((x, y, z, "cobblestone"))
            blocks.append((x, y + 1, z, "cobblestone"))
        elif tile_type == "wood":
            blocks.append((x, y, z, "oak_log"))
            blocks.append((x, y + 1, z, "oak_log"))
            blocks.append((x, y + 2, z, "oak_log"))
            blocks.append((x, y + 3, z, "leaves"))
        elif tile_type == "leaves":
            blocks.append((x, y + 1, z, "leaves"))
            blocks.append((x, y + 2, z, "leaves"))
        else:
            mc = "water" if block_type == "water" else block_type
            if block_type == "oak_log":
                mc = "oak_log"
            elif block_type == "leaves":
                mc = "leaves"
            blocks.append((x, y, z, mc))
    return blocks


def write_conversion_outputs(blocks: list[tuple[int, int, int, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    setblock_lines = [
        "# LC GO → MC Bedrock /setblock commands",
        f"# Total blocks: {len(blocks)}",
        "# Run each line in-game as a slash command.",
        "",
    ]
    for x, y, z, bid in blocks:
        setblock_lines.append(f"setblock {x} {y} {z} {bid}")
    (out_dir / "sample_level.setblock").write_text("\n".join(setblock_lines) + "\n", encoding="utf-8")

    mcfunction = [f"setblock {x} {y} {z} {bid}" for x, y, z, bid in blocks]
    (out_dir / "lcgo_level.mcfunction").write_text("\n".join(mcfunction) + "\n", encoding="utf-8")

    py_lines = ["# Auto-generated LC GO voxel data", "BLOCKS = ["]
    for x, y, z, bid in blocks:
        py_lines.append(f"    ({x}, {y}, {z}, '{bid}'),")
    py_lines.append("]")
    (out_dir / "lcgo_blocks.py").write_text("\n".join(py_lines) + "\n", encoding="utf-8")


def assemble_mcpack(out_dir: Path, mcpack_path: Path) -> None:
    mcpack_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(mcpack_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(out_dir.rglob("*")):
            if path.is_file() and path.name != mcpack_path.name:
                arc = path.relative_to(out_dir).as_posix()
                zf.write(path, arc)


def parse_origin(s: str) -> tuple[int, int, int]:
    parts = [int(p.strip()) for p in s.split(",")]
    if len(parts) != 3:
        raise ValueError("origin must be x,y,z")
    return parts[0], parts[1], parts[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="LC GO → Minecraft Bedrock diorama tool")
    parser.add_argument(
        "--mode",
        choices=["all", "textures", "pack", "convert"],
        default="all",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--level", type=Path, default=DEFAULT_LEVEL)
    parser.add_argument("--origin", type=str, default="0,100,0")
    args = parser.parse_args()

    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    if args.mode in ("all", "textures"):
        n = generate_all_textures(out)
        print(f"Generated {n} texture(s) → {out}")

    if args.mode in ("all", "pack"):
        write_manifest(out)
        mcpack = REPO_ROOT / "download" / "Lara_Croft_GO_Diorama.mcpack"
        assemble_mcpack(out, mcpack)
        kb = mcpack.stat().st_size / 1024
        print(f"Packaged {mcpack} ({kb:.1f} KB)")

    if args.mode in ("all", "convert"):
        level = json.loads(args.level.read_text(encoding="utf-8"))
        origin = parse_origin(args.origin)
        blocks = lcgo_level_to_blocks(level, origin)
        write_conversion_outputs(blocks, out)
        level_copy = REPO_ROOT / "download" / "sample_level.json"
        level_copy.write_text(json.dumps(level, indent=2) + "\n", encoding="utf-8")
        print(f"Converted {len(blocks)} blocks → {out / 'sample_level.setblock'}")


if __name__ == "__main__":
    main()
