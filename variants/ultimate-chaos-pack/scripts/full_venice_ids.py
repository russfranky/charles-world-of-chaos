#!/usr/bin/env python3
"""All Venice manifest texture IDs (full texture-pack facelift)."""

from __future__ import annotations

import json
from pathlib import Path

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "venice_prompts.json"


def full_venice_ids() -> list[str]:
    manifest = json.loads(PROMPTS.read_text(encoding="utf-8"))
    return sorted({t["id"] for t in manifest["textures"]})


def main() -> None:
    print(",".join(full_venice_ids()))


if __name__ == "__main__":
    main()
