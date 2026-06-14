#!/usr/bin/env python3
"""Full build pipeline for Brindal & Grayson Ultimate Cow Pack."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from common import PACK_BP, PACK_RP, REPO_ROOT, VARIANT_ROOT, VANILLA_SRC

SCRIPTS = VARIANT_ROOT / "scripts"


def run_script(name: str, *args: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / name), *args]
    print(f"\n{'='*60}\n>>> {' '.join(cmd)}\n{'='*60}")
    subprocess.check_call(cmd, cwd=SCRIPTS)


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
    (script_dir / "main.js").write_text(SCRIPT_API_SOURCE, encoding="utf-8")
    print(f"Wrote {script_dir / 'main.js'}")


SCRIPT_API_SOURCE = '''/**
 * Brindal & Grayson Ultimate Cow Pack — Script API backup cowifier.
 * Transforms any non-cow mob into a cow on spawn (belt-and-suspenders with BP transforms).
 */
import { world, system } from "@minecraft/server";

const COW_TYPE = "minecraft:cow";
const SKIP_TYPES = new Set(["minecraft:cow", "minecraft:mooshroom", "minecraft:player"]);

function cowifyEntity(entity) {
    const typeId = entity.typeId;
    if (SKIP_TYPES.has(typeId)) return;
    try {
        const loc = entity.location;
        const dim = entity.dimension;
        entity.remove();
        dim.spawnEntity(COW_TYPE, loc);
    } catch (e) {
        // Entity may have been removed already
    }
}

world.afterEvents.entitySpawn.subscribe((event) => {
    system.run(() => cowifyEntity(event.entity));
});

console.warn("[BG Cow Pack] Script API cowifier active — moo!");
'''


def build_all(rebuild_textures: bool = False, skip_package: bool = False, venice: bool = False) -> None:
    ensure_vanilla_src()

    # Clean output dirs on full rebuild
    if rebuild_textures:
        for d in (PACK_RP, PACK_BP):
            if d.exists():
                shutil.rmtree(d)

    run_script("build_cow_pack.py", *(["--rebuild"] if rebuild_textures else []))
    run_script("cowify_entity_models.py")
    run_script("cowify_sounds.py")
    run_script("prune_sounds.py")
    run_script("cowify_behavior_entities.py", *(["--rebuild"] if rebuild_textures else []))
    run_script("personalize_pack.py")
    run_script("merge_custom_cows.py")
    write_script_api()

    if venice:
        run_script("venice_generate_textures.py", "--all")

    if not skip_package:
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
                        help="Generate featured textures via Venice AI (requires VENICE_API_KEY)")
    args = parser.parse_args()
    build_all(rebuild_textures=args.rebuild_textures, skip_package=args.skip_package,
              venice=args.venice)


if __name__ == "__main__":
    main()
