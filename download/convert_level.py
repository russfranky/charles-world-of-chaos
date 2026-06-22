#!/usr/bin/env python3
"""Convert cel-band level JSON into Bedrock block placements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VARIANT_ROOT = Path(__file__).resolve().parent.parent


def default_level_path() -> Path:
    script_dir = Path(__file__).resolve().parent
    local = script_dir / "sample_level.json"
    if local.is_file():
        return local
    return script_dir.parent / "levels" / "sample_level.json"


def default_output_dir() -> Path:
    script_dir = Path(__file__).resolve().parent
    if (script_dir / "sample_level.json").is_file():
        return script_dir
    return script_dir.parents[2] / "download"

TILE_TO_MC: dict[str, str] = {
    "floor_lit": "calcite",
    "floor_light": "stone",
    "floor_dark": "deepslate",
    "floor_shadow": "bedrock",
    "wall": "cobblestone",
    "sand": "sand",
    "wood": "oak_log",
    "leaves": "leaves",
    "water": "water",
    "gold_relic": "gold_block",
    "jade_relic": "emerald_block",
    "bronze_relic": "copper_block",
}


def level_to_blocks(level_json: dict, origin: tuple[int, int, int] = (0, 100, 0)) -> list[tuple[int, int, int, str]]:
    blocks: list[tuple[int, int, int, str]] = []
    base_x, base_y, base_z = origin
    for tile in level_json.get("tiles", []):
        x = base_x + tile["x"]
        y = base_y + tile.get("y", 0)
        z = base_z + tile["z"]
        tile_type = tile["type"]
        block_type = TILE_TO_MC.get(tile_type, "stone")
        if tile_type == "wall":
            blocks.append((x, y, z, "cobblestone"))
            blocks.append((x, y + 1, z, "cobblestone"))
        elif tile_type == "wood":
            blocks.append((x, y, z, "oak_log"))
            blocks.append((x, y + 1, z, "oak_log"))
            blocks.append((x, y + 2, z, "oak_log"))
            blocks.append((x, y + 3, z, "leaves"))
        elif tile_type == "leaves":
            blocks.append((x, y + 1, z, "leaves"))
            blocks.append((x, y + 2, z, "leaves"))
        else:
            blocks.append((x, y, z, block_type))
    return blocks


def write_outputs(blocks: list[tuple[int, int, int, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    setblock_lines = [
        "# Cel-band level → MC Bedrock /setblock commands",
        f"# Total blocks: {len(blocks)}",
        "# Run each line in-game as a slash command.",
        "",
    ]
    for x, y, z, block in blocks:
        setblock_lines.append(f"setblock {x} {y} {z} {block}")
    (out_dir / "sample_level.setblock").write_text("\n".join(setblock_lines) + "\n", encoding="utf-8")

    mcfunction = [f"setblock {x} {y} {z} {block}" for x, y, z, block in blocks]
    (out_dir / "diorama_level.mcfunction").write_text("\n".join(mcfunction) + "\n", encoding="utf-8")

    py_lines = ["# Converted cel-band voxel data", "BLOCKS = ["]
    for x, y, z, block in blocks:
        py_lines.append(f"    ({x}, {y}, {z}, '{block}'),")
    py_lines.append("]")
    (out_dir / "diorama_blocks.py").write_text("\n".join(py_lines) + "\n", encoding="utf-8")


def parse_origin(value: str) -> tuple[int, int, int]:
    parts = [int(part.strip()) for part in value.split(",")]
    if len(parts) != 3:
        raise ValueError("origin must be x,y,z")
    return parts[0], parts[1], parts[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert cel-band level JSON to Bedrock placements")
    parser.add_argument("--level", type=Path, default=None)
    parser.add_argument("--origin", default="0,100,0")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    level_path = args.level or default_level_path()
    output_dir = args.output or default_output_dir()

    level = json.loads(level_path.read_text(encoding="utf-8"))
    origin = parse_origin(args.origin)
    blocks = level_to_blocks(level, origin)
    write_outputs(blocks, output_dir)
    (output_dir / "sample_level.json").write_text(json.dumps(level, indent=2) + "\n", encoding="utf-8")
    print(f"Converted {len(blocks)} blocks → {output_dir / 'sample_level.setblock'}")


if __name__ == "__main__":
    main()
