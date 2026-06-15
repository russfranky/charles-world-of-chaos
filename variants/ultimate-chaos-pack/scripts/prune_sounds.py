#!/usr/bin/env python3
"""Remove bundled mob sound files — vanilla game provides them at runtime."""

from __future__ import annotations

import argparse
import shutil

from common import PACK_RP

KEEP_MOB_DIRS = {"cow", "moody_cow"}


def prune_mob_sounds() -> int:
    mob_dir = PACK_RP / "sounds" / "mob"
    if not mob_dir.exists():
        return 0

    removed = 0
    for entry in mob_dir.iterdir():
        if entry.is_dir() and entry.name not in KEEP_MOB_DIRS:
            count = sum(1 for _ in entry.rglob("*") if _.is_file())
            shutil.rmtree(entry)
            removed += count
        elif entry.is_file():
            entry.unlink()
            removed += 1

    print(f"Pruned {removed} unused mob sound files")
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Prune unused mob sounds")
    args = parser.parse_args()
    prune_mob_sounds()


if __name__ == "__main__":
    main()
