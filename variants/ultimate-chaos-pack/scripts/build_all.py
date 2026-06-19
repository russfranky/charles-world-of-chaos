#!/usr/bin/env python3
"""Full build pipeline for Brindal & Grayson Cow World."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

from common import PACK_BP, PACK_RP, REPO_ROOT, VANILLA_SRC, VARIANT_ROOT
from env_loader import init_env

SCRIPTS = VARIANT_ROOT / "scripts"

# Lite overlay Venice pass (surgical IDs via lite_venice_ids.py).


def run_script(name: str, *args: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / name), *args]
    print(f"\n{'='*60}\n>>> {' '.join(cmd)}\n{'='*60}")
    subprocess.check_call(cmd, cwd=SCRIPTS)


def venice_key_set() -> bool:
    return bool(os.environ.get("VENICE_API_KEY") or os.environ.get("VENICE_INFERENCE_KEY"))


def run_venice_cel_facelift(*, full: bool = False, force: bool = False) -> bool:
    """Generate textures via Venice AI; cel-bake runs in finalize_texture + polish pass."""
    if not venice_key_set():
        print("Venice API key not set — skip AI cel facelift (export VENICE_API_KEY)")
        return False
    flag = ["--force"] if force else []
    script = "full_venice_ids.py" if full else "lite_venice_ids.py"
    ids = subprocess.check_output(
        [sys.executable, str(SCRIPTS / script)],
        cwd=SCRIPTS,
        text=True,
    ).strip()
    n = len(ids.split(",")) if ids else 0
    label = "full manifest" if full else "lite overlay"
    print(f"Venice cel facelift: {n} textures ({label})")
    run_script("venice_generate_textures.py", "--skip-anchor", "--id", ids, *flag)
    return True


def ensure_vanilla_src() -> None:
    if VANILLA_SRC.exists() and (VANILLA_SRC / "resource_pack").exists():
        print("vanilla_src already present")
        return

    print("Cloning Mojang bedrock-samples (sparse)...")
    if VANILLA_SRC.exists():
        shutil.rmtree(VANILLA_SRC)

    subprocess.check_call([
        "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
        "https://github.com/Mojang/bedrock-samples.git", str(VANILLA_SRC),
    ], cwd=REPO_ROOT)
    subprocess.check_call(
        ["git", "sparse-checkout", "set", "resource_pack", "behavior_pack"],
        cwd=VANILLA_SRC,
    )


def write_script_api() -> None:
    script_dir = PACK_BP / "scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    src = VARIANT_ROOT / "script_api" / "main.js"
    if not src.exists():
        raise FileNotFoundError(f"Script API source missing: {src}")
    shutil.copy2(src, script_dir / "main.js")
    print(f"Wrote {script_dir / 'main.js'}")


def build_all(
    rebuild_textures: bool = False,
    skip_package: bool = False,
    venice: bool = False,
    venice_audio: bool = False,
    venice_force: bool = False,
    procedural_fallback: bool = False,
    full: bool = False,
) -> None:
    ensure_vanilla_src()
    init_env()

    if rebuild_textures:
        for d in (PACK_RP, PACK_BP):
            if d.exists():
                shutil.rmtree(d)

    use_venice = venice or venice_key_set()

    if full:
        print("=== FULL texture pack (all vanilla PNGs + cel bake) ===")
        run_script("prepare_full_pack.py")
    else:
        run_script("prepare_lite_pack.py")

    run_script("personalize_pack.py")
    run_script("merge_custom_cows.py")
    write_script_api()
    run_script("apply_pack_lang.py")
    run_script("apply_audio_overrides.py", "--lite")
    run_script("optimize_audio.py")

    if venice_audio:
        run_script("venice_generate_audio.py", "--batch", "1")

    if use_venice:
        run_venice_cel_facelift(full=full, force=venice_force)
    elif procedural_fallback or os.environ.get("COWIFY_PROCEDURAL") == "1":
        print("No Venice key — optional procedural overlay (COWIFY_PROCEDURAL=1)")
        run_script("cowify_kid_textures.py")
    else:
        mode = "full vanilla + cel polish" if full else "lite staging + cel polish"
        print(f"Texture path: {mode} (set VENICE_API_KEY for AI hero art)")

    # Cel bake on all pack PNGs (Venice heroes + every other texture when --full).
    run_script("polish_textures.py", "--sources")
    run_script("polish_textures.py")

    if not skip_package:
        run_script("optimize_pngs.py")
        if full:
            run_script("package_mcpack.py", "--output", str(REPO_ROOT / "dist" / "brindal-grayson-cow-pack-full.mcpack"))
            run_script("package_mcaddon.py", "--output", str(REPO_ROOT / "dist" / "brindal-grayson-cow-pack-full.mcaddon"))
        else:
            run_script("package_mcpack.py")
            run_script("package_mcaddon.py")

    print("\nBuild complete!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Full cow pack build pipeline")
    parser.add_argument("--rebuild-textures", action="store_true",
                        help="Recopy vanilla source and rebuild all textures")
    parser.add_argument("--skip-package", action="store_true",
                        help="Skip packaging .mcpack/.mcaddon")
    parser.add_argument("--venice", action="store_true",
                        help="Venice AI cel facelift (auto when VENICE_API_KEY is set)")
    parser.add_argument("--venice-force", action="store_true",
                        help="Regenerate Venice textures even if cached")
    parser.add_argument("--venice-audio", action="store_true",
                        help="Generate batch-1 audio via Venice AI (requires VENICE_API_KEY)")
    parser.add_argument("--procedural-fallback", action="store_true",
                        help="Use legacy procedural overlays when Venice key missing")
    parser.add_argument("--full", action="store_true",
                        help="Full vanilla RP (~5k textures) + cel bake on every PNG")
    args = parser.parse_args()
    build_all(
        rebuild_textures=args.rebuild_textures,
        skip_package=args.skip_package,
        venice=args.venice,
        venice_audio=args.venice_audio,
        venice_force=args.venice_force,
        procedural_fallback=args.procedural_fallback,
        full=args.full,
    )


if __name__ == "__main__":
    main()
