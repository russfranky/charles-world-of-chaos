#!/usr/bin/env python3
"""Package behavior + resource packs as .mcaddon."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from common import DIST, PACK_BP, PACK_RP


def package_mcaddon(output: Path | None = None) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    out = output or DIST / "brindal-grayson-cow-pack.mcaddon"

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for pack_dir in (PACK_RP, PACK_BP):
            for path in sorted(pack_dir.rglob("*")):
                if path.is_file() and ".DS_Store" not in path.name:
                    zf.write(path, path.relative_to(pack_dir.parent))

    print(f"Packaged MCADDON: {out} ({out.stat().st_size:,} bytes)")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Package full add-on as MCADDON")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    package_mcaddon(args.output)


if __name__ == "__main__":
    main()
