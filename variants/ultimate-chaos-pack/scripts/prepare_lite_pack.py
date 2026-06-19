#!/usr/bin/env python3
"""Prepare lightweight overlay packs — only changed assets, not full vanilla copies."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import (
    CUSTOM_RP,
    PACK_BP,
    PACK_RP,
    REPO_ROOT,
    VANILLA_RP,
    load_json,
)

PROMPTS_FILE = Path(__file__).resolve().parent.parent / "prompts" / "venice_prompts.json"
BAKED_DIR = Path(__file__).resolve().parent.parent / "baked_textures"
CUSTOM_BP = REPO_ROOT / "behavior_packs" / "brindal_grayson_cow_bp"

# Custom item icons (procedural at build — not vanilla copies).
EXTRA_TEXTURES = (
    "textures/blocks/diamond_block.png",
    "textures/blocks/gold_block.png",
)

LITE_RP_COPY: tuple[str, ...] = ()


def featured_texture_paths() -> list[str]:
    """Texture paths to include in the lite overlay resource pack."""
    manifest = load_json(PROMPTS_FILE)
    paths: set[str] = set(EXTRA_TEXTURES)
    for entry in manifest.get("textures", []):
        if entry.get("category") not in ("block", "item", "environment"):
            continue
        paths.add(entry["pack_path"])
        for extra in entry.get("also_apply", []):
            paths.add(extra)
    return sorted(paths)


def _reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def copy_vanilla_files(dest_root: Path, rel_paths: list[str]) -> int:
    count = 0
    for rel in rel_paths:
        src = VANILLA_RP / rel
        if not src.exists():
            baked = BAKED_DIR / rel
            if baked.exists():
                src = baked
            else:
                print(f"  skip missing vanilla: {rel}")
                continue
        dst = dest_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        count += 1
    return count


def prepare_lite_rp() -> int:
    """Empty RP workspace with only featured vanilla textures to customize."""
    _reset_dir(PACK_RP)
    paths = featured_texture_paths()
    copied = copy_vanilla_files(PACK_RP, paths)
    for rel in LITE_RP_COPY:
        src = CUSTOM_RP / rel
        if src.exists():
            dst = PACK_RP / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    print(f"Lite RP: staged {copied} texture file(s) (+ manifest/icons added later)")
    return copied


def prepare_lite_bp() -> int:
    """Empty BP workspace with only custom cow entities + spawn rules."""
    _reset_dir(PACK_BP)
    count = 0
    for sub in ("entities", "spawn_rules", "items", "texts"):
        src_dir = CUSTOM_BP / sub
        if not src_dir.exists():
            continue
        for src in src_dir.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(CUSTOM_BP)
            dst = PACK_BP / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
    print(f"Lite BP: staged {count} file(s) from custom cow behavior pack")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare lite overlay pack workspaces")
    parser.add_argument("--rp-only", action="store_true")
    parser.add_argument("--bp-only", action="store_true")
    args = parser.parse_args()
    if not args.rp_only and not args.bp_only:
        prepare_lite_rp()
        prepare_lite_bp()
    elif args.rp_only:
        prepare_lite_rp()
    else:
        prepare_lite_bp()


if __name__ == "__main__":
    main()
