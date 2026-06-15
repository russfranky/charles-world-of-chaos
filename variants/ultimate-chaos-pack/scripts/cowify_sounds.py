#!/usr/bin/env python3
"""Redirect mob sounds to cow moo sounds."""

from __future__ import annotations

import argparse
import copy

from common import PACK_RP, copy_vanilla_rp, load_json, save_json

COW_SAY = "mob.cow.say"
COW_HURT = "mob.cow.hurt"
COW_DEATH = "mob.cow.death"
COW_STEP = "mob.cow.step"

MOB_SOUND_EVENTS = {"ambient", "hurt", "death", "step", "attack", "warn", "mad", "scream"}


def redirect_sound_value(value):
    """Recursively redirect sound strings to cow sounds."""
    if isinstance(value, str):
        if not value or value.startswith("mob.cow") or value.startswith("game."):
            return value
        if "hurt" in value or "hit" in value:
            return COW_HURT
        if "death" in value or "die" in value:
            return COW_DEATH
        if "step" in value or "walk" in value:
            return COW_STEP
        return COW_SAY
    if isinstance(value, dict):
        result = copy.deepcopy(value)
        if "sound" in result and isinstance(result["sound"], str):
            snd = result["sound"]
            if snd and not snd.startswith("mob.cow"):
                if "hurt" in snd or "hit" in snd:
                    result["sound"] = COW_HURT
                elif "death" in snd or "die" in snd:
                    result["sound"] = COW_DEATH
                elif "step" in snd or "walk" in snd:
                    result["sound"] = COW_STEP
                else:
                    result["sound"] = COW_SAY
        else:
            for k, v in result.items():
                result[k] = redirect_sound_value(v)
        return result
    if isinstance(value, list):
        return [redirect_sound_value(v) for v in value]
    return value


def cowify_sounds(rebuild: bool = False) -> int:
    if rebuild or not PACK_RP.exists():
        copy_vanilla_rp()

    sounds_path = PACK_RP / "sounds.json"
    data = load_json(sounds_path)
    count = 0

    entity_sounds = data.get("entity_sounds", {})
    entities = entity_sounds.get("entities", {})

    for name, config in entities.items():
        if name == "cow":
            continue
        entities[name] = redirect_sound_value(config)
        count += 1

    # Redirect defaults mob-like events
    defaults = entity_sounds.get("defaults", {})
    events = defaults.get("events", {})
    for event_name in list(events.keys()):
        if event_name in MOB_SOUND_EVENTS or event_name in ("hurt", "death", "ambient"):
            old = events[event_name]
            if isinstance(old, str) and old and not old.startswith("mob.cow"):
                events[event_name] = COW_HURT if "hurt" in event_name else COW_SAY
                count += 1
            elif isinstance(old, dict):
                events[event_name] = redirect_sound_value(old)
                count += 1

    save_json(sounds_path, data)
    print(f"Redirected sounds for {count} entity sound entries")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Cowify mob sounds")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    cowify_sounds(rebuild=args.rebuild)


if __name__ == "__main__":
    main()
