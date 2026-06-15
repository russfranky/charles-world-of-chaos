#!/usr/bin/env python3
"""Block publish when shipped mobs are not approved in mob-index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_JSON = ROOT / "docs" / "mob-index" / "mob-index.json"
APPROVALS_FILE = ROOT / "docs" / "mob-index" / "mob-approvals.json"


def validate(*, strict: bool = False) -> bool:
    if not INDEX_JSON.exists():
        print("Mob index missing — run: python3 scripts/generate_mob_index.py", file=sys.stderr)
        return False

    with open(INDEX_JSON, encoding="utf-8") as f:
        data = json.load(f)

    blockers = [
        m for m in data.get("mobs", [])
        if m.get("shipped") and not m.get("approved")
    ]
    missing_preview = [
        m for m in data.get("mobs", [])
        if m.get("shipped") and not m.get("has_texture")
    ]

    if blockers:
        print("MOB APPROVAL FAILED — shipped mobs not approved:", file=sys.stderr)
        for m in blockers:
            print(f"  ✗ {m['id']} ({m['name']}) — edit {APPROVALS_FILE.relative_to(ROOT)}", file=sys.stderr)
        return False

    if missing_preview:
        print("Warning: shipped mobs missing preview textures:", file=sys.stderr)
        for m in missing_preview:
            print(f"  ⚠ {m['id']}", file=sys.stderr)
        if strict:
            return False

    summary = data.get("summary", {})
    print(
        f"Mob approvals OK — {summary.get('shipped', 0)} shipped, "
        f"{summary.get('approved', 0)} approved, {summary.get('total', 0)} cataloged"
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate mob approvals before publish")
    parser.add_argument("--strict", action="store_true", help="Fail on missing previews too")
    args = parser.parse_args()
    sys.exit(0 if validate(strict=args.strict) else 1)


if __name__ == "__main__":
    main()
