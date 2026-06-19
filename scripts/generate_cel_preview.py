#!/usr/bin/env python3
"""Generate before/after cel-toon texture preview for docs."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "variants" / "ultimate-chaos-pack" / "scripts"))

from texture_polish import (  # noqa: E402
    PROFILES,
    _bayer_dither,
    _clean_alpha,
    _despeckle,
    _edge_snap,
    _quantize,
    polish_image,
    profile_for_path,
)

PACK = ROOT / "variants" / "ultimate-chaos-pack" / "pack"
BAKED = ROOT / "variants" / "ultimate-chaos-pack" / "baked_textures"
VANILLA = ROOT / "variants" / "ultimate-chaos-pack" / "vanilla_src" / "resource_pack"
OUT = ROOT / "docs" / "assets" / "cel-toon-preview.png"

SAMPLES = (
    ("textures/blocks/grass_top.png", "Grass"),
    ("textures/blocks/stone.png", "Stone"),
    ("textures/blocks/gold_ore.png", "Gold ore"),
    ("textures/blocks/chest_front.png", "Chest"),
    ("textures/items/ranch_bell.png", "Ranch Bell"),
    ("textures/items/feed_bag.png", "Feed Bag"),
    ("textures/entity/brindal_cow.png", "Spot Cow"),
    ("textures/entity/grayson_cow.png", "Storm Cow"),
    ("textures/environment/sun.png", "Sun"),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def source_image(rel: str) -> Image.Image | None:
    """Prefer pre-cel baked procedural cache, else vanilla, else built pack."""
    for base in (BAKED, VANILLA, PACK):
        path = base / rel
        if path.exists():
            return Image.open(path).convert("RGBA")
    return None


def polish_legacy(img: Image.Image, profile: str) -> Image.Image:
    """Old dither polish (pre-cel) for side-by-side comparison."""
    opts = {
        **PROFILES.get(profile, PROFILES["default"]),
        "dither": True,
        "dither_strength": 0.35 if profile == "block" else 0.3,
        "cel_bands": 0,
        "cel_outline": False,
    }
    out = _clean_alpha(img, opts["alpha_cutoff"])
    out = _quantize(out, opts.get("max_colors", 12) + 2)
    if opts.get("dither"):
        out = _bayer_dither(out, opts["dither_strength"])
    if opts["despeckle"]:
        out = _despeckle(out)
    out = _edge_snap(out, opts["merge_dist"])
    return out


def upscale(img: Image.Image, scale: int) -> Image.Image:
    w, h = img.size
    up = img.resize((w * scale, h * scale), Image.Resampling.NEAREST)
    # Pixel grid hint
    draw = ImageDraw.Draw(up)
    for x in range(0, up.width, scale):
        draw.line([(x, 0), (x, up.height)], fill=(0, 0, 0, 40))
    for y in range(0, up.height, scale):
        draw.line([(0, y), (up.width, y)], fill=(0, 0, 0, 40))
    return up


def main() -> None:
    scale = 24
    tile = scale * 16
    cols = 2
    rows = len(SAMPLES)
    pad = 24
    header = 72
    label_h = 28
    col_w = tile + pad * 2
    row_h = tile + label_h + pad
    w = pad + cols * col_w + pad
    h = header + rows * row_h + pad

    canvas = Image.new("RGBA", (w, h), (32, 38, 48, 255))
    draw = ImageDraw.Draw(canvas)

    draw.text((w // 2, 22), "Cel / Toon Texture Bake (build-time only)", fill=(255, 255, 255), font=font(22, True), anchor="mm")
    draw.text(
        (w // 2, 52),
        "Left: old dither polish  ·  Right: cel bands + ink outline (shipped in .mcaddon)",
        fill=(180, 190, 200),
        font=font(13),
        anchor="mm",
    )

    for i, (rel, title) in enumerate(SAMPLES):
        src = source_image(rel)
        if src is None:
            continue
        prof = profile_for_path(rel)
        before = polish_legacy(src.copy(), prof)
        after = polish_image(src.copy(), prof)

        y0 = header + i * row_h
        for col, (img, label) in enumerate(((before, "Before"), (after, "Cel bake"))):
            x0 = pad + col * col_w
            up = upscale(img, scale)
            # Center in tile box
            ox = x0 + pad + (tile - up.width) // 2
            oy = y0 + pad // 2 + (tile - up.height) // 2
            canvas.paste(up, (ox, oy), up)
            draw.text((x0 + col_w // 2, y0 + tile + pad // 2), f"{title} — {label}", fill=(220, 225, 230), font=font(12, True), anchor="mm")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, format="PNG", optimize=True)
    print(f"Wrote {OUT} ({w}×{h})")


if __name__ == "__main__":
    main()
