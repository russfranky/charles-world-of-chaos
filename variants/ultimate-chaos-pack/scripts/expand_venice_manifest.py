#!/usr/bin/env python3
"""Append featured Venice texture entries to venice_prompts.json (idempotent)."""

from __future__ import annotations

import json
from pathlib import Path

PROMPTS_FILE = Path(__file__).resolve().parent.parent / "prompts" / "venice_prompts.json"

# High-quality comedy prompts matching existing manifest tone.
NEW_TEXTURES = [
    # --- Hostile mobs ---
    {
        "id": "wither_skeleton",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/skeleton/wither_skeleton.png",
        "prompt": "Minecraft skin texture UV sheet, 64x64. A wither skeleton made of charcoal-black cow bones — ribcage like a cow skeleton, skull is a cow skull with curved horns, holding a stone sword. Faint Holstein spots on bones where marrow glows. Menacing but silly. Flat pixel art, Minecraft entity template, transparent background.",
    },
    {
        "id": "guardian",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/guardian.png",
        "prompt": "Minecraft entity texture sheet, flat UV, 64x64. A fish guardian with Holstein cow-spotted scales, one giant dopey cow eye in the center, spikes replaced with tiny horns. Pink udder underside. Looks deeply offended. Flat pixel art, hard edges, Minecraft template layout, transparent background.",
    },
    {
        "id": "slime",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/slime/slime.png",
        "prompt": "Minecraft entity texture sheet, 64x64 flat UV. A translucent green slime cube with a cow face visible inside like a trapped mascot in jello. Black and white spots float inside the gel. Comically squished expression. Flat pixel art, Minecraft style, transparent background.",
    },
    {
        "id": "pillager",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/pillager.png",
        "prompt": "Minecraft skin texture sheet, flat UV, 64x64. An illager bandit wearing a cow-print bandana mask and Holstein spotted poncho, crossbow made from a cow femur. Angry eyebrows but cow nose visible. Flat pixel art, Minecraft entity template, transparent background.",
    },
    {
        "id": "ravager",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/illager/ravager.png",
        "prompt": "Minecraft entity texture sheet, 64x64 flat UV. A massive beast with enormous cow horns, Holstein hide armor plates, iron saddle with cowbell dangling. Mouth full of hay. Looks like a bull that raided a village. Flat pixel art, hard edges, Minecraft template, transparent background.",
    },
    {
        "id": "warden",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/warden/warden.png",
        "prompt": "Minecraft entity texture sheet, flat UV, 64x64. A dark teal warden with bioluminescent Holstein cow spots pulsing on its chest. No eyes — just a glowing cow nose silhouette. Scary but absurdly spotted. Flat pixel art, Minecraft template layout, transparent background.",
    },
    {
        "id": "breeze",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/breeze/breeze.png",
        "prompt": "Minecraft entity texture sheet, 64x64 flat UV. A wind spirit made of swirling cream-and-black cow-print mist, tiny horns of compressed air, eyes like spinning cowbells. Whimsical tornado shape. Flat pixel art, hard edges, Minecraft template, transparent background.",
    },
    {
        "id": "elder_guardian",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/guardian_elder.png",
        "prompt": "Minecraft entity texture sheet, flat UV, 64x64. A giant elder guardian fish with pale cow-spotted scales, enormous tired cow eye, crown of coral shaped like horns. Ancient and judgmental. Flat pixel art, Minecraft template, transparent background.",
    },
    {
        "id": "wither_boss",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/wither_boss/wither.png",
        "prompt": "Minecraft entity texture sheet, 64x64 flat UV. The Wither boss with three cow skull heads instead of skeleton skulls, each with horns. Dark body with charcoal Holstein spots. Ribcage exposed like a cow skeleton. Terrifying but ridiculous. Flat pixel art, Minecraft template, transparent background.",
    },
    # --- Passive / neutral mobs ---
    {
        "id": "chicken",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/chicken/chicken.png",
        "prompt": "Minecraft skin texture sheet, 64x64 flat UV. A chicken with Holstein cow-spotted feathers, tiny useless cow horns on its head, beak still visible. Lays milk instead of eggs (tiny milk bottle under wing). Flat pixel art, Minecraft entity template, transparent background.",
    },
    {
        "id": "horse",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/horse/horse_brown.png",
        "prompt": "Minecraft entity texture sheet, flat UV, 64x64. A horse wearing a full Holstein cow-print bodysuit over its brown coat, cardboard cow ears, tail is a cow tail. Horse face peeking out confused. Flat pixel art, Minecraft template, transparent background.",
    },
    {
        "id": "wolf",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/wolf/wolf.png",
        "prompt": "Minecraft entity texture sheet, 64x64 flat UV. A wolf with fluffy Holstein cow-spotted fur, floppy cow ears, pink udder on belly. Still has wolf fangs but looks embarrassed about the costume. Flat pixel art, hard edges, Minecraft template, transparent background.",
    },
    {
        "id": "cat",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/cat/blackcat.png",
        "prompt": "Minecraft skin texture sheet, flat UV, 64x64. A black cat with Holstein white cow spots painted on (badly), tiny cow horns headband, tail has a cowbell. Cat eyes still judging everyone. Flat pixel art, Minecraft entity template, transparent background.",
    },
    {
        "id": "bee",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/bee/bee.png",
        "prompt": "Minecraft entity texture sheet, 64x64 flat UV. A bee with black and white Holstein stripes replacing yellow-black, tiny cow horns on head, wings shaped like milk carton flaps. Buzzing angrily. Flat pixel art, Minecraft template, transparent background.",
    },
    {
        "id": "iron_golem",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/iron_golem.png",
        "prompt": "Minecraft entity texture sheet, flat UV, 64x64. An iron golem with cow-pattern metal plates welded on, face is a stamped cow face with horns, poppy replaced with a daisy. Village protector cosplaying as a cow. Flat pixel art, hard edges, Minecraft template, transparent background.",
    },
    {
        "id": "villager",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/villager/villager.png",
        "prompt": "Minecraft villager skin texture sheet, flat UV, 64x64. A villager wearing a Holstein cow-print robe with hood, cow horn headpiece poking through, big nose still visible. Holding a milk bucket. Flat pixel art, Minecraft entity template, transparent background.",
    },
    {
        "id": "brindal_cow",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/brindal_cow.png",
        "prompt": "Minecraft player skin texture sheet, 64x64 flat UV. Cute child character Brindal wearing a full brown-and-white Holstein cow costume onesie with hood ears, pink udder on belly, tiny crown on head, letter B on chest. Adorable, joyful. Flat pixel art, Minecraft skin template, transparent background.",
    },
    {
        "id": "grayson_cow",
        "category": "entity",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 64,
        "pack_path": "textures/entity/grayson_cow.png",
        "prompt": "Minecraft player skin texture sheet, 64x64 flat UV. Cute child character Grayson wearing a gray cow costume onesie with hood horns, dark Holstein spots, letter G on chest, cow tail. Mischievous grin. Flat pixel art, Minecraft skin template, transparent background.",
    },
    # --- Blocks ---
    {
        "id": "coal_ore",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/coal_ore.png",
        "prompt": "Seamless tile. Gray stone with dark black coal ore spots arranged like Holstein cow spots on white-gray stone. Minecraft ore block texture, flat pixel art, hard edges, tileable.",
    },
    {
        "id": "iron_ore",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/iron_ore.png",
        "prompt": "Seamless tile. Stone with tan-beige iron ore flecks on Holstein black-and-white cow-spotted stone base. Minecraft ore texture, flat colors, tileable.",
    },
    {
        "id": "gold_ore",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/gold_ore.png",
        "prompt": "Seamless tile. Stone with golden-yellow ore spots on black-and-white cow hide pattern background. Minecraft gold ore block, flat pixel art, tileable.",
    },
    {
        "id": "emerald_ore",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/emerald_ore.png",
        "prompt": "Seamless tile. Dark stone with green emerald crystals scattered on Holstein cow-pattern background. Minecraft ore texture, flat pixel art, tileable.",
    },
    {
        "id": "grass_top",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/grass_top.png",
        "prompt": "Seamless tile. Green grass block top with grass blades forming subtle cow spot patterns in darker green. Minecraft grass texture, flat shading, tileable.",
    },
    {
        "id": "netherrack",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/netherrack.png",
        "prompt": "Seamless tile. Dark red netherrack surface with black cow spot pattern baked into the rock. Nether dimension block, flat pixel art, tileable.",
    },
    {
        "id": "soul_sand",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/soul_sand.png",
        "prompt": "Seamless tile. Dark brown soul sand with screaming cow face impressions pressed into the surface. Eerie but silly. Minecraft block texture, flat pixel art, tileable.",
    },
    {
        "id": "end_stone",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/end_stone.png",
        "prompt": "Seamless tile. Pale yellow end stone with cream cow spot pattern. The End dimension block, flat colors, Minecraft style, tileable.",
    },
    {
        "id": "cobblestone",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/cobblestone.png",
        "prompt": "Seamless tile. Gray cobblestone pieces with Holstein black-and-white patches on individual stones. Minecraft block texture, flat pixel art, tileable.",
    },
    {
        "id": "furnace_front",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/furnace_front_off.png",
        "also_apply": ["textures/blocks/furnace_front_on.png"],
        "prompt": "Stone furnace front face with cow-nose shaped opening, dark interior. Off version unlit. Minecraft block texture, flat pixel art.",
    },
    {
        "id": "chest_front",
        "category": "block",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/blocks/chest_front.png",
        "prompt": "Wooden chest front with cow face latch design and Holstein spots on the wood planks. Minecraft block texture, flat pixel art.",
    },
    # --- Items ---
    {
        "id": "steak",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/beef_cooked.png",
        "prompt": "Item sprite. Cooked beef steak with grill marks shaped like tiny cow spots, brown and juicy. Minecraft item icon, 45-degree angle, transparent background.",
    },
    {
        "id": "milk_bucket",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/bucket_milk.png",
        "prompt": "Item sprite. Gray bucket overflowing with white milk, Holstein cow spot pattern on the bucket sides. Minecraft item icon, transparent background.",
    },
    {
        "id": "golden_apple",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/apple_golden.png",
        "prompt": "Item sprite. Golden apple with tiny cow silhouette shine reflection on the surface. Magical golden glow. Minecraft item icon, transparent background.",
    },
    {
        "id": "leather",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/leather.png",
        "prompt": "Item sprite. Brown cowhide leather piece with visible Holstein black and white spots. Minecraft item icon, transparent background.",
    },
    {
        "id": "diamond",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/diamond.png",
        "prompt": "Item sprite. Cyan diamond gem with tiny cow silhouette reflection inside the facets. Minecraft item icon, transparent background.",
    },
    {
        "id": "bow",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/bow_standby.png",
        "prompt": "Item sprite. Bow made from a curved cow horn, leather string, wooden grip with cow spot inlay. Minecraft item icon, transparent background.",
    },
    {
        "id": "bread",
        "category": "item",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 16,
        "pack_path": "textures/items/bread.png",
        "prompt": "Item sprite. Bread loaf with Holstein cow spot pattern on the crust. Minecraft food item icon, transparent background.",
    },
    # --- GUI ---
    {
        "id": "heart",
        "category": "gui",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 9,
        "pack_path": "textures/ui/heart.png",
        "prompt": "Minecraft HUD icon. Red heart shape with subtle Holstein cow spots, full health heart. Tiny pixel art, transparent background.",
    },
    {
        "id": "hunger",
        "category": "gui",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 9,
        "pack_path": "textures/ui/hunger_full.png",
        "prompt": "Minecraft HUD icon. Cooked cow steak replacing the hunger drumstick, brown with grill marks. Full hunger icon. Tiny pixel art, transparent background.",
    },
    {
        "id": "crosshair",
        "category": "gui",
        "model": "flux-2-pro",
        "generate_size": 1024,
        "target_size": 15,
        "pack_path": "textures/ui/thumbnail_crosshair.png",
        "prompt": "Minecraft crosshair. Cow nose nostrils shape — two dark oval nostrils with a horizontal line between them. Centered targeting reticle. Tiny pixel art, transparent background.",
    },
]


def main() -> None:
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        manifest = json.load(f)

    existing_ids = {t["id"] for t in manifest["textures"]}
    added = 0
    for entry in NEW_TEXTURES:
        if entry["id"] not in existing_ids:
            manifest["textures"].append(entry)
            existing_ids.add(entry["id"])
            added += 1

    manifest["version"] = 2
    with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Added {added} new textures ({len(manifest['textures'])} total)")


if __name__ == "__main__":
    main()
