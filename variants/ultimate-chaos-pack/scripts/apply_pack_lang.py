#!/usr/bin/env python3
"""Apply lang-only pack branding (Marketplace-safe — no JSON UI overrides)."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import PACK_RP

LANG_SRC = Path(__file__).resolve().parent.parent / "gui_overrides" / "texts" / "cow_gui.lang"


def apply_pack_lang() -> int:
    lang_src = LANG_SRC
    if not lang_src.exists():
        print("  No pack lang source — skip")
        return 0
    dest = PACK_RP / "texts" / "en_US.lang"
    dest.parent.mkdir(parents=True, exist_ok=True)
    existing = dest.read_text(encoding="utf-8").splitlines() if dest.exists() else []
    overrides: dict[str, str] = {}
    for line in lang_src.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        overrides[key] = value

    new_lines = []
    seen = set()
    for line in existing:
        if "=" in line:
            key = line.split("=", 1)[0]
            if key in overrides:
                new_lines.append(f"{key}={overrides[key]}")
                seen.add(key)
                continue
        new_lines.append(line)

    for key, value in overrides.items():
        if key not in seen:
            new_lines.append(f"{key}={value}")

    dest.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"  Lang: {len(overrides)} key(s) in en_US.lang (no JSON UI)")
    return len(overrides)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply lang-only pack branding")
    parser.parse_args()
    print("Applying pack lang (Marketplace-safe)...")
    apply_pack_lang()


if __name__ == "__main__":
    main()
