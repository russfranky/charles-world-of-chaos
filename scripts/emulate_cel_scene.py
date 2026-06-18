#!/usr/bin/env python3
"""
Emulate how cel-baked textures look in a simple Minecraft-style scene.
Build-time textures only — no game engine. Runs in cloud CI.
"""

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
VANILLA = ROOT / "variants" / "ultimate-chaos-pack" / "vanilla_src" / "resource_pack"
OUT_DIR = ROOT / "docs" / "assets" / "cel-emulation"


def font(size: int, bold: bool = False):
    try:
        n = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{n}", size)
    except OSError:
        return ImageFont.load_default()


def load_raw(rel: str) -> Image.Image:
    for base in (BAKED, CUSTOM, VANILLA, PACK):
        p = base / rel
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(rel)


def legacy_polish(img: Image.Image, prof: str) -> Image.Image:
    from texture_polish import PROFILES, _bayer_dither, _clean_alpha, _despeckle, _edge_snap, _quantize

    o = {**PROFILES[prof], "dither": True, "dither_strength": 0.32, "cel_bands": 0, "cel_outline": False}
    x = _clean_alpha(img, o["alpha_cutoff"])
    x = _quantize(x, o["max_colors"] + 2)
    x = _bayer_dither(x, o["dither_strength"])
    if o["despeckle"]:
        x = _despeckle(x)
    return _edge_snap(x, o["merge_dist"])


def tile(tex: Image.Image, cols: int, rows: int, scale: int) -> Image.Image:
    s = tex.resize((16 * scale, 16 * scale), Image.Resampling.NEAREST)
    w, h = s.size
    out = Image.new("RGBA", (w * cols, h * rows))
    for row in range(rows):
        for col in range(cols):
            out.paste(s, (col * w, row * h), s)
    return out


