#!/usr/bin/env python3
"""Apply cow-themed GUI texture replacements (texture-only, no JSON UI)."""

from __future__ import annotations

import argparse
import fnmatch
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import PACK_RP, VANILLA_RP

# Cow palette
BROWN_DARK = (72, 46, 22, 255)
BROWN_MID = (139, 90, 43, 255)
BROWN_LIGHT = (186, 140, 78, 255)
CREAM = (245, 235, 210, 255)
WHITE = (255, 255, 255, 255)
BLACK_SPOT = (35, 28, 22, 255)
MILK_BLUE = (200, 220, 255, 255)
HAY_GOLD = (210, 170, 60, 255)
DISABLED_GREY = (110, 100, 90, 200)

CONTAINER_PATTERNS = [
    "dialog_background*.png",
    "cell_image*.png",
    "background_panel.png",
    "panel_outline.png",
    "slots_bg.png",
    "screen_background.png",
    "header_bar.png",
    "dark_bg.png",
    "item_cell.png",
    "dark_background.png",
]

BUTTON_PATTERNS = [
    "button_borderless_light*.png",
    "button_borderless_dark*.png",
    "realms_button_borderless_*.png",
    "coin_button_borderless*.png",
    "csb_button_borderless_*.png",
    "NormalButtonStroke*.png",
    "NormalButtonThin*.png",
    "disabledButton*.png",
    "DarkButton*.png",
    "ButtonWithBorder*.png",
    "buttonNew.png",
]

GUI_CONTAINER_PATTERNS = CONTAINER_PATTERNS + [
    "dialog-background*.png",
    "dialog_background*.png",
]

HUD_FILES = [
    "hotbar_start_cap.png",
    "hotbar_end_cap.png",
    *[f"hotbar_{i}.png" for i in range(9)],
    "experiencebarfull.png",
    "experiencebarempty.png",
    "experience_bar_full_blue.png",
    "experience_bar_empty_blue.png",
    "experience_bar_full_white.png",
    "selected_hotbar_slot.png",
    "thumbnail_crosshair.png",
    "heart_background.png",
    "hunger_full.png",
]

TITLE_FILES = ["title.png"]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _spot_rng(seed: int) -> random.Random:
    return random.Random(seed)


def _draw_spots(
    draw: ImageDraw.ImageDraw,
    rng: random.Random,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    count: int,
    color: tuple[int, int, int, int] = BLACK_SPOT,
) -> None:
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    for _ in range(count):
        sx = x0 + rng.randint(0, max(0, w - 2))
        sy = y0 + rng.randint(0, max(0, h - 2))
        sw = rng.randint(1, min(4, w))
        sh = rng.randint(1, min(4, h))
        draw.rectangle([sx, sy, sx + sw, sy + sh], fill=color)


