"""Minecraft pixel-art texture polish — post-process AI and hand-made PNGs.

Build-time only: cel/toon shading is baked into PNG pixels (no in-game shaders).

Inspired by multi-stage 3D→pixel pipelines (e.g. hubzz-3d-pipeline), Three.js
MeshToonMaterial (offline gradient-map analog), and retro shader packs:
  1. Alpha cleanup — remove fringe halos from diffusion models
  2. Color quantize — snap to a small Bedrock-friendly palette
  3. Cel band — step luminance into discrete toon shades (gradient-map bake)
  4. Cel outline — ink edge on silhouettes (optional per profile)
  5. Despeckle — drop lone stray pixels after downscale
  6. Edge snap — merge near-duplicate shades on opaque pixels

Pure Pillow — no extra deps.
"""

from __future__ import annotations

from PIL import Image

# 4×4 Bayer matrix (0–15), used like ordered dither shaders
_BAYER_4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)

PROFILES = {
    "block": {
        "max_colors": 10,
        "alpha_cutoff": 200,
        "despeckle": True,
        "merge_dist": 18,
        "dither": False,
        "dither_strength": 0.0,
        "cel_bands": 4,
        "cel_outline": "alpha",
        "cel_outline_strength": 0.7,
    },
    "item": {
        "max_colors": 12,
        "alpha_cutoff": 200,
        "despeckle": True,
        "merge_dist": 16,
        "dither": False,
        "dither_strength": 0.0,
        "cel_bands": 4,
        "cel_outline": "alpha",
        "cel_outline_strength": 0.75,
    },
    "entity": {
        "max_colors": 20,
        "alpha_cutoff": 128,
        "despeckle": True,
        "merge_dist": 14,
        "dither": False,
        "dither_strength": 0.0,
        "cel_bands": 5,
        "cel_outline": "alpha",
        "cel_outline_strength": 0.8,
    },
    "environment": {
        "max_colors": 16,
        "alpha_cutoff": 128,
        "despeckle": False,
        "merge_dist": 16,
        "dither": False,
        "dither_strength": 0.0,
        "cel_bands": 4,
        "cel_outline": False,
        "cel_outline_strength": 0.0,
    },
    "icon": {
        "max_colors": 24,
        "alpha_cutoff": 100,
        "despeckle": False,
        "merge_dist": 12,
        "dither": False,
        "dither_strength": 0.0,
        "cel_bands": 5,
        "cel_outline": "alpha",
        "cel_outline_strength": 0.65,
    },
    "default": {
        "max_colors": 14,
        "alpha_cutoff": 160,
        "despeckle": True,
        "merge_dist": 16,
        "dither": False,
        "dither_strength": 0.0,
        "cel_bands": 4,
        "cel_outline": "alpha",
        "cel_outline_strength": 0.7,
    },
}


def profile_for_path(rel_path: str) -> str:
    rel = rel_path.replace("\\", "/").lower()
    if rel.endswith("pack_icon.png") or "/pack_icon" in rel:
        return "icon"
    if "/entity/" in rel:
        return "entity"
    if "/items/" in rel:
        return "item"
    if "/environment/" in rel:
        return "environment"
    if "/blocks/" in rel:
        return "block"
    return "default"


