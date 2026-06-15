#!/usr/bin/env python3
"""Block releases and kid handoff until play_ready.json says the pack is worth playing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAY_READY = ROOT / "play_ready.json"


def load_status() -> dict:
    if not PLAY_READY.exists():
        return {"ready": False, "note": "Missing play_ready.json"}
    with open(PLAY_READY, encoding="utf-8") as f:
        return json.load(f)


def validate() -> bool:
    data = load_status()
    if data.get("ready") is True:
        who = data.get("signed_off_by") or "unknown"
        print(f"Play-ready: YES (signed off by {who})")
        return True

    print("PLAY NOT READY — do not hand to kids or cut a release yet.", file=sys.stderr)
    note = data.get("note", "")
    if note:
        print(f"  {note}", file=sys.stderr)
    print(f"\nEdit {PLAY_READY.relative_to(ROOT)} when iPad playtest passes:", file=sys.stderr)
    print('  "ready": true, "signed_off_by": "Russ", "signed_off_at": "2026-06-15"', file=sys.stderr)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Check play_ready.json before release")
    parser.parse_args()
    sys.exit(0 if validate() else 1)


if __name__ == "__main__":
    main()
