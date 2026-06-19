#!/usr/bin/env python3
"""Prepare full resource pack — entire vanilla RP + lite custom BP."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import PACK_BP, PACK_RP, REPO_ROOT, copy_vanilla_rp

CUSTOM_BP = REPO_ROOT / "behavior_packs" / "brindal_grayson_cow_bp"


def _reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def prepare_full_rp() -> int:
    """Copy complete Mojang resource_pack (all textures, sounds, etc.)."""
    copy_vanilla_rp(PACK_RP)
    count = len(list(PACK_RP.rglob("*.png")))
    print(f"Full RP: copied vanilla resource pack ({count} PNGs)")
    return count


def prepare_full_bp() -> int:
    """Lite behavior pack — custom cows + items only (not full vanilla BP)."""
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
    print(f"Full BP: staged {count} custom file(s)")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare full vanilla RP workspace")
    parser.add_argument("--rp-only", action="store_true")
    parser.add_argument("--bp-only", action="store_true")
    args = parser.parse_args()
    if not args.rp_only and not args.bp_only:
        prepare_full_rp()
        prepare_full_bp()
    elif args.rp_only:
        prepare_full_rp()
    else:
        prepare_full_bp()


if __name__ == "__main__":
    main()
