"""Minecraft pixel-art texture polish — post-process AI and hand-made PNGs.

Inspired by multi-stage 3D→pixel pipelines (e.g. hubzz-3d-pipeline):
  1. Alpha cleanup — remove fringe halos from diffusion models
  2. Color quantize — snap to a small Bedrock-friendly palette
  3. Despeckle — drop lone stray pixels after downscale
  4. Edge snap — merge near-duplicate shades on opaque pixels

Pure Pillow — no extra deps.
"""

from __future__ import annotations

from PIL import Image

PROFILES = {
    "block": {"max_colors": 12, "alpha_cutoff": 200, "despeckle": True, "merge_dist": 18},
    "item": {"max_colors": 14, "alpha_cutoff": 200, "despeckle": True, "merge_dist": 16},
    "entity": {"max_colors": 28, "alpha_cutoff": 128, "despeckle": True, "merge_dist": 14},
    "environment": {"max_colors": 20, "alpha_cutoff": 128, "despeckle": False, "merge_dist": 16},
    "icon": {"max_colors": 36, "alpha_cutoff": 100, "despeckle": False, "merge_dist": 12},
    "default": {"max_colors": 16, "alpha_cutoff": 160, "despeckle": True, "merge_dist": 16},
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


def _quantize(img: Image.Image, max_colors: int) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    if max_colors < 2:
        return rgba

    # Quantize opaque RGB; keep hard alpha from cleanup step
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
            # Lone pixel — replace with most common neighbor color
            counts: dict[tuple[int, int, int], int] = {}
            for p in nbrs:
                c = p[:3]
                counts[c] = counts.get(c, 0) + 1
            best = max(counts, key=counts.get)
            opx[x, y] = (*best, 255)
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
    """Run full polish chain on one texture."""
    opts = PROFILES.get(profile, PROFILES["default"])
    out = _clean_alpha(img, opts["alpha_cutoff"])
    out = _quantize(out, opts["max_colors"])
    if opts["despeckle"]:
        out = _despeckle(out)
    return out


def polish_file(path, profile: str | None = None) -> Image.Image:
    from pathlib import Path

    path = Path(path)
    prof = profile or profile_for_path(str(path))
    img = Image.open(path).convert("RGBA")
    polished = polish_image(img, prof)
    polished.save(path, format="PNG")
    return polished