def _nineslice_corner(size: int, w: int, h: int) -> int:
    if w <= 4 and h <= 4:
        return 1
    if w <= 8 or h <= 8:
        return 2
    return min(4, size // 4, w // 3, h // 3)


def make_container_texture(w: int, h: int, seed: int, *, watermark: bool = False) -> Image.Image:
    img = Image.new("RGBA", (w, h), BROWN_MID)
    draw = ImageDraw.Draw(img)
    rng = _spot_rng(seed)

    if w <= 2 or h <= 2:
        _draw_spots(draw, rng, 0, 0, w, h, 1)
        return img

    corner = _nineslice_corner(max(w, h), w, h)
    if corner * 2 >= min(w, h):
        corner = max(1, min(w, h) // 3)

    # Nine-slice corners and edges — solid for stretch safety
    if w > corner * 2:
        draw.rectangle([corner, 0, w - corner - 1, corner - 1], fill=BROWN_DARK)
        draw.rectangle([corner, h - corner, w - corner - 1, h - 1], fill=BROWN_DARK)
    if h > corner * 2:
        draw.rectangle([0, corner, corner - 1, h - corner - 1], fill=BROWN_DARK)
        draw.rectangle([w - corner, corner, w - 1, h - corner - 1], fill=BROWN_DARK)

    draw.rectangle([0, 0, corner - 1, corner - 1], fill=BROWN_DARK)
    draw.rectangle([w - corner, 0, w - 1, corner - 1], fill=BROWN_DARK)
    draw.rectangle([0, h - corner, corner - 1, h - 1], fill=BROWN_DARK)
    draw.rectangle([w - corner, h - corner, w - 1, h - 1], fill=BROWN_DARK)

    cx0, cy0 = corner, corner
    cx1, cy1 = max(corner + 1, w - corner), max(corner + 1, h - corner)
    _draw_spots(draw, rng, cx0, cy0, cx1, cy1, max(1, (w * h) // 40))
    _draw_spots(draw, rng, cx0, cy0, cx1, cy1, max(1, (w * h) // 80), WHITE)

    if watermark and w >= 32 and h >= 32:
        font = _font(max(6, min(w, h) // 8))
        draw.text((corner + 1, h - corner - 8), "B&G", fill=(*CREAM[:3], 120), font=font)

    return img


def _button_variant(name: str) -> str:
    lower = name.lower()
    if "disabled" in lower:
        return "disabled"
    if "pressed" in lower or "press" in lower:
        return "pressed"
    if "hover" in lower:
        return "hover"
    return "normal"


def make_button_texture(w: int, h: int, seed: int, variant: str) -> Image.Image:
    base = {
        "normal": BROWN_MID,
        "hover": BROWN_LIGHT,
        "pressed": BROWN_DARK,
        "disabled": DISABLED_GREY,
    }[variant]
    img = Image.new("RGBA", (w, h), base)
    draw = ImageDraw.Draw(img)
    rng = _spot_rng(seed)

    spot_color = WHITE if variant == "hover" else BLACK_SPOT
    spot_count = 3 if variant == "hover" else 1
    if w <= 6:
        _draw_spots(draw, rng, 0, 0, w, h, spot_count, spot_color)
    else:
        corner = _nineslice_corner(max(w, h), w, h)
        _draw_spots(draw, rng, corner, corner, w - corner, h - corner, spot_count, spot_color)

    if variant == "pressed":
        draw.rectangle([0, 0, w - 1, h - 1], outline=BROWN_DARK)
    return img


def make_hotbar_texture(w: int, h: int, seed: int, *, cap: str | None = None) -> Image.Image:
    img = Image.new("RGBA", (w, h), BROWN_MID)
    draw = ImageDraw.Draw(img)
    rng = _spot_rng(seed)
    if cap == "start":
        for y in range(h):
            shade = int(BROWN_MID[0] * (0.85 + 0.15 * y / max(1, h - 1)))
            draw.line([(0, y), (w - 1, y)], fill=(shade, shade // 2, shade // 4, 255))
    elif cap == "end":
        for y in range(h):
            shade = int(BROWN_MID[0] * (1.0 - 0.12 * y / max(1, h - 1)))
            draw.line([(0, y), (w - 1, y)], fill=(shade, shade // 2, shade // 4, 255))
    else:
        for x in range(w):
            shade = int(BROWN_MID[0] * (0.9 + 0.1 * (x % 4) / 3))
            draw.line([(x, 0), (x, h - 1)], fill=(shade, shade // 2, shade // 4, 255))
    _draw_spots(draw, rng, 0, 0, w, h, max(1, w * h // 30))
    draw.rectangle([0, 0, w - 1, h - 1], outline=BROWN_DARK)
    return img


def make_xp_texture(w: int, h: int, *, filled: bool) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if filled:
        draw.rectangle([0, 0, w - 1, h - 1], fill=MILK_BLUE)
        draw.rectangle([1, 1, w - 2, h - 2], fill=WHITE)
        if w > 4:
            draw.rectangle([w // 3, 1, 2 * w // 3, h - 2], fill=MILK_BLUE)
    else:
        draw.rectangle([0, 0, w - 1, h - 1], outline=BROWN_LIGHT)
        draw.rectangle([1, 1, w - 2, h - 2], fill=(230, 230, 230, 180))
    return img


def make_crosshair_texture(w: int, h: int) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2
    # Cow nose print — two nostrils + muzzle oval
    draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 10], fill=BROWN_MID, outline=BROWN_DARK)
    draw.ellipse([cx - 6, cy - 1, cx - 2, cy + 3], fill=BROWN_DARK)
    draw.ellipse([cx + 2, cy - 1, cx + 6, cy + 3], fill=BROWN_DARK)
    return img


def make_title_texture(w: int, h: int) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rng = _spot_rng(42)
    _draw_spots(draw, rng, 0, 0, w, h, w // 40, BROWN_LIGHT)
    font_big = _font(72)
    font_sub = _font(28)
    draw.text((w // 2, h // 2 - 20), "MOOcraft", fill=WHITE, font=font_big, anchor="mm",
              stroke_width=4, stroke_fill=BROWN_DARK)
    draw.text((w // 2, h // 2 + 50), "Brindal & Grayson's Cow World", fill=CREAM, font=font_sub, anchor="mm",
              stroke_width=2, stroke_fill=BROWN_DARK)
    return img


def make_hotbar_slot(w: int, h: int, seed: int) -> Image.Image:
    img = make_container_texture(w, h, seed)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w - 1, h - 1], outline=CREAM, width=1)
    return img


def cowify_icons(path: Path) -> None:
    vanilla = VANILLA_RP / "textures" / "gui" / "icons.png"
    if vanilla.exists():
        img = Image.open(vanilla).convert("RGBA")
    elif path.exists():
        img = Image.open(path).convert("RGBA")
    else:
        return

    draw = ImageDraw.Draw(img)
    # Hearts region (top rows) — small cow-head ovals
    for col in range(10):
        x, y = col * 16, 0
        draw.ellipse([x + 4, y + 4, x + 12, y + 12], fill=BROWN_MID, outline=BROWN_DARK)
        draw.ellipse([x + 5, y + 7, x + 7, y + 9], fill=BROWN_DARK)
        draw.ellipse([x + 9, y + 7, x + 11, y + 9], fill=BROWN_DARK)

    # Hunger region (second row) — hay blocks
    for col in range(10):
        x, y = col * 16, 16
        draw.rectangle([x + 3, y + 6, x + 13, y + 14], fill=HAY_GOLD, outline=BROWN_DARK)
        draw.line([(x + 3, y + 9), (x + 13, y + 9)], fill=BROWN_DARK)
        draw.line([(x + 3, y + 12), (x + 13, y + 12)], fill=BROWN_DARK)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def make_heart_icon(w: int, h: int) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([1, 2, w - 2, h - 1], fill=(180, 40, 40, 255), outline=BROWN_DARK)
    draw.ellipse([w // 2 - 2, h // 2, w // 2 + 1, h // 2 + 3], fill=BROWN_DARK)
    return img


def make_hunger_icon(w: int, h: int) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 4, w - 3, h - 2], fill=HAY_GOLD, outline=BROWN_DARK)
    draw.line([(2, h // 2), (w - 3, h // 2)], fill=BROWN_DARK)
    return img


def cowify_gui_texture(path: Path, rel: str) -> bool:
    name = path.name
    w, h = Image.open(path).size
    seed = hash(rel) & 0xFFFFFFFF

    if any(fnmatch.fnmatch(name, pat) for pat in CONTAINER_PATTERNS):
        img = make_container_texture(w, h, seed, watermark=w >= 16)
    elif any(fnmatch.fnmatch(name, pat) for pat in BUTTON_PATTERNS):
        img = make_button_texture(w, h, seed, _button_variant(name))
    elif name == "hotbar_start_cap.png":
        img = make_hotbar_texture(w, h, seed, cap="start")
    elif name == "hotbar_end_cap.png":
        img = make_hotbar_texture(w, h, seed, cap="end")
    elif name.startswith("hotbar_"):
        img = make_hotbar_texture(w, h, seed)
    elif "experience" in name and "empty" in name:
        img = make_xp_texture(w, h, filled=False)
    elif "experience" in name:
        img = make_xp_texture(w, h, filled=True)
    elif name == "selected_hotbar_slot.png":
        img = make_hotbar_slot(w, h, seed)
    elif name == "thumbnail_crosshair.png":
        img = make_crosshair_texture(w, h)
    elif name == "heart_background.png":
        img = make_heart_icon(w, h)
    elif name == "hunger_full.png":
        img = make_hunger_icon(w, h)
    elif name == "title.png":
        img = make_title_texture(w, h)
    else:
        return False

    img.save(path)
    return True


def _match_patterns(directory: Path, patterns: list[str]) -> list[Path]:
    results = []
    for pat in patterns:
        results.extend(directory.glob(pat))
    return sorted(set(results))


def cowify_gui() -> dict[str, int]:
    counts = {"containers": 0, "buttons": 0, "hud": 0, "title": 0, "gui": 0}

    ui_dir = PACK_RP / "textures" / "ui"
    if ui_dir.exists():
        for path in _match_patterns(ui_dir, GUI_CONTAINER_PATTERNS):
            if cowify_gui_texture(path, str(path.relative_to(PACK_RP))):
                counts["containers"] += 1
        for path in _match_patterns(ui_dir, BUTTON_PATTERNS):
            if cowify_gui_texture(path, str(path.relative_to(PACK_RP))):
                counts["buttons"] += 1
        for name in HUD_FILES:
            path = ui_dir / name
            if path.exists() and cowify_gui_texture(path, str(path.relative_to(PACK_RP))):
                counts["hud"] += 1
        for name in TITLE_FILES:
            path = ui_dir / name
            if path.exists() and cowify_gui_texture(path, str(path.relative_to(PACK_RP))):
                counts["title"] += 1

    gui_dir = PACK_RP / "textures" / "gui"
    icons = gui_dir / "icons.png"
    if icons.exists() or (VANILLA_RP / "textures" / "gui" / "icons.png").exists():
        cowify_icons(icons)
        counts["gui"] += 1

    for sub in ("", "newgui", "newgui/buttons"):
        target = gui_dir / sub if sub else gui_dir
        if not target.exists():
            continue
        for path in _match_patterns(target, GUI_CONTAINER_PATTERNS):
            if path.name == "icons.png":
                continue
            if cowify_gui_texture(path, str(path.relative_to(PACK_RP))):
                counts["gui"] += 1
        for path in _match_patterns(target, BUTTON_PATTERNS):
            if cowify_gui_texture(path, str(path.relative_to(PACK_RP))):
                counts["gui"] += 1

    total = sum(counts.values())
    print(f"Cow GUI textures: {total} files ({counts})")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply cow-themed GUI textures")
    parser.parse_args()
    if not PACK_RP.exists():
        raise SystemExit("pack/ not found — run build_cow_pack.py first")
    cowify_gui()


if __name__ == "__main__":
    main()
