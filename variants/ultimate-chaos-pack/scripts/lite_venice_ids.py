#!/usr/bin/env python3
"""Return comma-separated Venice texture IDs for the lite overlay pack only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from prepare_lite_pack import featured_texture_paths  # noqa: E402

PROMPTS = SCRIPTS.parent / "prompts" / "venice_prompts.json"
EXTRA_IDS = ("brindal_cow", "grayson_cow", "ranch_bell", "feed_bag")


def lite_venice_ids() -> list[str]:
    paths = set(featured_texture_paths())
    manifest = json.loads(PROMPTS.read_text(encoding="utf-8"))
    ids: list[str] = []
    for entry in manifest["textures"]:
        if entry.get("category") not in ("block", "item", "environment"):
            continue
        hit = entry["pack_path"] in paths
        for extra in entry.get("also_apply", []):
            if extra in paths:
                hit = True
        if hit:
            ids.append(entry["id"])
    for tex_id in EXTRA_IDS:
        if tex_id not in ids:
            ids.append(tex_id)
    return sorted(set(ids))


def main() -> None:
    print(",".join(lite_venice_ids()))


if __name__ == "__main__":
    main()
