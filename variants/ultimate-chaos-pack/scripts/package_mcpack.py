#!/usr/bin/env python3
"""Package resource pack as .mcpack."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from common import DIST, PACK_RP


def package_mcpack(output: Path | None = None) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    out = output or DIST / "brindal-grayson-cow-pack.mcpack"

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACK_RP.rglob("*")):
            if path.is_file() and ".DS_Store" not in path.name:
                zf.write(path, path.relative_to(PACK_RP))

    print(f"Packaged MCPACK: {out} ({out.stat().st_size:,} bytes)")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Package resource pack as MCPACK")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    package_mcpack(args.output)


if __name__ == "__main__":
    main()