def _color_dist_sq(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def _palette_from_image(px, w: int, h: int) -> list[tuple[int, int, int]]:
    colors: set[tuple[int, int, int]] = set()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= 128:
                colors.add((r, g, b))
    return sorted(colors)


def _nearest_two(
    color: tuple[int, int, int], palette: list[tuple[int, int, int]]
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    ranked = sorted(palette, key=lambda p: _color_dist_sq(color, p))
    first = ranked[0]
    second = ranked[1] if len(ranked) > 1 else first
    return first, second


def _bayer_dither(img: Image.Image, strength: float) -> Image.Image:
    """Ordered Bayer dither between two nearest palette colors."""
    if strength <= 0:
        return img
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    palette = _palette_from_image(px, w, h)
    if len(palette) < 2:
        return rgba

    out = rgba.copy()
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            c = (r, g, b)
            n1, n2 = _nearest_two(c, palette)
            if n1 == n2:
                opx[x, y] = (*n1, 255)
                continue
            d1 = _color_dist_sq(c, n1) ** 0.5
            d2 = _color_dist_sq(c, n2) ** 0.5
            if d1 + d2 < 1:
                opx[x, y] = (*n1, 255)
                continue
            blend = d1 / (d1 + d2)
            threshold = (_BAYER_4[y % 4][x % 4] + 0.5) / 16.0
            cutoff = threshold * (1.0 - strength) + (1.0 - strength) * 0.5
            pick = n2 if blend > cutoff else n1
            opx[x, y] = (*pick, 255)
    return out


def _quantize(img: Image.Image, max_colors: int) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    if max_colors < 2:
        return rgba

    bg = Image.new("RGB", (w, h), (0, 0, 0))
    alpha = rgba.split()[3]
    bg.paste(rgba, mask=alpha)
    q = bg.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT).convert("RGB")

    out = Image.new("RGBA", (w, h))
    opx = out.load()
    qpx = q.load()
    apx = alpha.load()
    for y in range(h):
        for x in range(w):
            a = apx[x, y]
            if a < 128:
                opx[x, y] = (0, 0, 0, 0)
            else:
                r, g, b = qpx[x, y]
                opx[x, y] = (r, g, b, 255)
    return out


def _despeckle(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    out = rgba.copy()
    opx = out.load()

    def neighbors(x: int, y: int) -> list[tuple[int, int, int, int]]:
        result = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    result.append(px[nx, ny])
        return result

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            nbrs = [p for p in neighbors(x, y) if p[3] >= 128]
            if not nbrs:
                continue
            same = sum(1 for p in nbrs if p[:3] == (r, g, b, a)[:3])
            if same >= 2:
                continue
            counts: dict[tuple[int, int, int], int] = {}
            for p in nbrs:
                c = p[:3]
                counts[c] = counts.get(c, 0) + 1
            best = max(counts, key=counts.get)
            opx[x, y] = (*best, 255)
    return out


def _edge_snap(img: Image.Image, merge_dist: int) -> Image.Image:
    """Merge near-duplicate neighbor shades (edge snap)."""
    if merge_dist <= 0:
        return img
    dist_sq = merge_dist * merge_dist
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    out = rgba.copy()
    opx = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            c = (r, g, b)
            counts: dict[tuple[int, int, int], int] = {c: 1}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if nx < 0 or ny < 0 or nx >= w or ny >= h:
                        continue
                    nr, ng, nb, na = px[nx, ny]
                    if na < 128:
                        continue
                    nc = (nr, ng, nb)
                    if _color_dist_sq(c, nc) <= dist_sq:
                        counts[nc] = counts.get(nc, 0) + 1
            if len(counts) <= 1:
                continue
            best = max(counts, key=counts.get)
            if best != c and counts[best] >= 3:
                opx[x, y] = (*best, 255)
    return out


def _luminance(r: int, g: int, b: int) -> float:
    return 0.299 * r + 0.587 * g + 0.114 * b


def _cel_shade(img: Image.Image, bands: int) -> Image.Image:
    """Bake toon/cel shading — step luminance like a Three.js gradient map."""
    if bands < 2:
        return img
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    out = rgba.copy()
    opx = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            lum = _luminance(r, g, b)
            if lum < 1.0:
                opx[x, y] = (r, g, b, 255)
                continue
            # Discrete shade bands (mid-tone lift keeps Minecraft readability)
            band = min(bands - 1, int((lum / 255.0) * bands))
            shade = (band + 0.5) / bands
            scale = (shade * 255.0) / lum
            opx[x, y] = (
                max(0, min(255, int(r * scale))),
                max(0, min(255, int(g * scale))),
                max(0, min(255, int(b * scale))),
                255,
            )
    return out


def _cel_outline(
    img: Image.Image,
    mode: str | bool,
    strength: float,
    color_diff: int = 36,
) -> Image.Image:
    """Ink outline on alpha edges (and optional color boundaries)."""
    if not mode or strength <= 0:
        return img
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    out = rgba.copy()
    opx = out.load()
    ink = (24, 18, 28)
    diff_sq = color_diff * color_diff

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            edge = False
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    edge = True
                    break
                nr, ng, nb, na = px[nx, ny]
                if na < 128:
                    edge = True
                    break
                if mode == "full" and _color_dist_sq((r, g, b), (nr, ng, nb)) > diff_sq:
                    edge = True
                    break
            if edge:
                opx[x, y] = (
                    int(r * (1.0 - strength) + ink[0] * strength),
                    int(g * (1.0 - strength) + ink[1] * strength),
                    int(b * (1.0 - strength) + ink[2] * strength),
                    255,
                )
    return out


def _clean_alpha(img: Image.Image, cutoff: int) -> Image.Image:
    rgba = img.convert("RGBA")
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a < cutoff:
                px[x, y] = (0, 0, 0, 0)
            elif a < 255:
                px[x, y] = (r, g, b, 255)
    return rgba


def polish_image(img: Image.Image, profile: str = "default") -> Image.Image:
    """Run full polish chain on one texture (cel/toon baked into pixels)."""
    opts = PROFILES.get(profile, PROFILES["default"])
    out = _clean_alpha(img, opts["alpha_cutoff"])
    out = _quantize(out, opts["max_colors"])
    cel_bands = opts.get("cel_bands", 0)
    if cel_bands and cel_bands >= 2:
        out = _cel_shade(out, cel_bands)
        out = _cel_outline(
            out,
            opts.get("cel_outline", False),
            opts.get("cel_outline_strength", 0.0),
        )
    elif opts.get("dither"):
        out = _bayer_dither(out, opts.get("dither_strength", 0.3))
    if opts["despeckle"]:
        out = _despeckle(out)
    out = _edge_snap(out, opts["merge_dist"])
    return out


def polish_file(path, profile: str | None = None) -> Image.Image:
    from pathlib import Path

    path = Path(path)
    prof = profile or profile_for_path(str(path))
    img = Image.open(path).convert("RGBA")
    polished = polish_image(img, prof)
    polished.save(path, format="PNG")
    return polished
