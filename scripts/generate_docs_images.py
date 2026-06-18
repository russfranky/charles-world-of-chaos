#!/usr/bin/env python3
"""Generate showcase images for README and docs from pack textures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
RP = ROOT / "resource_packs" / "brindal_grayson_cow_rp"
BUILT_RP = ROOT / "variants" / "ultimate-chaos-pack" / "pack"


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


def upscale(img: Image.Image, scale: int) -> Image.Image:
    w, h = img.size
    return img.resize((w * scale, h * scale), Image.Resampling.NEAREST)


def load_tex(path: Path, scale: int = 8) -> Image.Image | None:
    if not path.exists():
        return None
    return upscale(Image.open(path).convert("RGBA"), scale)


def draw_cow_card(name: str, subtitle: str, summon_id: str, tex: Image.Image, accent: tuple, out: Path) -> None:
    card = Image.new("RGBA", (400, 480), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    # Background
    draw.rounded_rectangle([10, 10, 390, 470], radius=20, fill=(45, 62, 35, 255))
    draw.rounded_rectangle([10, 10, 390, 470], radius=20, outline=accent, width=4)
    # Grass strip
    draw.rectangle([10, 360, 390, 470], fill=(86, 125, 70, 255))
    # Cow texture centered
    cx, cy = 200, 220
    tw, th = tex.size
    card.paste(tex, (cx - tw // 2, cy - th // 2), tex)
    # Labels
    draw.text((200, 40), name, fill=accent, font=font(32, True), anchor="mm")
    draw.text((200, 78), subtitle, fill=(220, 220, 220), font=font(16), anchor="mm")
    draw.text((200, 420), f"/summon {summon_id}", fill=(255, 255, 200), font=font(13), anchor="mm")
    card.save(out)


def draw_sign(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *, post_h: int = 50) -> None:
    """Simple wooden sign with text."""
    draw.rectangle([x + 8, y + post_h - 8, x + 12, y + post_h + 30], fill=(101, 67, 33))
    draw.rectangle([x, y, x + 120, y + post_h], fill=(139, 90, 43), outline=(80, 50, 20), width=2)
    for i, line in enumerate(text.split("\n")):
        draw.text((x + 60, y + 12 + i * 14), line, fill=(255, 255, 220), font=font(11, True), anchor="mm")


def draw_mob_silhouette(draw: ImageDraw.ImageDraw, x: int, y: int, kind: str) -> None:
    """Blocky mob placeholder with cow spots."""
    colors = {
        "zombie": (60, 120, 60, 255),
        "creeper": (80, 120, 60, 255),
        "skeleton": (220, 220, 200, 255),
        "spider": (40, 40, 40, 255),
        "pig": (255, 180, 200, 255),
    }
    c = colors.get(kind, (139, 90, 43, 255))
    draw.rectangle([x + 20, y + 30, x + 60, y + 90], fill=c)
    draw.ellipse([x + 30, y + 5, x + 70, y + 40], fill=c)
    for sx, sy in [(x + 25, y + 50), (x + 45, y + 60), (x + 35, y + 75)]:
        draw.rectangle([sx, sy, sx + 8, sy + 8], fill=(30, 30, 30))


def draw_hero(out: Path) -> None:
    w, h = 1200, 500
    hero = Image.new("RGBA", (w, h), (135, 206, 235, 255))
    draw = ImageDraw.Draw(hero)

    # Sunset sky
    for i in range(h // 2):
        t = i / (h // 2)
        draw.line([(0, i), (w, i)], fill=(int(255 * t), int(180 + 40 * t), int(100 + 80 * t)))

    # Square sun
    draw.rectangle([920, 50, 1040, 170], fill=(255, 220, 80), outline=(220, 160, 40), width=3)

    # Hills and grass stage
    draw.polygon([(0, 340), (400, 280), (800, 320), (1200, 290), (1200, h), (0, h)], fill=(76, 130, 60))
    draw.rectangle([0, 380, w, h], fill=(86, 145, 70))
    draw.rectangle([100, 360, 1100, 390], fill=(101, 140, 65))  # grass block stage

    # Welcome signpost
    draw.rectangle([60, 300, 68, 380], fill=(101, 67, 33))
    draw.rectangle([20, 270, 200, 310], fill=(139, 90, 43), outline=(80, 50, 20), width=2)
    draw.text((110, 290), "Brindal & Grayson's", fill=(255, 255, 220), font=font(12, True), anchor="mm")
    draw.text((110, 302), "Cow World", fill=(255, 255, 220), font=font(11, True), anchor="mm")

    # Mob lineup with signs
    mobs = [
        (180, "zombie", "MOO?\n(Yes)"),
        (340, "creeper", "MILK ME"),
        (500, "skeleton", "We are ALL\ncows now."),
        (660, "spider", "EAT MORE\nGRASS"),
        (820, "pig", "I AM COW"),
    ]
    for x, kind, sign in mobs:
        draw_mob_silhouette(draw, x, 250, kind)
        draw_sign(draw, x, 180, sign)

    # Title
    draw.text((w // 2, 40), "Brindal & Grayson's", fill=(60, 40, 20), font=font(36, True), anchor="mm")
    draw.text((w // 2, 85), "Cow World", fill=(40, 25, 10), font=font(52, True), anchor="mm")

    # Footer badge
    draw.rectangle([w - 320, h - 36, w - 20, h - 10], fill=(30, 30, 30, 200))
    draw.text((w - 170, h - 23), "MINECRAFT BEDROCK RESOURCE PACK", fill=(220, 220, 220), font=font(12), anchor="mm")

    hero.save(out)


def draw_commands_card(out: Path) -> None:
    card = Image.new("RGBA", (800, 420), (50, 40, 30, 255))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle([8, 8, 792, 412], radius=12, outline=(255, 200, 80), width=3)

    title_font = font(28, True)
    body_font = font(17)
    draw.text((400, 35), "Cow Barn — Tap to Play", fill=(255, 220, 100), font=title_font, anchor="mm")

    commands = [
        ("Ranch Bell", "Open barn menu"),
        ("Feed Bag", "Feed or catch wild cows"),
        ("Breed", "Mix two happy adults"),
        ("/bgcow:barn", "See your herd"),
        ("/bgcow:next", "Switch active cow"),
        ("Catalog", "Discover traits + loot"),
    ]
    y = 75
    for cmd, desc in commands:
        draw.text((60, y), cmd, fill=(144, 238, 144), font=body_font)
        draw.text((280, y), desc, fill=(220, 220, 220), font=body_font)
        y += 38

    draw.text((400, 390), "Ranch Bell + Feed Bag  •  Beta APIs ON", fill=(180, 180, 180), font=font(14), anchor="mm")
    card.save(out)


def draw_install_steps(out: Path) -> None:
    """Simple 4-step install illustration."""
    w, h = 1000, 280
    img = Image.new("RGBA", (w, h), (245, 245, 240, 255))
    draw = ImageDraw.Draw(img)

    steps = [
        ("1", "Download", ".mcaddon\nin Safari"),
        ("2", "Open", "Tap →\nOpen in\nMinecraft"),
        ("3", "New World", "Holiday Creator\n+ Beta APIs"),
        ("4", "Play!", "Ranch Bell\nFeed Bag\nBreed cows"),
    ]
    colors = [(93, 173, 226), (100, 180, 100), (255, 180, 80), (200, 120, 200)]

    for i, (num, title, detail) in enumerate(steps):
        x = 30 + i * 245
        draw.rounded_rectangle([x, 30, x + 220, 250], radius=16, fill=colors[i] + (255,), outline=(60, 60, 60), width=2)
        draw.ellipse([x + 15, 45, x + 55, 85], fill=(255, 255, 255, 220))
        draw.text((x + 35, 65), num, fill=colors[i], font=font(24, True), anchor="mm")
        draw.text((x + 110, 110), title, fill=(255, 255, 255), font=font(22, True), anchor="mm")
        for j, line in enumerate(detail.split("\n")):
            draw.text((x + 110, 145 + j * 28), line, fill=(255, 255, 255), font=font(15), anchor="mm")

    img.save(out)


def copy_pack_icon(out: Path) -> None:
    src = None
    for candidate in (
        RP / "pack-icon.png",
        RP / "pack_icon.png",
    ):
        if candidate.exists():
            src = candidate
            break
    if src:
        icon = Image.open(src).convert("RGBA")
        upscale(icon, 4).save(out)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)

    brindal_tex = load_tex(RP / "textures/entity/brindal_cow.png", 8)
    grayson_tex = load_tex(RP / "textures/entity/grayson_cow.png", 8)

    if brindal_tex:
        draw_cow_card("Brindal", "Brown cow with white spots", "bgcow:brindal_cow", brindal_tex, (255, 200, 100), ASSETS / "brindal-cow.png")
    if grayson_tex:
        draw_cow_card("Grayson", "Gray cow with dark spots", "bgcow:grayson_cow", grayson_tex, (180, 180, 200), ASSETS / "grayson-cow.png")

    if brindal_tex and grayson_tex:
        together = Image.new("RGBA", (700, 400), (86, 125, 70, 255))
        d = ImageDraw.Draw(together)
        d.rectangle([0, 300, 700, 400], fill=(76, 110, 60))
        together.paste(brindal_tex, (120, 100), brindal_tex)
        together.paste(grayson_tex, (380, 100), grayson_tex)
        d.text((350, 40), "Meet the Family Cows", fill=(255, 255, 255), font=font(28, True), anchor="mm")
        d.text((200, 350), "Brindal", fill=(255, 220, 150), font=font(22, True), anchor="mm")
        d.text((500, 350), "Grayson", fill=(220, 220, 240), font=font(22, True), anchor="mm")
        together.save(ASSETS / "family-cows.png")

    draw_hero(ASSETS / "hero-banner.png")
    draw_commands_card(ASSETS / "commands-card.png")
    draw_install_steps(ASSETS / "install-steps.png")
    copy_pack_icon(ASSETS / "pack-icon.png")

    print(f"Generated images in {ASSETS}/")
    for p in sorted(ASSETS.glob("*.png")):
        print(f"  {p.name} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
