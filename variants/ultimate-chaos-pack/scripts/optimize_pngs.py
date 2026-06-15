#!/usr/bin/env python3
"""Lossless PNG optimization for the built resource pack."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image

from common import PACK_RP

ENTITY_TEXTURE_PARTS = ("textures/entity/", "textures/ui/panorama")


def _is_entity_sheet(rel: str) -> bool:
    return any(part in rel for part in ENTITY_TEXTURE_PARTS)


def _optimize_with_oxipng(path: Path) -> bool:
    try:
        subprocess.run(
            ["oxipng", "-q", "-o", "4", "--strip", "safe", str(path)],
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _optimize_with_pillow(path: Path) -> None:
    with Image.open(path) as img:
        img.save(path, format="PNG", optimize=True)


def optimize_png(path: Path) -> int:
    """Optimize one PNG in place. Returns bytes saved (may be negative)."""
    before = path.stat().st_size
    try:
        if not _optimize_with_oxipng(path):
            _optimize_with_pillow(path)
    except Exception as exc:
        print(f"  skip {path.name}: {exc}", file=sys.stderr)
        return 0
    return before - path.stat().st_size


def optimize_pack(pack_rp: Path = PACK_RP) -> tuple[int, int, int]:
    textures = pack_rp / "textures"
    if not textures.exists():
        raise FileNotFoundError(f"textures/ not found under {pack_rp}")

    before_total = 0
    after_total = 0
    count = 0
    for png in sorted(textures.rglob("*.png")):
        rel = str(png.relative_to(pack_rp))
        size_before = png.stat().st_size
        before_total += size_before
        saved = optimize_png(png)
        size_after = png.stat().st_size
        after_total += size_after
        count += 1
        if saved > 0:
            kind = "entity" if _is_entity_sheet(rel) else "block"
            print(f"  -{saved:,} B  [{kind}] {rel}")

    # pack icon at RP root
    icon = pack_rp / "pack_icon.png"
    if icon.exists():
        before_total += icon.stat().st_size
        optimize_png(icon)
        after_total += icon.stat().st_size
        count += 1

    return count, before_total, after_total


def main() -> None:
    parser = argparse.ArgumentParser(description="Lossless PNG optimization for built pack")
    parser.add_argument("--pack", type=Path, default=PACK_RP, help="Resource pack directory")
    args = parser.parse_args()

    print("Optimizing PNGs (lossless)...")
    try:
        count, before, after = optimize_pack(args.pack)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    saved = before - after
    pct = (saved / before * 100) if before else 0
    print(f"\nOptimized {count} PNGs: {before:,} → {after:,} bytes ({saved:,} saved, {pct:.1f}%)")


if __name__ == "__main__":
    main()
