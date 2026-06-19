#!/usr/bin/env python3
"""Single source of truth for shipped pack semver (manifest + release tags)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def read_version_tuple() -> tuple[int, int, int]:
    text = VERSION_FILE.read_text(encoding="utf-8").strip()
    match = SEMVER_RE.match(text)
    if not match:
        raise ValueError(f"Invalid VERSION file (expected X.Y.Z): {VERSION_FILE}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def write_version_tuple(major: int, minor: int, patch: int) -> str:
    version = f"{major}.{minor}.{patch}"
    VERSION_FILE.write_text(version + "\n", encoding="utf-8")
    return version


def pack_version_list() -> list[int]:
    return list(read_version_tuple())


def version_label() -> str:
    major, minor, patch = read_version_tuple()
    return f"v{major}.{minor}.{patch}"


def git_tag() -> str:
    return version_label()


def bump_patch() -> str:
    major, minor, patch = read_version_tuple()
    return write_version_tuple(major, minor, patch + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read or bump pack VERSION file")
    parser.add_argument("--bump-patch", action="store_true", help="Increment patch and write VERSION")
    parser.add_argument("--print", choices=("semver", "label", "tag", "tuple"), default="semver")
    args = parser.parse_args()

    if args.bump_patch:
        print(bump_patch())
        return

    if args.print == "semver":
        major, minor, patch = read_version_tuple()
        print(f"{major}.{minor}.{patch}")
    elif args.print == "label":
        print(version_label())
    elif args.print == "tag":
        print(git_tag())
    else:
        print(",".join(str(x) for x in read_version_tuple()))


if __name__ == "__main__":
    main()
