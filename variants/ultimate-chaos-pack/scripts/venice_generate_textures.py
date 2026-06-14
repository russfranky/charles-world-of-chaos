#!/usr/bin/env python3
"""
Generate Minecraft textures via Venice AI and apply to the Ultimate Chaos pack.

Workflow:
  1. Generate at 1024×1024 (or configured generate_size) with FLUX / gpt-image-2
  2. Downscale with nearest-neighbor to exact Minecraft size (16/32/64/128/256/512)
  3. Write into pack/ paths (overrides algorithmic cow-hide for featured textures)

Requires VENICE_API_KEY environment variable. Never commit API keys.

Usage:
  export VENICE_API_KEY='your-key'
  python3 venice_generate_textures.py --list
  python3 venice_generate_textures.py --id zombie,creeper,pack_icon
  python3 venice_generate_textures.py --category entity --dry-run
  python3 venice_generate_textures.py --all
"""

from __future__ import annotations

import argparse
import json
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

from common import PACK_RP, VARIANT_ROOT
from venice_client import VeniceError, generate_image, save_png

PROMPTS_FILE = VARIANT_ROOT / "prompts" / "venice_prompts.json"
CACHE_DIR = VARIANT_ROOT / "venice_cache"
STYLE_SUFFIX = (
    " Flat pixel art, hard edges, no anti-aliasing, no gradients, "
    "solid color blocks, Minecraft style."
)


def load_manifest() -> dict:
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def downscale_nearest(data: bytes, target_size: int | tuple[int, int]) -> Image.Image:
    img = Image.open(BytesIO(data)).convert("RGBA")
    if isinstance(target_size, int):
        size = (target_size, target_size)
    else:
        size = target_size
    return img.resize(size, Image.Resampling.NEAREST)


def apply_to_pack(img: Image.Image, pack_path: str) -> None:
    dest = PACK_RP / pack_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, format="PNG")
    print(f"  → {dest.relative_to(PACK_RP.parent)}")


def generate_texture(entry: dict, manifest: dict, *, dry_run: bool = False, force: bool = False) -> bool:
    tex_id = entry["id"]
    cache_hi = CACHE_DIR / f"{tex_id}_{entry['generate_size']}.png"
    cache_lo = CACHE_DIR / f"{tex_id}_{entry['target_size']}.png"

    if cache_lo.exists() and not force:
        print(f"[cache] {tex_id} — applying cached {cache_lo.name}")
        img = Image.open(cache_lo).convert("RGBA")
        apply_to_pack(img, entry["pack_path"])
        for extra in entry.get("also_apply", []):
            apply_to_pack(img, extra)
        return True

    prompt = entry["prompt"] + STYLE_SUFFIX
    model = entry.get("model", "flux-dev")
    gen_size = entry["generate_size"]

    if dry_run:
        print(f"[dry-run] {tex_id}: model={model} size={gen_size}→{entry['target_size']}")
        print(f"  prompt: {prompt[:120]}...")
        return True

    print(f"[generate] {tex_id} via {model} at {gen_size}×{gen_size}...")
    try:
        raw = generate_image(prompt, model=model, width=gen_size, height=gen_size)
    except VeniceError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return False

    save_png(raw, cache_hi)
    img = downscale_nearest(raw, entry["target_size"])
    save_png(_img_to_bytes(img), cache_lo)

    if not PACK_RP.exists():
        print(f"  ⚠ pack/ not found — saved to cache only ({cache_lo})", file=sys.stderr)
        return True

    apply_to_pack(img, entry["pack_path"])
    for extra in entry.get("also_apply", []):
        apply_to_pack(img, extra)
    return True


def _img_to_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_style_anchor(manifest: dict, *, dry_run: bool = False) -> bool:
    anchor = manifest.get("style_anchor")
    if not anchor:
        return True

    cache = CACHE_DIR / "style_anchor.png"
    if cache.exists() and not dry_run:
        print(f"[anchor] cached at {cache}")
        return True

    if dry_run:
        print(f"[dry-run] style anchor: {anchor['prompt'][:100]}...")
        return True

    print("[anchor] Generating style reference image...")
    try:
        raw = generate_image(
            anchor["prompt"] + STYLE_SUFFIX,
            model=anchor.get("model", "flux-dev"),
            width=anchor.get("generate_size", 1024),
            height=anchor.get("generate_size", 1024),
        )
        save_png(raw, cache)
        print(f"  → {cache}")
        return True
    except VeniceError as exc:
        print(f"  ✗ anchor failed: {exc}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate textures via Venice AI")
    parser.add_argument("--id", help="Comma-separated texture IDs (e.g. zombie,creeper)")
    parser.add_argument("--category", help="Filter by category: entity, block, item, gui, environment, panorama")
    parser.add_argument("--all", action="store_true", help="Generate all textures in manifest")
    parser.add_argument("--list", action="store_true", help="List available texture IDs")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling API")
    parser.add_argument("--force", action="store_true", help="Regenerate even if cached")
    parser.add_argument("--skip-anchor", action="store_true", help="Skip style anchor generation")
    args = parser.parse_args()

    manifest = load_manifest()
    textures = manifest["textures"]

    if args.list:
        for t in textures:
            print(f"  {t['id']:25} {t['category']:12} → {t['pack_path']} ({t['target_size']}px)")
        return

    if args.all:
        selected = textures
    elif args.id:
        ids = {s.strip() for s in args.id.split(",")}
        selected = [t for t in textures if t["id"] in ids]
        missing = ids - {t["id"] for t in selected}
        if missing:
            print(f"Unknown IDs: {missing}", file=sys.stderr)
    elif args.category:
        selected = [t for t in textures if t["category"] == args.category]
    else:
        parser.print_help()
        sys.exit(1)

    if not selected:
        print("No textures selected.", file=sys.stderr)
        sys.exit(1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_anchor and not args.dry_run:
        if not generate_style_anchor(manifest, dry_run=args.dry_run):
            print("Style anchor failed — continuing anyway", file=sys.stderr)

    ok = 0
    fail = 0
    for entry in selected:
        if generate_texture(entry, manifest, dry_run=args.dry_run, force=args.force):
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} succeeded, {fail} failed")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
