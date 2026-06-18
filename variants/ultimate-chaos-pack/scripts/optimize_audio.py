#!/usr/bin/env python3
"""Re-encode menu music for lite pack size (autoresearch: mcaddon_kb)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from common import PACK_RP

MENU_TRACK = PACK_RP / "sounds" / "music" / "menu" / "Bell_At_Twilight.ogg"


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def optimize_ogg(path: Path) -> int:
    """Re-encode in place if smaller. Returns bytes saved (may be negative)."""
    if not path.exists():
        return 0
    if not _ffmpeg_available():
        print("  skip audio: ffmpeg not found")
        return 0

    before = path.stat().st_size
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(path),
                "-ac",
                "1",
                "-ar",
                "44100",
                "-b:a",
                "64k",
                "-c:a",
                "libvorbis",
                str(tmp_path),
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        tmp_path.unlink(missing_ok=True)
        print(f"  skip audio {path.name}: {exc.stderr.decode(errors='replace')[:120]}", file=sys.stderr)
        return 0

    after = tmp_path.stat().st_size
    if after >= before:
        tmp_path.unlink(missing_ok=True)
        print(f"  skip audio {path.name}: encode not smaller ({after} >= {before})")
        return 0

    tmp_path.replace(path)
    saved = before - after
    print(f"  -{saved:,} B  [audio] {path.relative_to(PACK_RP)}")
    return saved


def optimize_pack_audio(pack_rp: Path = PACK_RP) -> int:
    track = pack_rp / "sounds" / "music" / "menu" / "Bell_At_Twilight.ogg"
    return optimize_ogg(track)


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize menu music in built pack")
    parser.add_argument("--pack", type=Path, default=PACK_RP)
    args = parser.parse_args()

    print("Optimizing audio (lite menu music)...")
    saved = optimize_pack_audio(args.pack)
    if saved > 0:
        print(f"Saved {saved:,} bytes on menu music")
    else:
        print("No audio savings")


if __name__ == "__main__":
    main()