def draw_hotbar(
    draw: ImageDraw.ImageDraw,
    items: list[Image.Image | None],
    selected: int,
    y: int,
    w: int,
    scale: int,
) -> None:
    """Minecraft-style 9-slot hotbar with selected highlight and XP strip."""
    slots = 9
    slot_sz = 20 * scale
    gap = 2 * scale
    pad = 4 * scale
    bar_h = slot_sz + pad * 2
    total_w = slots * slot_sz + (slots - 1) * gap + pad * 2
    x0 = (w - total_w) // 2

    # Cow-hide bar strip (dark brown, like in-game HUD)
    draw.rounded_rectangle(
        [x0, y, x0 + total_w, y + bar_h],
        radius=6 * scale // 2,
        fill=(42, 28, 18, 210),
        outline=(90, 62, 38, 255),
        width=max(1, scale // 2),
    )

    slot_x0 = x0 + pad
    icon_sz = 16 * scale
    for i in range(slots):
        sx = slot_x0 + i * (slot_sz + gap)
        sy = y + pad
        inner = (28, 18, 12, 180) if i != selected else (55, 38, 24, 220)
        draw.rectangle([sx, sy, sx + slot_sz, sy + slot_sz], fill=inner)
        if i == selected:
            draw.rectangle(
                [sx - scale, sy - scale, sx + slot_sz + scale, sy + slot_sz + scale],
                outline=(255, 255, 255, 230),
                width=max(2, scale),
            )
        else:
            draw.rectangle([sx, sy, sx + slot_sz, sy + slot_sz], outline=(70, 48, 30, 180))
        icon = items[i] if i < len(items) else None
        if icon is not None:
            ic = icon.resize((icon_sz, icon_sz), Image.Resampling.NEAREST)
            ox = sx + (slot_sz - ic.width) // 2
            oy = sy + (slot_sz - ic.height) // 2
            draw._image.paste(ic, (ox, oy), ic)

    # XP bar above hotbar
    xp_y = y - 6 * scale
    xp_w = total_w - pad * 2
    xp_h = max(4, scale)
    xp_x = x0 + pad
    draw.rectangle([xp_x, xp_y, xp_x + xp_w, xp_y + xp_h], fill=(20, 14, 10, 200), outline=(60, 42, 28))
    draw.rectangle([xp_x + 1, xp_y + 1, xp_x + int(xp_w * 0.62), xp_y + xp_h - 1], fill=(80, 200, 255))


def build_scene(tex_map: dict[str, Image.Image], title: str) -> Image.Image:
    """Fake third-person ranch view using 16x16 tiles."""
    scale = 6
    sky_h = 80 * scale
    ground_rows = 5
    ground_cols = 14
    ground = tile(tex_map["grass"], ground_cols, ground_rows, scale)
    stone_strip = tile(tex_map["stone"], ground_cols, 1, scale)
    ore_patch = tile(tex_map["gold_ore"], 3, 2, scale)
    diamond_pad = tile(tex_map["diamond_block"], 2, 1, scale)
    tnt_block = tex_map["tnt_top"].resize((16 * scale, 16 * scale), Image.Resampling.NEAREST)

    w = ground.width
    h = sky_h + ground.height + stone_strip.height
    scene = Image.new("RGBA", (w, h), (135, 206, 235, 255))

    # Sun
    sun = tex_map["sun"].resize((32 * scale, 32 * scale), Image.Resampling.NEAREST)
    scene.paste(sun, (w - sun.width - 20, 20), sun)

    # Ground layers
    scene.paste(ground, (0, sky_h), ground)
    scene.paste(stone_strip, (0, sky_h + ground.height), stone_strip)
    scene.paste(ore_patch, (w // 3, sky_h + ground.height - ore_patch.height), ore_patch)

    # Diamond block marker pad (lite-pack landmark block)
    pad_x = w // 2 - diamond_pad.width // 2
    pad_y = sky_h + ground.height - diamond_pad.height
    scene.paste(diamond_pad, (pad_x, pad_y), diamond_pad)

    # TNT block beside ore patch
    tnt_x = w // 3 + ore_patch.width + scale * 2
    tnt_y = sky_h + ground.height - tnt_block.height
    scene.paste(tnt_block, (tnt_x, tnt_y), tnt_block)

    # Chest on diamond pad
    chest = tex_map["chest"].resize((16 * scale, 16 * scale), Image.Resampling.NEAREST)
    cx = w // 2 - chest.width // 2
    cy = pad_y - chest.height + scale
    scene.paste(chest, (cx, cy), chest)

    # Cow sprite (entity UV center crop — show full sheet scaled)
    cow = tex_map["cow"]
    cow_show = cow.resize((cow.width * 3, cow.height * 3), Image.Resampling.NEAREST)
    scene.paste(cow_show, (w // 4, sky_h + scale * 8), cow_show)

    draw = ImageDraw.Draw(scene)
    hotbar_items: list[Image.Image | None] = [
        tex_map["bell"],
        tex_map["bag"],
        tex_map["bread"],
        tex_map["diamond_block"],
        tex_map["tnt_top"],
        None,
        None,
        None,
        None,
    ]
    hotbar_y = h - 34 * scale
    draw_hotbar(draw, hotbar_items, selected=0, y=hotbar_y, w=w, scale=scale)
    draw.rectangle([0, 0, w, 28 * scale], fill=(0, 0, 0, 140))
    draw.text((w // 2, 14 * scale), title, fill=(255, 255, 255), font=font(14, True), anchor="mm")
    return scene


def make_texture_set(cel: bool) -> dict[str, Image.Image]:
    paths = {
        "grass": "textures/blocks/grass_top.png",
        "stone": "textures/blocks/stone.png",
        "gold_ore": "textures/blocks/gold_ore.png",
        "diamond_block": "textures/blocks/diamond_block.png",
        "tnt_top": "textures/blocks/tnt_top.png",
        "chest": "textures/blocks/chest_front.png",
        "bell": "textures/items/ranch_bell.png",
        "bag": "textures/items/feed_bag.png",
        "bread": "textures/items/bread.png",
        "cow": "textures/entity/brindal_cow.png",
        "sun": "textures/environment/sun.png",
    }
    out: dict[str, Image.Image] = {}
    for key, rel in paths.items():
        raw = load_raw(rel)
        prof = profile_for_path(rel)
        out[key] = polish_image(raw.copy(), prof) if cel else legacy_polish(raw.copy(), prof)
    return out


def write_html(paths: dict[str, Path]) -> None:
    import base64

    def b64(p: Path) -> str:
        return base64.standard_b64encode(p.read_bytes()).decode("ascii")

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<title>Cel / Toon Texture Emulation</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #1a1e28; color: #e8eaed; margin: 24px; }}
  h1 {{ font-size: 1.4rem; }}
  p {{ color: #9aa0a6; max-width: 720px; }}
  img {{ max-width: 100%; height: auto; border: 2px solid #3c4043; border-radius: 8px; margin: 16px 0; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 16px; }}
  .row img {{ flex: 1; min-width: 280px; }}
</style></head><body>
<h1>Cel / Toon bake — cloud emulation</h1>
<p>Build-time PNG bake only (no in-game shaders). Generated by <code>scripts/emulate_cel_scene.py</code> in CI/cloud.</p>
<h2>In-world scene</h2>
<div class="row">
  <figure><img src="data:image/png;base64,{b64(paths['scene_before'])}" alt="Before"/><figcaption>Before (dither polish)</figcaption></figure>
  <figure><img src="data:image/png;base64,{b64(paths['scene_cel'])}" alt="Cel"/><figcaption>After (cel bake — shipped)</figcaption></figure>
</div>
<h2>Texture pairs</h2>
<img src="data:image/png;base64,{b64(paths['pairs'])}" alt="Texture pairs"/>
<h2>Full sheet</h2>
<img src="data:image/png;base64,{b64(paths['sheet'])}" alt="Full sheet"/>
</body></html>"""
    paths["html"].write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Building texture sets...")
    before = make_texture_set(cel=False)
    after = make_texture_set(cel=True)

    print("Rendering emulated scenes...")
    scene_before = build_scene(before, "BEFORE — dither polish")
    scene_cel = build_scene(after, "AFTER — cel bake (shipped in .mcaddon)")

    # Side-by-side composite
    gap = 16
    combo_h = max(scene_before.height, scene_cel.height)
    combo = Image.new("RGBA", (scene_before.width + scene_cel.width + gap, combo_h + 48), (28, 32, 40, 255))
    combo.paste(scene_before, (0, 40))
    combo.paste(scene_cel, (scene_before.width + gap, 40))
    draw = ImageDraw.Draw(combo)
    draw.text((combo.width // 2, 16), "Minecraft-style emulation (cloud render)", fill=(255, 255, 255), font=font(18, True), anchor="mm")

    paths = {
        "scene_before": OUT_DIR / "scene-before.png",
        "scene_cel": OUT_DIR / "scene-cel.png",
        "combo": OUT_DIR / "scene-comparison.png",
        "pairs": OUT_DIR / "texture-pairs.png",
        "sheet": OUT_DIR / "texture-sheet.png",
        "html": OUT_DIR / "index.html",
    }
    scene_before.save(paths["scene_before"])
    scene_cel.save(paths["scene_cel"])
    combo.save(paths["combo"])

    # Reuse existing generators
    import subprocess

    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "generate_cel_showcase.py")], cwd=ROOT)
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "generate_cel_preview.py")], cwd=ROOT)
    paths["pairs"] = ROOT / "docs" / "assets" / "cel-toon-showcase.png"
    paths["sheet"] = ROOT / "docs" / "assets" / "cel-toon-preview.png"
    shutil_copy = __import__("shutil")
    shutil_copy.copy2(paths["pairs"], OUT_DIR / "texture-pairs.png")
    shutil_copy.copy2(paths["sheet"], OUT_DIR / "texture-sheet.png")

    write_html(paths)
    print(f"Emulation complete → {OUT_DIR}/")
    for name, p in paths.items():
        if p.exists():
            print(f"  {name}: {p} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
