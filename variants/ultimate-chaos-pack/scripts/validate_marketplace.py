#!/usr/bin/env python3
"""Lightweight Marketplace compliance checks (cooperative add-on rules)."""

from __future__ import annotations

import argparse
import sys

from common import PACK_BP, PACK_RP, load_json

COW_UI_DEFS = (
    "ui/cow_start.json",
    "ui/cow_start_screen.json",
)

CUSTOM_ITEMS = (
    "items/ranch_bell.json",
    "items/feed_bag.json",
)


def validate() -> list[str]:
    errors: list[str] = []

    for rel in COW_UI_DEFS:
        if (PACK_RP / rel).exists():
            errors.append(f"JSON UI override present: {rel}")

    defs_path = PACK_RP / "ui" / "_ui_defs.json"
    if defs_path.exists():
        for entry in COW_UI_DEFS:
            if entry in load_json(defs_path).get("ui_defs", []):
                errors.append(f"UI def registered: {entry}")

    for rel in CUSTOM_ITEMS:
        path = PACK_BP / rel
        if not path.exists():
            errors.append(f"Missing Marketplace custom item: {rel}")
            continue
        ident = (
            load_json(path)
            .get("minecraft:item", {})
            .get("description", {})
            .get("identifier", "")
        )
        if not ident.startswith("bgcow:"):
            errors.append(f"Item must use bgcow: namespace: {rel}")

    lang = PACK_RP / "texts" / "en_US.lang"
    if lang.exists():
        text = lang.read_text(encoding="utf-8")
        for key in ("item.bgcow:ranch_bell.name", "item.bgcow:feed_bag.name"):
            if key not in text:
                errors.append(f"Missing lang key: {key}")
    else:
        errors.append("Missing RP en_US.lang")

    script = PACK_BP / "scripts" / "main.js"
    if script.exists():
        body = script.read_text(encoding="utf-8")
        if "bgcow:ranch_bell" not in body or "bgcow:feed_bag" not in body:
            errors.append("Script must reference bgcow:ranch_bell and bgcow:feed_bag")
    else:
        errors.append("Missing behavior_pack/scripts/main.js")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Marketplace compliance")
    parser.parse_args()
    print("Marketplace compliance...")
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
