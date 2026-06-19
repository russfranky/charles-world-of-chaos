#!/usr/bin/env python3
"""Single-page cel before/after preview (fits chat width)."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "variants" / "ultimate-chaos-pack" / "scripts"))

from texture_polish import polish_image, profile_for_path  # noqa: E402

PACK = ROOT / "variants" / "ultimate-chaos-pack" / "pack"
BAKED = ROOT / "variants" / "ultimate-chaos-pack" / "baked_textures"
CUSTOM = ROOT / "resource_packs" / "brindal_grayson_cow_rp"
OUT = ROOT / "docs" / "assets" / "cel-toon-showcase.png"

SAMPLES = (
    ("textures/blocks/grass_top.png", "Grass", BAKED),
    ("textures/blocks/gold_ore.png", "Gold ore", BAKED),
    ("textures/items/ranch_bell.png", "Ranch Bell", BAKED),
    ("textures/entity/brindal_cow.png", "Spot Cow", CUSTOM),
)


def font(size: int, bold: bool = False):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)
    except OSError:
        return ImageFont.load_default()


def load_src(rel: str, base: Path) -> Image.Image:
    p = base / rel
    if not p.exists():
        p = PACK / rel
    return Image.open(p).convert("RGBA")


def legacy(img: Image.Image, prof: str) -> Image.Image:
    from texture_polish import PROFILES, _bayer_dither, _clean_alpha, _despeckle, _edge_snap, _quantize

    o = {**PROFILES[prof], "dither": True, "dither_strength": 0.3, "cel_bands": 0, "cel_outline": False}
    x = _clean_alpha(img, o["alpha_cutoff"])
    x = _quantize(x, o["max_colors"] + 2)
    x = _bayer_dither(x, o["dither_strength"])
    if o["despeckle"]:
        x = _despeckle(x)
    return _edge_snap(x, o["merge_dist"])


def up(img: Image.Image, s: int) -> Image.Image:
    w, h = img.size
    return img.resize((w * s, h * s), Image.Resampling.NEAREST)


def main() -> None:
    scale = 16
    cell = 16 * scale
    gap = 12
    pad = 20
    cols = 2
    rows = len(SAMPLES)
    header = 64
    label = 22
    w = pad * 2 + cols * cell + (cols - 1) * gap
    h = header + pad + rows * (cell + label) + (rows - 1) * gap + pad

    canvas = Image.new("RGB", (w, h), (28, 32, 40))
    draw = ImageDraw.Draw(canvas)
    draw.text((w // 2, 18), "Before (dither)  vs  After (cel bake)", fill=(255, 255, 255), font=font(16, True), anchor="mm")
    draw.text((w // 2, 42), "Build-time only — baked into PNGs, no in-game shaders", fill=(150, 160, 170), font=font(11), anchor="mm")

    y = header + pad
    for row_idx, (rel, title, base) in enumerate(SAMPLES):
        src = load_src(rel, base)
        prof = profile_for_path(rel)
        pair = (legacy(src.copy(), prof), polish_image(src.copy(), prof))
        tags = ("Before", "Cel bake")
        row_y = y + row_idx * (cell + label + gap)
        for col, img in enumerate(pair):
            x = pad + col * (cell + gap)
            canvas.paste(up(img, scale), (x, row_y))
            draw.rectangle([x - 1, row_y - 1, x + cell, row_y + cell], outline=(80, 90, 100))
            draw.text((x + cell // 2, row_y + cell + 6), tags[col], fill=(180, 190, 200), font=font(10), anchor="mm")
        draw.text((pad + 2 * (cell + gap) + gap, row_y + cell // 2), title, fill=(255, 220, 120), font=font(11, True), anchor="lm")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT, optimize=True)
    print(f"Wrote {OUT} ({w}x{h})")


if __name__ == "__main__":
    main()
