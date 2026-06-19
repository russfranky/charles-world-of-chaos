#!/usr/bin/env python3
"""Compact cel preview strip for README / quick viewing."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "variants" / "ultimate-chaos-pack" / "scripts"))

from generate_cel_preview import (  # noqa: E402
    SAMPLES,
    font,
    polish_legacy,
    profile_for_path,
    source_image,
    upscale,
)
from texture_polish import polish_image  # noqa: E402

OUT = ROOT / "docs" / "assets" / "cel-toon-preview-compact.png"

# Pick the most kid-visible samples
PICK = (
    "textures/blocks/grass_top.png",
    "textures/blocks/gold_ore.png",
    "textures/items/ranch_bell.png",
    "textures/entity/brindal_cow.png",
)


def main() -> None:
    scale = 20
    tile = 16 * scale
    pad = 16
    header = 56
    w = pad + len(PICK) * 2 * (tile + pad) + pad
    h = header + tile + 40 + pad

    canvas = Image.new("RGBA", (w, h), (32, 38, 48, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((w // 2, 20), "Cel bake preview", fill=(255, 255, 255), font=font(18, True), anchor="mm")
    draw.text((w // 2, 42), "dither → cel bands + ink", fill=(160, 170, 180), font=font(11), anchor="mm")

    x = pad
    for rel in PICK:
        title = next(t for r, t in SAMPLES if r == rel)
        src = source_image(rel)
        if not src:
            continue
        prof = profile_for_path(rel)
        for img, sub in ((polish_legacy(src.copy(), prof), "before"), (polish_image(src.copy(), prof), "cel")):
            up = upscale(img, scale)
            canvas.paste(up, (x, header), up)
            draw.text((x + tile // 2, header + tile + 12), f"{title}", fill=(200, 205, 210), font=font(10), anchor="mm")
            draw.text((x + tile // 2, header + tile + 26), sub, fill=(140, 180, 220) if sub == "cel" else (180, 140, 140), font=font(9, True), anchor="mm")
            x += tile + pad

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
