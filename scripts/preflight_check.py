#!/usr/bin/env python3
"""Pre-flight smoke test for Cel_Band_Pack.mcpack before Bedrock import."""

from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "dist" / "Cel_Band_Pack.mcpack"

EXPECTED_BLOCKS = [
    "textures/blocks/calcite.png",
    "textures/blocks/stone.png",
    "textures/blocks/deepslate/deepslate.png",
    "textures/blocks/bedrock.png",
    "textures/blocks/sand.png",
    "textures/blocks/dirt.png",
    "textures/blocks/cobblestone.png",
    "textures/blocks/log_oak_top.png",
    "textures/blocks/log_oak.png",
    "textures/blocks/leaves_oak.png",
    "textures/blocks/leaves_oak_opaque.png",
    "textures/blocks/water_still_grey.png",
    "textures/blocks/gold_block.png",
    "textures/blocks/emerald_block.png",
    "textures/blocks/copper_block.png",
]

EXPECTED_ITEMS = [
    "textures/items/chorus_fruit.png",
    "textures/items/zombie_head.png",
    "textures/items/iron_ingot.png",
    "textures/items/prismarine_crystals.png",
    "textures/items/trident.png",
]

FRANCHISE_TERMS = ("lara", "croft", "lc go")


def check(pack_path: Path) -> bool:
    issues: list[str] = []
    ok: list[str] = []

    if not pack_path.exists():
        print(f"FAIL: Pack not found: {pack_path}")
        return False

    with zipfile.ZipFile(pack_path) as zf:
        names = zf.namelist()

        if "manifest.json" not in names:
            issues.append("manifest.json missing")
        else:
            try:
                manifest = json.loads(zf.read("manifest.json"))
                if manifest.get("format_version") != 2:
                    issues.append(f"manifest format_version should be 2, got {manifest.get('format_version')}")
                else:
                    ok.append("manifest format_version = 2")
                header = manifest.get("header", {})
                if not header.get("uuid"):
                    issues.append("manifest header.uuid missing")
                else:
                    ok.append("header UUID present")
                if not manifest.get("modules", [{}])[0].get("uuid"):
                    issues.append("manifest modules[0].uuid missing")
                else:
                    ok.append("module UUID present")
                if header.get("min_engine_version") != [1, 21, 0]:
                    issues.append(f"min_engine_version should be [1,21,0], got {header.get('min_engine_version')}")
                else:
                    ok.append("min_engine_version = 1.21.0")
                branding = (header.get("name", "") + header.get("description", "")).lower()
                for term in FRANCHISE_TERMS:
                    if term in branding:
                        issues.append(f"manifest contains franchise term: {term!r}")
            except Exception as exc:
                issues.append(f"manifest.json parse error: {exc}")

        from PIL import Image

        if "pack_icon.png" not in names:
            issues.append("pack_icon.png missing")
        else:
            icon = Image.open(io.BytesIO(zf.read("pack_icon.png")))
            if icon.size != (256, 256):
                issues.append(f"pack_icon.png should be 256x256, got {icon.size}")
            else:
                ok.append("pack_icon.png 256x256")

        block_textures = [n for n in names if n.startswith("textures/blocks/") and n.endswith(".png")]
        for path in block_textures:
            img = Image.open(io.BytesIO(zf.read(path)))
            if img.size != (16, 16):
                issues.append(f"{path} should be 16x16, got {img.size}")
        if block_textures and not any("blocks/" in i and "16x16" in i for i in issues):
            ok.append(f"{len(block_textures)} block textures all 16x16")

        item_textures = [n for n in names if n.startswith("textures/items/") and n.endswith(".png")]
        for path in item_textures:
            img = Image.open(io.BytesIO(zf.read(path)))
            if img.size != (16, 16):
                issues.append(f"{path} should be 16x16, got {img.size}")
            if img.mode != "RGBA":
                issues.append(f"{path} should be RGBA, got {img.mode}")
        if item_textures and not any("items/" in i for i in issues):
            ok.append(f"{len(item_textures)} item textures all 16x16 RGBA")

        missing_blocks = [b for b in EXPECTED_BLOCKS if b not in names]
        if missing_blocks:
            issues.append(f"Missing block textures: {missing_blocks}")
        else:
            ok.append(f"All {len(EXPECTED_BLOCKS)} expected block textures present")

        missing_items = [i for i in EXPECTED_ITEMS if i not in names]
        if missing_items:
            issues.append(f"Missing item textures: {missing_items}")
        else:
            ok.append(f"All {len(EXPECTED_ITEMS)} expected item textures present")

        if "textures/ui/hotbar_start_cap.png" not in names:
            issues.append("hotbar_start_cap.png missing")
        else:
            ok.append("hotbar_start_cap.png present")
        if "textures/ui/title.png" not in names:
            issues.append("title.png missing")
        else:
            ok.append("title.png present")

        expected_count = 1 + 1 + len(EXPECTED_BLOCKS) + len(EXPECTED_ITEMS) + 2
        if len(names) != expected_count:
            issues.append(f"Unexpected file count: {len(names)} (expected {expected_count})")

    print("=" * 60)
    print(f"PREFLIGHT CHECK: {pack_path}")
    print("=" * 60)
    print(f"\nPASSED ({len(ok)} checks):")
    for line in ok:
        print(f"  {line}")
    if issues:
        print(f"\nFAILED ({len(issues)} issues):")
        for line in issues:
            print(f"  {line}")
        print("\nResult: FAIL — do not import")
        return False
    print("\nResult: PASS — safe to import into Bedrock 1.21+")
    return True


def main() -> None:
    pack = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PACK
    success = check(pack)
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
