#!/usr/bin/env python3
"""Validate Lara Croft GO Diorama build artifacts."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "dist" / "Lara_Croft_GO_Diorama.mcpack"
SAMPLE = ROOT / "download" / "sample_level.json"
TOOL = ROOT / "variants" / "lcgo-diorama" / "scripts" / "lcgo_mc_tool.py"


def fail(message: str) -> None:
    print(f"validate_pack: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not TOOL.is_file():
        fail(f"missing generator: {TOOL}")

    if not PACK.is_file():
        fail(f"missing distributable: {PACK}")

    if PACK.stat().st_size < 5_000:
        fail(f"pack too small: {PACK.stat().st_size} bytes")

    with zipfile.ZipFile(PACK) as archive:
        names = archive.namelist()
        if "manifest.json" not in names:
            fail("pack missing manifest.json")
        if "pack_icon.png" not in names:
            fail("pack missing pack_icon.png")
        manifest = json.loads(archive.read("manifest.json"))
        header = manifest.get("header", {})
        if header.get("min_engine_version", [0, 0, 0]) < [1, 21, 0]:
            fail("manifest min_engine_version must be >= 1.21.0")

    if not SAMPLE.is_file():
        fail(f"missing sample level: {SAMPLE}")

    level = json.loads(SAMPLE.read_text())
    tiles = level.get("tiles", [])
    if len(tiles) < 35:
        fail(f"sample level too small: {len(tiles)} tiles")

    print("validate_pack: OK")


if __name__ == "__main__":
    main()
