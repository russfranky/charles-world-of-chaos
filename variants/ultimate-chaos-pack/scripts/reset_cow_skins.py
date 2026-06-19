#!/usr/bin/env python3
"""Reset custom cow textures to vanilla Minecraft cow (no AI / cel skins)."""

from __future__ import annotations

import argparse
import shutil

from common import CUSTOM_RP, VANILLA_RP

VANILLA_COW_V2 = VANILLA_RP / "textures" / "entity" / "cow" / "cow_v2.png"
VANILLA_COW_COLD = VANILLA_RP / "textures" / "entity" / "cow" / "cow_cold.png"

CUSTOM_COW_TEXTURES = (
    (CUSTOM_RP / "textures" / "entity" / "brindal_cow.png", VANILLA_COW_V2),
    (CUSTOM_RP / "textures" / "entity" / "grayson_cow.png", VANILLA_COW_COLD),
)


def reset_cow_skins() -> int:
    if not VANILLA_COW_V2.exists():
        raise FileNotFoundError(f"Vanilla cow texture missing — run build once to clone bedrock-samples: {VANILLA_COW_V2}")

    count = 0
    for dest, src in CUSTOM_COW_TEXTURES:
        if not src.exists():
            src = VANILLA_COW_V2
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  reset {dest.relative_to(CUSTOM_RP.parent)} ← {src.name}")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy vanilla cow PNGs onto custom cow slots")
    parser.parse_args()
    print("Resetting cow skins to vanilla...")
    n = reset_cow_skins()
    print(f"Done: {n} texture(s)")


if __name__ == "__main__":
    main()
