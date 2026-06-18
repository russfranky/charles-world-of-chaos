#!/usr/bin/env python3
"""Personalize the pack for Brindal & Grayson."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import (
    BP_DATA_MODULE_UUID,
    BP_HEADER_UUID,
    BP_SCRIPT_MODULE_UUID,
    PACK_BP,
    PACK_ICON_SIZE,
    PACK_NAME_BP,
    PACK_NAME_RP,
    PACK_RP,
    RP_HEADER_UUID,
    RP_MODULE_UUID,
    find_custom_pack_icon,
    save_json,
)

PACK_VERSION = [1, 0, 0]
MIN_ENGINE = [1, 21, 0]


def write_rp_manifest() -> None:
    save_json(PACK_RP / "manifest.json", {
        "format_version": 2,
        "header": {
            "name": PACK_NAME_RP,
            "description": (
                "Cow-themed blocks, GUI, and Brindal & Grayson cows. "
                "Turn ON Holiday Creator Features + Beta APIs in a NEW world."
            ),
            "uuid": RP_HEADER_UUID,
            "version": PACK_VERSION,
            "min_engine_version": MIN_ENGINE,
        },
        "modules": [{
            "type": "resources",
            "uuid": RP_MODULE_UUID,
            "version": PACK_VERSION,
        }],
    })


def write_bp_manifest() -> None:
    save_json(PACK_BP / "manifest.json", {
        "format_version": 2,
        "header": {
            "name": PACK_NAME_BP,
            "description": (
                "Cow Barn — breed and collect cows with Ranch Bell + Feed Bag. "
                "Beta APIs + Holiday Creator Features in a NEW world."
            ),
            "uuid": BP_HEADER_UUID,
            "version": PACK_VERSION,
            "min_engine_version": MIN_ENGINE,
        },
        "modules": [
            {
                "type": "data",
                "uuid": BP_DATA_MODULE_UUID,
                "version": PACK_VERSION,
            },
            {
                "type": "script",
                "language": "javascript",
                "uuid": BP_SCRIPT_MODULE_UUID,
                "version": PACK_VERSION,
                "entry": "scripts/main.js",
                "dependencies": [
                    {"module_name": "@minecraft/server", "version": "2.0.0"},
                    {"module_name": "@minecraft/server-ui", "version": "2.0.0"},
                ],
            },
        ],
        "dependencies": [{
            "uuid": RP_HEADER_UUID,
            "version": PACK_VERSION,
        }],
    })


def create_pack_icon(path: Path, letter: str, bg_color: tuple, fg_color: tuple) -> None:
    img = Image.new("RGBA", (128, 128), bg_color)
    draw = ImageDraw.Draw(img)
    # Cow body
    draw.ellipse([20, 50, 108, 110], fill=(139, 90, 43, 255))
    draw.ellipse([70, 25, 108, 65], fill=(139, 90, 43, 255))
    draw.ellipse([30, 95, 50, 120], fill=(139, 90, 43, 255))
    draw.ellipse([78, 95, 98, 120], fill=(139, 90, 43, 255))
    # Letter
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((128 - tw) // 2, 8), letter, fill=fg_color, font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def draw_letter_on_block(path: Path, letter: str, base_color: tuple, letter_color: tuple) -> None:
    """Draw a letter on a 16x16 block texture."""
    if not path.exists():
        return
    img = Image.open(path).convert("RGBA")
    # Fill with base color but keep some shading
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            _, _, _, a = pixels[x, y]
            if a > 0:
                shade = 1.0 - (y / img.height) * 0.2
                pixels[x, y] = (
                    int(base_color[0] * shade),
                    int(base_color[1] * shade),
                    int(base_color[2] * shade),
                    a,
                )

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((img.width - tw) // 2, (img.height - th) // 2 - 1), letter, fill=letter_color, font=font)
    img.save(path)


def personalize_painting() -> None:
    painting_dir = PACK_RP / "textures" / "painting"
    if not painting_dir.exists():
        return
    # Create a Brindal & Grayson painting (kristoffer_zetterstrand style 64x64)
    kz = painting_dir / "kz.png"
    if kz.exists():
        img = Image.new("RGBA", (64, 64), (135, 206, 235, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 28, 56, 56], fill=(139, 90, 43, 255))
        draw.ellipse([36, 10, 56, 30], fill=(139, 90, 43, 255))
        draw.ellipse([10, 44, 20, 58], fill=(139, 90, 43, 255))
        draw.ellipse([44, 44, 54, 58], fill=(139, 90, 43, 255))
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        except OSError:
            font = ImageFont.load_default()
        draw.text((4, 2), "B&G", fill=(255, 255, 255, 255), font=font)
        img.save(kz)


def personalize_blocks() -> None:
    blocks_dir = PACK_RP / "textures" / "blocks"
    diamond = blocks_dir / "diamond_block.png"
    gold = blocks_dir / "gold_block.png"
    draw_letter_on_block(diamond, "B", (93, 219, 213), (0, 80, 80))
    draw_letter_on_block(gold, "G", (249, 198, 40), (120, 80, 0))


def personalize_lang() -> None:
    for lang_path in [
        PACK_RP / "texts" / "en_US.lang",
        PACK_BP / "texts" / "en_US.lang",
    ]:
        if not lang_path.parent.exists():
            lang_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        if lang_path.exists():
            lines = lang_path.read_text(encoding="utf-8").splitlines()
        extra = [
            "pack.name=Brindal & Grayson Cow World",
            "pack.description=Cow fun for Brindal & Grayson! NEW world + Holiday Creator Features + Beta APIs for Cow Barn.",
            "menu.title=Brindal & Grayson's Moo World",
            "menu.moo_world_subtitle=Cow Barn · Tap Ranch Bell · My Herd to switch cows",
            "item.bgcow:ranch_bell.name=Ranch Bell",
            "item.bgcow:feed_bag.name=Feed Bag",
        ]
        existing_keys = {l.split("=")[0] for l in lines if "=" in l}
        for line in extra:
            key = line.split("=")[0]
            if key not in existing_keys:
                lines.append(line)
        lang_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _save_pack_icon(img: Image.Image, path: Path) -> None:
    """Small palette PNG for marketplace / iPad install size."""
    rgba = img.convert("RGBA")
    if rgba.size != (PACK_ICON_SIZE, PACK_ICON_SIZE):
        rgba = rgba.resize((PACK_ICON_SIZE, PACK_ICON_SIZE), Image.Resampling.LANCZOS)
    flat = Image.new("RGB", rgba.size, (0, 0, 0))
    flat.paste(rgba, mask=rgba.split()[3])
    q = flat.quantize(colors=64, method=Image.Quantize.MEDIANCUT).convert("RGB")
    q.save(path, format="PNG", optimize=True)


def apply_pack_icon() -> None:
    """Use custom pack-icon.png from source RP, or fall back to generated B/G icons."""
    src = find_custom_pack_icon()
    if src:
        img = Image.open(src).convert("RGBA")
        _save_pack_icon(img, PACK_RP / "pack_icon.png")
        # Tiny procedural icon on BP — kids see the nice art on the RP / world list.
        create_pack_icon(
            PACK_BP / "pack_icon.png",
            "G",
            (255, 215, 0, 255),
            (80, 40, 0, 255),
        )
        print(f"Applied custom pack icon from {src.name} (RP {PACK_ICON_SIZE}px, BP letter)")
        return
    create_pack_icon(PACK_RP / "pack_icon.png", "B", (135, 206, 235, 255), (255, 255, 255, 255))
    create_pack_icon(PACK_BP / "pack_icon.png", "G", (255, 215, 0, 255), (80, 40, 0, 255))


def personalize(rebuild: bool = False) -> None:
    write_rp_manifest()
    write_bp_manifest()
    apply_pack_icon()
    personalize_painting()
    personalize_blocks()
    personalize_lang()
    print("Personalized pack for Brindal & Grayson")


def main() -> None:
    parser = argparse.ArgumentParser(description="Personalize pack branding")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    personalize(rebuild=args.rebuild)


if __name__ == "__main__":
    main()
