#!/usr/bin/env python3
"""Validate shipped product branding matches Charles' World of Chaos."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_RP = ROOT / "variants/ultimate-chaos-pack/pack"
PACK_BP = ROOT / "variants/ultimate-chaos-pack/behavior_pack"
PRODUCT = "Charles' World of Chaos"


def validate() -> list[str]:
    errors: list[str] = []

    rp_lang = PACK_RP / "texts" / "en_US.lang"
    if not rp_lang.exists():
        errors.append("Built RP lang missing — run ./scripts/build-mcaddon.sh first")
        return errors

    text = rp_lang.read_text(encoding="utf-8")
    if f"pack.name={PRODUCT}" not in text:
        errors.append(f"RP lang pack.name must be '{PRODUCT}'")
    if "menu.moo_world_subtitle" not in text or "Ranch Bell" not in text:
        errors.append("RP lang missing menu.moo_world_subtitle with Ranch Bell")

    bp_manifest = PACK_BP / "manifest.json"
    if bp_manifest.exists():
        bp_text = bp_manifest.read_text(encoding="utf-8")
        if PRODUCT not in bp_text:
            errors.append(f"BP manifest should reference '{PRODUCT}'")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"# {PRODUCT}" not in readme:
        errors.append(f"README.md H1 should be '# {PRODUCT}'")

    return errors


def main() -> int:
    print("Branding consistency...")
    errors = validate()
    if errors:
        print("FAILED:")
        for err in errors:
            print(f"  ✗ {err}")
        return 1
    print(f"PASSED — product brand '{PRODUCT}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
