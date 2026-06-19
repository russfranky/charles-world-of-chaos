#!/usr/bin/env python3
"""Procedural 800x450 key art stub for Marketplace marketing folder."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "marketing" / "key_art_stub_800x450.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_blocky_cow(draw: ImageDraw.ImageDraw, x: int, y: int, body: tuple, spot: tuple) -> None:
    draw.rectangle([x + 24, y + 36, x + 72, y + 88], fill=body)
    draw.rectangle([x + 32, y + 8, x + 64, y + 40], fill=body)
    draw.rectangle([x + 20, y + 44, x + 28, y + 56], fill=body)
    draw.rectangle([x + 68, y + 44, x + 76, y + 56], fill=body)
    for sx, sy in [(x + 30, y + 50), (x + 50, y + 58), (x + 38, y + 72)]:
        draw.rectangle([sx, sy, sx + 10, sy + 10], fill=spot)
    draw.rectangle([x + 40, y + 18, x + 44, y + 22], fill=(20, 20, 20))
    draw.rectangle([x + 52, y + 18, x + 56, y + 22], fill=(20, 20, 20))


def main() -> None:
    w, h = 800, 450
    img = Image.new("RGBA", (w, h), (135, 206, 235, 255))
    draw = ImageDraw.Draw(img)

    for i in range(h // 2):
        t = i / (h // 2)
        draw.line([(0, i), (w, i)], fill=(int(255 * t), int(180 + 40 * t), int(100 + 80 * t)))

    draw.polygon([(0, 280), (260, 240), (520, 270), (800, 250), (800, h), (0, h)], fill=(76, 130, 60))
    draw.rectangle([0, 320, w, h], fill=(86, 145, 70))

    draw.rectangle([40, 260, 200, 300], fill=(139, 90, 43), outline=(80, 50, 20), width=2)
    draw.text((120, 280), "COW RANCH", fill=(255, 255, 220), font=font(14, True), anchor="mm")

    draw_blocky_cow(draw, 120, 300, (160, 110, 70), (40, 30, 25))
    draw_blocky_cow(draw, 280, 290, (140, 145, 155), (60, 65, 75))
    draw_blocky_cow(draw, 440, 305, (180, 120, 80), (30, 30, 30))

    draw.text((w // 2, 48), "Brindal & Grayson", fill=(60, 40, 20), font=font(28, True), anchor="mm")
    draw.text((w // 2, 88), "Cow Ranch", fill=(40, 25, 10), font=font(42, True), anchor="mm")
    draw.text((w // 2, 130), "World Template · KEY ART STUB", fill=(80, 60, 40), font=font(14), anchor="mm")

    draw.rectangle([w - 180, h - 32, w - 16, h - 10], fill=(30, 30, 30, 200))
    draw.text((w - 98, h - 21), "800 × 450 PLACEHOLDER", fill=(200, 200, 200), font=font(10), anchor="mm")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
