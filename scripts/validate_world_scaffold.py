#!/usr/bin/env python3
"""Verify Marketplace world template scaffold files exist and manifest is valid."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCaffold = ROOT / "worlds" / "brindal_grayson_ranch"

REQUIRED_FILES = (
    "README.md",
    "WORLD_CHECKLIST.md",
    "manifest.json",
    "level_settings.reference.json",
    "texts/en_US.lang",
    "texts/languages.json",
)

MANIFEST_HEADER_KEYS = (
    "uuid",
    "version",
    "lock_template_options",
    "base_game_version",
)


def validate() -> list[str]:
    errors: list[str] = []

    if not SCaffold.is_dir():
        errors.append(f"Missing scaffold directory: {SCaffold.relative_to(ROOT)}")
        return errors

    for rel in REQUIRED_FILES:
        if not (SCaffold / rel).exists():
            errors.append(f"Missing required file: worlds/brindal_grayson_ranch/{rel}")

    manifest_path = SCaffold / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid manifest.json: {exc}")
            return errors

        header = manifest.get("header", {})
        for key in MANIFEST_HEADER_KEYS:
            if key not in header:
                errors.append(f"manifest.json header missing: {key}")

        if header.get("lock_template_options") is not True:
            errors.append("manifest.json must set lock_template_options: true")

        modules = manifest.get("modules", [])
        if not any(m.get("type") == "world_template" for m in modules):
            errors.append("manifest.json must include a world_template module")

        deps = manifest.get("dependencies", [])
        uuids = {d.get("uuid") for d in deps if isinstance(d, dict)}
        for pack_uuid in (
            "c409dd16-412b-422a-9496-e1335c9f3ed5",
            "26cbe6c2-9ac3-464e-a6cd-08bfef85c38d",
        ):
            if pack_uuid not in uuids:
                errors.append(f"manifest.json missing dependency UUID: {pack_uuid}")

    lang = SCaffold / "texts" / "en_US.lang"
    if lang.exists():
        text = lang.read_text(encoding="utf-8")
        for key in ("pack.name=", "pack.description="):
            if key not in text:
                errors.append(f"texts/en_US.lang missing {key.rstrip('=')}")

    return errors


def main() -> int:
    print("World template scaffold...")
    errors = validate()
    if errors:
        print("FAILED:")
        for err in errors:
            print(f"  ✗ {err}")
        return 1
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
