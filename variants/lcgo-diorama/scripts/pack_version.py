#!/usr/bin/env python3
"""Read or bump the Lara Croft GO Diorama pack semver."""

from __future__ import annotations

import argparse
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


def read_version() -> tuple[int, int, int]:
    text = VERSION_FILE.read_text().strip()
    parts = text.split(".")
    if len(parts) != 3:
        raise SystemExit(f"Invalid VERSION format in {VERSION_FILE}: {text!r}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def write_version(major: int, minor: int, patch: int) -> None:
    VERSION_FILE.write_text(f"{major}.{minor}.{patch}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="LC GO Diorama pack version helper")
    parser.add_argument("--bump-patch", action="store_true")
    parser.add_argument("--print", choices=["semver", "tag", "label"], dest="print_field")
    args = parser.parse_args()

    major, minor, patch = read_version()
    if args.bump_patch:
        patch += 1
        write_version(major, minor, patch)

    if args.print_field == "semver":
        print(f"{major}.{minor}.{patch}")
    elif args.print_field == "tag":
        print(f"v{major}.{minor}.{patch}")
    elif args.print_field == "label":
        print(f"{major}.{minor}.{patch}")


if __name__ == "__main__":
    main()
