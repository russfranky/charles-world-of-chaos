#!/usr/bin/env python3
"""Pre-commit hook: block accidental API key commits."""

from __future__ import annotations

import re
import sys

ALLOWED = {".env.example"}
PATTERNS = [
    re.compile(r"VENICE_INFERENCE_KEY_[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{30,}"),
]


def main() -> int:
    failed = []
    for path in sys.argv[1:]:
        name = path.rsplit("/", 1)[-1]
        if name in ALLOWED:
            continue
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pattern in PATTERNS:
            if pattern.search(text):
                failed.append(path)
                break

    if failed:
        print("Possible API key detected in:", file=sys.stderr)
        for path in failed:
            print(f"  {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
