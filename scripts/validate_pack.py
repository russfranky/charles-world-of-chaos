#!/usr/bin/env python3
"""Validate Cel Band Pack build artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "dist" / "Cel_Band_Pack.mcpack"
DOWNLOAD_PACK = ROOT / "download" / "Cel_Band_Pack.mcpack"
PACK_SRC = ROOT / "variants" / "cel-band" / "pack"
VERSION_FILE = ROOT / "variants" / "cel-band" / "VERSION"
SAMPLE = ROOT / "download" / "sample_level.json"

# Blocks emitted by convert_level.py must have converted textures in pack/.
BLOCK_TEXTURES: dict[str, list[str]] = {
    "calcite": ["textures/blocks/calcite.png"],
    "stone": ["textures/blocks/stone.png"],
    "deepslate": ["textures/blocks/deepslate/deepslate.png"],
    "bedrock": ["textures/blocks/bedrock.png"],
    "sand": ["textures/blocks/sand.png"],
    "cobblestone": ["textures/blocks/cobblestone.png"],
    "oak_log": ["textures/blocks/log_oak.png", "textures/blocks/log_oak_top.png"],
    "leaves": ["textures/blocks/leaves_oak.png", "textures/blocks/leaves_oak_opaque.png"],
    "water": ["textures/blocks/water_still_grey.png"],
    "gold_block": ["textures/blocks/gold_block.png"],
    "emerald_block": ["textures/blocks/emerald_block.png"],
    "copper_block": ["textures/blocks/copper_block.png"],
}

FRANCHISE_TERMS = ("lara", "croft", "lc go")


def fail(message: str) -> None:
    print(f"validate_pack: {message}", file=sys.stderr)
    raise SystemExit(1)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_branding(text: str, label: str) -> None:
    lower = text.lower()
    for term in FRANCHISE_TERMS:
        if term in lower:
            fail(f"{label} must not reference trademarked franchises ({term!r})")


def main() -> None:
    if not PACK_SRC.is_dir():
        fail(f"missing pack source: {PACK_SRC}")

    if not (PACK_SRC / "manifest.json").is_file():
        fail("pack source missing manifest.json")

    if not PACK.is_file():
        fail(f"missing distributable: {PACK}")

    if not DOWNLOAD_PACK.is_file():
        fail(f"missing download mirror: {DOWNLOAD_PACK}")

    if PACK.stat().st_size < 10_000:
        fail(f"pack too small: {PACK.stat().st_size} bytes")

    if file_hash(PACK) != file_hash(DOWNLOAD_PACK):
        fail("dist/ and download/ .mcpack files differ")

    semver = VERSION_FILE.read_text().strip().split(".")
    if len(semver) != 3:
        fail(f"invalid VERSION file: {VERSION_FILE.read_text()!r}")

    for block, texture_paths in BLOCK_TEXTURES.items():
        for rel in texture_paths:
            if not (PACK_SRC / rel).is_file():
                fail(f"converter block {block!r} requires missing texture: {rel}")

    with zipfile.ZipFile(PACK) as archive:
        names = set(archive.namelist())
        if "manifest.json" not in names:
            fail("pack missing manifest.json")
        if "pack_icon.png" not in names:
            fail("pack missing pack_icon.png")
        for rel in sum(BLOCK_TEXTURES.values(), []):
            if rel not in names:
                fail(f"pack zip missing {rel}")
        manifest = json.loads(archive.read("manifest.json"))
        header = manifest.get("header", {})
        if header.get("min_engine_version", [0, 0, 0]) < [1, 21, 0]:
            fail("manifest min_engine_version must be >= 1.21.0")
        check_branding(header.get("name", ""), "pack name")
        check_branding(header.get("description", ""), "pack description")
        if header.get("version") != [int(semver[0]), int(semver[1]), int(semver[2])]:
            fail("manifest version does not match VERSION file")
        if len(names) < 24:
            fail(f"pack should contain 24 files, got {len(names)}")

    if not SAMPLE.is_file():
        fail(f"missing sample level: {SAMPLE}")

    level = json.loads(SAMPLE.read_text())
    tiles = level.get("tiles", [])
    if len(tiles) < 40:
        fail(f"sample level too small: {len(tiles)} tiles")

    print("validate_pack: OK")


if __name__ == "__main__":
    main()
