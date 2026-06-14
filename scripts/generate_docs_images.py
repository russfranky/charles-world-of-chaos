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


def draw_hero(out: Path) -> None:
    w, h = 1200, 500
    hero = Image.new("RGBA", (w, h), (135, 206, 235, 255))
    draw = ImageDraw.Draw(hero)

    # Sky gradient bands
    for i in range(h // 2):
        c = int(135 + (200 - 135) * i / (h // 2))
        draw.line([(0, i), (w, i)], fill=(c, 206, 235))

    # Sun/cowbell
    draw.ellipse([950, 40, 1080, 170], fill=(255, 215, 0, 255), outline=(200, 160, 0), width=4)
    draw.rectangle([1005, 100, 1025, 140], fill=(180, 140, 0))

    # Hills
    draw.polygon([(0, 320), (300, 260), (600, 300), (900, 240), (1200, 290), (1200, h), (0, h)], fill=(76, 130, 60))
    draw.polygon([(0, 360), (400, 310), (800, 350), (1200, 300), (1200, h), (0, h)], fill=(86, 145, 70))

    brindal = load_tex(RP / "textures/entity/brindal_cow.png", 10)
    grayson = load_tex(RP / "textures/entity/grayson_cow.png", 10)
    vanilla = load_tex(BUILT_RP / "textures/entity/cow/cow_v2.png", 6)

    if brindal:
        hero.paste(brindal, (180, 240), brindal)
    if grayson:
        hero.paste(grayson, (420, 250), grayson)
    if vanilla:
        hero.paste(vanilla, (700, 220), vanilla)
        hero.paste(vanilla, (880, 260), vanilla)

    # Title banner
    draw.rounded_rectangle([40, 40, 760, 160], radius=16, fill=(40, 30, 20, 200))
    draw.text((400, 75), "Brindal & Grayson", fill=(255, 220, 100), font=font(44, True), anchor="mm")
    draw.text((400, 125), "COW WORLD", fill=(255, 255, 255), font=font(36, True), anchor="mm")

    # B & G badges
    draw.ellipse([60, 380, 110, 430], fill=(93, 219, 213), outline=(255, 255, 255), width=3)
    draw.text((85, 405), "B", fill=(0, 60, 60), font=font(28, True), anchor="mm")
    draw.ellipse([110, 380, 160, 430], fill=(249, 198, 40), outline=(255, 255, 255), width=3)
    draw.text((135, 405), "G", fill=(80, 50, 0), font=font(28, True), anchor="mm")

    draw.text((600, 460), "Minecraft Bedrock  •  iPad  •  Everything is cows!", fill=(40, 60, 30), font=font(18), anchor="mm")
    hero.save(out)


def draw_commands_card(out: Path) -> None:
    card = Image.new("RGBA", (800, 420), (50, 40, 30, 255))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle([8, 8, 792, 412], radius=12, outline=(255, 200, 80), width=3)

    title_font = font(28, True)
    body_font = font(17)
    draw.text((400, 35), "Fun Commands for Kids", fill=(255, 220, 100), font=title_font, anchor="mm")

    commands = [
        ("!moo", "Spawn a cow"),
        ("!b / !brindal", "Brindal's cow"),
        ("!g / !grayson", "Grayson's cow"),
        ("!party", "Cow party ring"),
        ("!rain", "Raining cows!"),
        ("!mega", "MEGA chaos"),
        ("!heal", "Cow magic heal"),
        ("!fly", "Levitation fun"),
    ]
    y = 75
    for cmd, desc in commands:
        draw.text((60, y), cmd, fill=(144, 238, 144), font=body_font)
        draw.text((280, y), desc, fill=(220, 220, 220), font=body_font)
        y += 38

    draw.text((400, 390), "Type in chat  •  Needs Beta APIs ON", fill=(180, 180, 180), font=font(14), anchor="mm")
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
        ("4", "Play!", "!moo  !party\n!b  !g"),
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
    src = RP / "pack_icon.png"
    if src.exists():
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
