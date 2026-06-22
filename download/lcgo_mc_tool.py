#!/usr/bin/env python3
"""
LC GO MC Texture Pack Generator & Voxel Converter
==================================================

Generates a Bedrock 1.21+ resource pack (.mcpack) with the LC GO sunlit
outdoor diorama aesthetic: warm stone + Holstein spots + 4-step cel bands
+ ink outlines. Also converts LC GO level JSON into Bedrock /setblock
command lists.

Usage:
    python3 lcgo_mc_tool.py --mode all
    python3 lcgo_mc_tool.py --mode textures --output ./out
    python3 lcgo_mc_tool.py --mode pack --output ./out
    python3 lcgo_mc_tool.py --mode convert --level sample_level.json --output ./out
"""

import argparse
import json
import os
import random
import uuid
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

# ============================================================================
# COLOR PALETTE — Sunlit outdoor LC GO aesthetic
# ============================================================================
# 4-step cel bands (lit / light_mid / dark_mid / shadow) plus ink, bronze,
# cool_blue, moss variants, water variants, gold, jade. Every color is warm-
# biased to match Routon's art-direction mandate (Pocket Gamer interview).
# ============================================================================
PALETTE = {
    # 4-step cel bands
    'lit':         (244, 228, 193),  # warm cream (sunlit top face)
    'light_mid':   (212, 184, 150),  # warm sand (sunlit side face)
    'dark_mid':    (138, 111,  79),  # warm brown (occluded side)
    'shadow':      ( 74,  53,  40),  # deep warm brown (caves / underhangs)
    'ink':         ( 26,  15,   8),  # near-black warm (outlines)

    # LC GO signature accents
    'bronze':      (184, 136,  74),  # LC GO tomb gold
    'cool_blue':   ( 61, 107, 138),  # LC GO shadow blue (rare cool accent)

    # Outdoor organics
    'moss_lit':    (160, 184,  92),  # lit leaves
    'moss_mid':    (108, 130,  68),  # mid leaves
    'moss_dark':   ( 64,  82,  40),  # shadow leaves
    'bark_lit':    (188, 144,  92),  # lit wood
    'bark_mid':    (140, 100,  60),  # mid wood
    'bark_dark':   ( 84,  56,  32),  # shadow wood
    'dirt_lit':    (160, 116,  76),  # lit dirt
    'dirt_mid':    (112,  76,  48),  # mid dirt
    'dirt_dark':   ( 68,  44,  28),  # shadow dirt

    # Water (static)
    'water_lit':   (140, 178, 196),
    'water_mid':   ( 88, 138, 158),
    'water_dark':  ( 48,  88, 110),

    # Relics (replaces vanilla gold/emerald/copper)
    'gold_lit':    (240, 198,  92),
    'gold_mid':    (192, 144,  56),
    'gold_dark':   (130,  88,  28),
    'jade_lit':    (148, 196, 156),
    'jade_mid':    ( 92, 152, 110),
    'jade_dark':   ( 56, 102,  72),
    'bronze_relic_lit':  (212, 144,  76),
    'bronze_relic_mid':  (160, 100,  48),
    'bronze_relic_dark': (108,  64,  28),
}

# ============================================================================
# HOLSTEIN SPOT GENERATION
# ============================================================================
def holstein_spot_mask(size, spot_count, seed, min_r, max_r):
    """
    Generate a set of (x, y) pixels that form irregular Holstein-style spots.
    The spots are NOT perfect circles — radius is perturbed per angle to
    create organic blobby shapes reminiscent of LC GO's graphic illustration
    style (Thierry Doizon's art direction, see Target 12 of source report).
    """
    rng = random.Random(seed)
    spots = set()
    for _ in range(spot_count):
        cx = rng.randint(2, size - 3)
        cy = rng.randint(2, size - 3)
        # Sample 8 perturbed radii around the blob
        angles = 8
        radii = [rng.uniform(min_r, max_r) for _ in range(angles)]
        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = (dx*dx + dy*dy) ** 0.5
                if dist == 0:
                    angle_idx = 0
                else:
                    angle = (rng.random() * 2 * 3.14159)  # perturb
                    angle_idx = int(angle / (2 * 3.14159) * angles) % angles
                if dist < radii[angle_idx]:
                    spots.add((x, y))
    return spots

def darken(color, amount=40):
    return tuple(max(0, c - amount) for c in color)

def lighten(color, amount=40):
    return tuple(min(255, c + amount) for c in color)

# ============================================================================
# TEXTURE GENERATORS
# ============================================================================
SIZE = 16

def make_block_texture(base_color, spot_color=None, spot_count=3,
                       min_r=2, max_r=5, outline=True, seed=0,
                       noise_amount=10):
    """
    Generate a 16x16 block texture with:
    - Base fill in `base_color` (one of the 4 cel bands)
    - 2-4 irregular Holstein spots in `spot_color` (defaults to darker band)
    - Subtle per-pixel brightness noise for grain
    - 1px ink border if `outline=True`
    """
    rng = random.Random(seed)
    img = Image.new('RGB', (SIZE, SIZE), base_color)
    draw = ImageDraw.Draw(img)

    # Subtle per-pixel noise (1-2 brightness units, warm-biased)
    pixels = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            n = rng.randint(-noise_amount, noise_amount)
            r, g, b = pixels[x, y]
            pixels[x, y] = (max(0, min(255, r + n)),
                            max(0, min(255, g + n)),
                            max(0, min(255, b + max(0, n // 2))))

    # Holstein spots
    if spot_color is None:
        spot_color = darken(base_color, 50)
    spot_pixels = holstein_spot_mask(SIZE, spot_count, seed, min_r, max_r)
    for (x, y) in spot_pixels:
        if 0 <= x < SIZE and 0 <= y < SIZE:
            img.putpixel((x, y), spot_color)

    # 1px ink border (the "cel outline")
    if outline:
        ink = PALETTE['ink']
        for i in range(SIZE):
            img.putpixel((i, 0), ink)
            img.putpixel((i, SIZE - 1), ink)
            img.putpixel((0, i), ink)
            img.putpixel((SIZE - 1, i), ink)

    return img

def make_log_side_texture(bark_color, ring_color, seed=0):
    """Wood log side: vertical bark stripes with occasional dark knot."""
    rng = random.Random(seed)
    img = Image.new('RGB', (SIZE, SIZE), bark_color)
    # Vertical bark stripes — every 3rd column darker
    for x in range(SIZE):
        stripe_strength = rng.random()
        if stripe_strength > 0.6:
            shade = darken(bark_color, 35)
            for y in range(SIZE):
                if rng.random() < 0.7:
                    img.putpixel((x, y), shade)
        elif stripe_strength > 0.3:
            shade = darken(bark_color, 15)
            for y in range(SIZE):
                if rng.random() < 0.5:
                    img.putpixel((x, y), shade)
    # Occasional horizontal bark line
    for y in [3, 7, 11]:
        if rng.random() < 0.5:
            shade = darken(bark_color, 25)
            for x in range(SIZE):
                if rng.random() < 0.6:
                    img.putpixel((x, y), shade)
    # Ink border
    ink = PALETTE['ink']
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img

def make_log_top_texture(ring_color, seed=0):
    """Wood log top: concentric rings centered on block."""
    rng = random.Random(seed)
    img = Image.new('RGB', (SIZE, SIZE), ring_color)
    cx, cy = SIZE // 2, SIZE // 2
    for y in range(SIZE):
        for x in range(SIZE):
            dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
            ring_index = int(dist) % 2
            if ring_index == 0:
                img.putpixel((x, y), darken(ring_color, 25))
            else:
                # tiny noise
                n = rng.randint(-8, 8)
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (max(0, min(255, r+n)),
                                       max(0, min(255, g+n)),
                                       max(0, min(255, b+n))))
    # Ink border
    ink = PALETTE['ink']
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img

def make_leaves_texture(base_color, lit_color, seed=0):
    """Leaves: clumpy organic texture with lit highlights."""
    rng = random.Random(seed)
    img = Image.new('RGB', (SIZE, SIZE), base_color)
    # Random lit clumps
    for _ in range(8):
        cx = rng.randint(1, SIZE - 2)
        cy = rng.randint(1, SIZE - 2)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if rng.random() < 0.6:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < SIZE and 0 <= y < SIZE:
                        img.putpixel((x, y), lit_color)
    # Dark gaps between leaves
    for _ in range(6):
        cx = rng.randint(0, SIZE - 1)
        cy = rng.randint(0, SIZE - 1)
        img.putpixel((cx, cy), PALETTE['ink'])
    # Ink border
    ink = PALETTE['ink']
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img

def make_water_texture(base_color, foam_color, seed=0):
    """Water: horizontal ripple bands."""
    rng = random.Random(seed)
    img = Image.new('RGB', (SIZE, SIZE), base_color)
    # 3 ripple bands
    for y in [2, 7, 12]:
        for x in range(SIZE):
            if rng.random() < 0.5:
                img.putpixel((x, y), foam_color)
    # Subtle horizontal streaks
    for y in range(SIZE):
        if rng.random() < 0.3:
            shade = darken(base_color, 15)
            for x in range(SIZE):
                if rng.random() < 0.3:
                    img.putpixel((x, y), shade)
    # NO ink border on water (water flows visually)
    return img

def make_relic_block_texture(lit, mid, dark, accent, seed=0):
    """Relic block: bright central gem with dark frame, like a treasure."""
    rng = random.Random(seed)
    img = Image.new('RGB', (SIZE, SIZE), mid)
    # Central 8x8 gem area in lit color
    for y in range(4, 12):
        for x in range(4, 12):
            img.putpixel((x, y), lit)
    # Diagonal highlight on gem
    for i in range(4, 12):
        n = rng.randint(-15, 15)
        c = lighten(lit, 20)
        img.putpixel((i, i), (max(0, min(255, c[0]+n)),
                              max(0, min(255, c[1]+n)),
                              max(0, min(255, c[2]+n))))
    # Corner accents in dark color
    for (x, y) in [(0,0),(0,15),(15,0),(15,15),(1,1),(1,14),(14,1),(14,14)]:
        img.putpixel((x, y), dark)
    # 4 small accent dots (treasure marker)
    for (x, y) in [(2,2),(13,2),(2,13),(13,13)]:
        img.putpixel((x, y), accent)
    # Ink border
    ink = PALETTE['ink']
    for i in range(SIZE):
        img.putpixel((i, 0), ink)
        img.putpixel((i, SIZE - 1), ink)
        img.putpixel((0, i), ink)
        img.putpixel((SIZE - 1, i), ink)
    return img

# ============================================================================
# ITEM TEXTURE GENERATORS (Relics)
# ============================================================================
def make_incan_bottle(seed=0):
    """Incan bottle relic: small clay pot shape."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    rng = random.Random(seed)
    # Bottle body (rows 5-13)
    body_color = PALETTE['bronze_relic_mid']
    body_dark = PALETTE['bronze_relic_dark']
    body_lit = PALETTE['bronze_relic_lit']
    # Outline silhouette
    silhouette = [
        # x range per row, 0-indexed from top
        (6, 9),   # 0 - empty top
        (6, 9),   # 1 - neck top
        (6, 9),   # 2 - neck
        (6, 9),   # 3 - neck
        (5, 10),  # 4 - shoulder
        (4, 11),  # 5 - body widen
        (4, 11),  # 6 - body
        (4, 11),  # 7 - body
        (4, 11),  # 8 - body
        (4, 11),  # 9 - body
        (4, 11),  # 10 - body
        (5, 10),  # 11 - base
        (5, 10),  # 12 - base
        (6, 9),   # 13 - foot
    ]
    for y, (x0, x1) in enumerate(silhouette):
        for x in range(x0, x1 + 1):
            # Lit on left side, dark on right
            if x < (x0 + x1) // 2:
                img.putpixel((x, y), body_lit + (255,))
            else:
                img.putpixel((x, y), body_color + (255,))
    # Ink outline (left & right edges only — top/bottom fade)
    for y, (x0, x1) in enumerate(silhouette):
        img.putpixel((x0, y), PALETTE['ink'] + (255,))
        img.putpixel((x1, y), PALETTE['ink'] + (255,))
    return img

def make_jade_mask(seed=0):
    """Jade mask relic: stylized face shape."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    # Oval face
    face_color = PALETTE['jade_mid']
    face_lit = PALETTE['jade_lit']
    face_dark = PALETTE['jade_dark']
    face_outline = [
        (5, 10), (4, 11), (4, 11), (4, 11), (4, 11),  # rows 3-7
        (4, 11), (4, 11), (5, 10), (5, 10), (6, 9),   # rows 8-12
    ]
    for y_idx, (x0, x1) in enumerate(face_outline):
        y = y_idx + 3
        for x in range(x0, x1 + 1):
            # Lit on upper-left
            if x < (x0 + x1) // 2 and y < 8:
                img.putpixel((x, y), face_lit + (255,))
            elif x >= (x0 + x1) // 2 and y >= 8:
                img.putpixel((x, y), face_dark + (255,))
            else:
                img.putpixel((x, y), face_color + (255,))
    # Eyes (two dark holes)
    for (ex, ey) in [(6, 6), (9, 6)]:
        img.putpixel((ex, ey), PALETTE['ink'] + (255,))
    # Mouth (dark slit)
    for x in range(6, 10):
        img.putpixel((x, 10), PALETTE['ink'] + (255,))
    # Outline
    for y_idx, (x0, x1) in enumerate(face_outline):
        y = y_idx + 3
        img.putpixel((x0, y), PALETTE['ink'] + (255,))
        img.putpixel((x1, y), PALETTE['ink'] + (255,))
    return img

def make_bronze_coin(seed=0):
    """Bronze coin relic: circular coin with center hole."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    rng = random.Random(seed)
    coin_lit = PALETTE['bronze_relic_lit']
    coin_mid = PALETTE['bronze_relic_mid']
    coin_dark = PALETTE['bronze_relic_dark']
    cx, cy = 8, 8
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            if 3 < dist < 6:
                # Lit on upper-left, dark on lower-right
                if dx < 0 and dy < 0:
                    img.putpixel((x, y), coin_lit + (255,))
                elif dx > 0 and dy > 0:
                    img.putpixel((x, y), coin_dark + (255,))
                else:
                    img.putpixel((x, y), coin_mid + (255,))
            elif dist <= 3:
                # Center hole — dark
                if dist < 2.5:
                    img.putpixel((x, y), PALETTE['ink'] + (255,))
    # Outer ink ring
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            if 5.5 < dist < 6.5:
                img.putpixel((x, y), PALETTE['ink'] + (255,))
    return img

def make_crystal_shard(seed=0):
    """Crystal shard relic: angular shard shape."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    # Diamond shape
    shard_lit = (200, 230, 240)
    shard_mid = (140, 180, 200)
    shard_dark = (80, 120, 150)
    # Diamond points
    points = [(8, 1), (13, 8), (8, 14), (3, 8)]
    # Fill diamond
    for y in range(SIZE):
        for x in range(SIZE):
            # Point-in-diamond test (rotated square)
            dx = abs(x - 8)
            dy = abs(y - 8)
            if dx + dy < 6:
                # Lit on upper portion, dark on lower
                if y < 8 and x < 8:
                    img.putpixel((x, y), shard_lit + (255,))
                elif y > 8 and x > 8:
                    img.putpixel((x, y), shard_dark + (255,))
                else:
                    img.putpixel((x, y), shard_mid + (255,))
    # Ink outline (the diamond edges)
    for y in range(SIZE):
        for x in range(SIZE):
            dx = abs(x - 8)
            dy = abs(y - 8)
            if abs(dx + dy - 5) < 1:
                img.putpixel((x, y), PALETTE['ink'] + (255,))
    # Inner highlight
    for (x, y) in [(7, 4), (6, 5), (5, 6)]:
        img.putpixel((x, y), (240, 250, 255) + (255,))
    return img

def make_spear_item(seed=0):
    """Spear: vertical shaft with spearhead."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    # Shaft (rows 6-15, brown)
    for y in range(6, 16):
        img.putpixel((8, y), PALETTE['bark_mid'] + (255,))
        img.putpixel((7, y), PALETTE['bark_lit'] + (255,))
        img.putpixel((9, y), PALETTE['bark_dark'] + (255,))
    # Spearhead (rows 1-6, bronze)
    head_shape = [
        (8, 1),         # tip
        (7, 9, 2),
        (6, 10, 3),
        (7, 9, 4),
        (8, 8, 5),
        (8, 8, 6),
    ]
    for row in head_shape:
        if len(row) == 2:
            x, y = row
            img.putpixel((x, y), PALETTE['bronze_relic_lit'] + (255,))
        else:
            x0, x1, y = row
            for x in range(x0, x1 + 1):
                if x < 8:
                    img.putpixel((x, y), PALETTE['bronze_relic_lit'] + (255,))
                else:
                    img.putpixel((x, y), PALETTE['bronze_relic_mid'] + (255,))
    # Ink outline
    for y in range(SIZE):
        for x in range(SIZE):
            if img.getpixel((x, y))[3] > 0:  # has alpha
                # Check neighbors — if any transparent neighbor, this is an edge
                neighbors = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
                is_edge = False
                for nx, ny in neighbors:
                    if 0 <= nx < SIZE and 0 <= ny < SIZE:
                        if img.getpixel((nx, ny))[3] == 0:
                            is_edge = True
                            break
                    else:
                        is_edge = True
                        break
                if is_edge:
                    img.putpixel((x, y), PALETTE['ink'] + (255,))
    return img

# ============================================================================
# UI TEXTURE GENERATORS
# ============================================================================
def make_hotbar_slot(seed=0):
    """Hotbar slot: warm bronze tint with ink border."""
    img = Image.new('RGBA', (SIZE, SIZE), PALETTE['bronze'] + (180,))
    # Slight inner gradient
    for y in range(SIZE):
        for x in range(SIZE):
            current = img.getpixel((x, y))
            n = (y - SIZE // 2) * 3
            img.putpixel((x, y), (max(0, min(255, current[0] + n)),
                                   max(0, min(255, current[1] + n // 2)),
                                   max(0, min(255, current[2] + n // 2)),
                                   180))
    # Ink border
    ink = PALETTE['ink']
    for i in range(SIZE):
        img.putpixel((i, 0), ink + (255,))
        img.putpixel((i, SIZE - 1), ink + (255,))
        img.putpixel((0, i), ink + (255,))
        img.putpixel((SIZE - 1, i), ink + (255,))
    return img

def make_title_background(seed=0):
    """Title screen background: stylized cave entrance."""
    img = Image.new('RGB', (64, 64), PALETTE['shadow'])
    rng = random.Random(seed)
    # Cave silhouette (dark arch in center)
    for y in range(64):
        for x in range(64):
            # Arch shape
            dx = abs(x - 32)
            dy = y - 16
            if dx * dx + max(0, dy) * max(0, dy) < 400 and y < 48:
                # Inside arch = lit cream
                if y < 32:
                    img.putpixel((x, y), PALETTE['lit'])
                else:
                    img.putpixel((x, y), PALETTE['light_mid'])
            elif y > 48:
                # Floor — warm sand
                img.putpixel((x, y), PALETTE['light_mid'])
            else:
                # Cave wall — brown with Holstein-style darker patches
                base = PALETTE['dark_mid']
                if rng.random() < 0.15:
                    base = PALETTE['shadow']
                img.putpixel((x, y), base)
    return img

# ============================================================================
# PACK ICON
# ============================================================================
def make_pack_icon():
    """256x256 pack icon: stylized LC GO-style scene."""
    img = Image.new('RGB', (256, 256), PALETTE['lit'])
    draw = ImageDraw.Draw(img)
    # Background gradient (warm cream top → sand bottom)
    for y in range(256):
        t = y / 256
        r = int(PALETTE['lit'][0] * (1 - t) + PALETTE['light_mid'][0] * t)
        g = int(PALETTE['lit'][1] * (1 - t) + PALETTE['light_mid'][1] * t)
        b = int(PALETTE['lit'][2] * (1 - t) + PALETTE['light_mid'][2] * t)
        for x in range(256):
            img.putpixel((x, y), (r, g, b))
    # Pyramid silhouette (LC GO tomb vibe)
    pyramid_pts = [(128, 60), (220, 220), (36, 220)]
    draw.polygon(pyramid_pts, fill=PALETTE['dark_mid'])
    # Pyramid shadow side
    shadow_pts = [(128, 60), (128, 220), (36, 220)]
    draw.polygon(shadow_pts, fill=PALETTE['shadow'])
    # Pyramid lit highlight
    lit_pts = [(128, 60), (180, 130), (128, 130)]
    draw.polygon(lit_pts, fill=PALETTE['bronze'])
    # Ink outlines
    draw.line([(128, 60), (220, 220)], fill=PALETTE['ink'], width=4)
    draw.line([(128, 60), (36, 220)], fill=PALETTE['ink'], width=4)
    draw.line([(36, 220), (220, 220)], fill=PALETTE['ink'], width=4)
    draw.line([(128, 60), (128, 220)], fill=PALETTE['ink'], width=3)
    # Sun (small circle top-right)
    draw.ellipse([(200, 30), (240, 70)], fill=PALETTE['gold_lit'],
                 outline=PALETTE['ink'], width=3)
    return img

# ============================================================================
# BLOCK DEFINITIONS — Maps vanilla block → texture files
# ============================================================================
# The 4-step cel band strategy: use 4 vanilla block types to represent
# the 4 bands. Player places different block types to achieve the banded look.
#   Band 1 (lit)       → calcite   (vanilla white block)
#   Band 2 (light_mid) → stone     (vanilla gray block)
#   Band 3 (dark_mid)  → deepslate (vanilla dark block)
#   Band 4 (shadow)    → bedrock   (vanilla black block)
# Plus: sand, dirt, oak_log, leaves, water, gold_block (relic), emerald_block, copper_block
# ============================================================================

BLOCK_TEXTURES = {
    # 4-step cel bands via 4 vanilla block types
    'calcite':   {'base': PALETTE['lit'],       'spot_count': 2, 'seed': 11},  # Band 1
    'stone':     {'base': PALETTE['light_mid'], 'spot_count': 3, 'seed': 22},  # Band 2
    'deepslate': {'base': PALETTE['dark_mid'],  'spot_count': 3, 'seed': 33},  # Band 3
    'bedrock':   {'base': PALETTE['shadow'],    'spot_count': 4, 'seed': 44},  # Band 4

    # Outdoor organics
    'sand':      {'base': PALETTE['lit'],       'spot_count': 1, 'seed': 55, 'min_r': 2, 'max_r': 3},
    'dirt':      {'base': PALETTE['dirt_mid'],  'spot_count': 3, 'seed': 66, 'spot_color': PALETTE['moss_dark']},

    # Wood (top + side)
    'oak_log_top':  {'log_top': True, 'ring_color': PALETTE['bark_lit'], 'seed': 77},
    'oak_log_side': {'log_side': True, 'bark_color': PALETTE['bark_mid'], 'ring_color': PALETTE['bark_lit'], 'seed': 88},

    # Leaves
    'leaves':    {'leaves': True, 'base': PALETTE['moss_mid'], 'lit': PALETTE['moss_lit'], 'seed': 99},

    # Water
    'water':     {'water': True, 'base': PALETTE['water_mid'], 'foam': PALETTE['water_lit'], 'seed': 110},

    # Relic blocks
    'gold_block':       {'relic': True, 'lit': PALETTE['gold_lit'], 'mid': PALETTE['gold_mid'], 'dark': PALETTE['gold_dark'], 'accent': PALETTE['bronze'], 'seed': 121},
    'emerald_block':    {'relic': True, 'lit': PALETTE['jade_lit'], 'mid': PALETTE['jade_mid'], 'dark': PALETTE['jade_dark'], 'accent': PALETTE['moss_dark'], 'seed': 132},
    'copper_block':     {'relic': True, 'lit': PALETTE['bronze_relic_lit'], 'mid': PALETTE['bronze_relic_mid'], 'dark': PALETTE['bronze_relic_dark'], 'accent': PALETTE['shadow'], 'seed': 143},
}

ITEM_TEXTURES = {
    'incan_bottle':  {'item': 'incan_bottle', 'seed': 200},
    'jade_mask':     {'item': 'jade_mask',    'seed': 201},
    'bronze_coin':   {'item': 'bronze_coin',  'seed': 202},
    'crystal_shard': {'item': 'crystal_shard','seed': 203},
    'spear':         {'item': 'spear',        'seed': 204},
}

# Vanilla block paths to override (Bedrock 1.21+)
VANILLA_BLOCK_PATHS = {
    'calcite':       'textures/blocks/calcite',
    'stone':         'textures/blocks/stone',
    'deepslate':     'textures/blocks/deepslate',
    'bedrock':       'textures/blocks/bedrock',
    'sand':          'textures/blocks/sand',
    'dirt':          'textures/blocks/dirt',
    'oak_log_top':   'textures/blocks/log_top',         # vanilla: oak top
    'oak_log_side':  'textures/blocks/log_side',        # vanilla: oak side
    'leaves':        'textures/blocks/leaves_oak',
    'water':         'textures/blocks/water_still_greyscale',
    'gold_block':    'textures/blocks/gold_block',
    'emerald_block': 'textures/blocks/emerald_block',
    'copper_block':  'textures/blocks/copper_block',
}

# Item paths (replace existing vanilla items)
VANILLA_ITEM_PATHS = {
    'incan_bottle':  'textures/items/chorus_fruit',         # vase-like shape
    'jade_mask':     'textures/items/zombie_head',          # face-like shape
    'bronze_coin':   'textures/items/iron_ingot',           # coin-like
    'crystal_shard': 'textures/items/prismarine_crystals',  # crystal-like
    'spear':         'textures/items/trident',              # spear-like
}

# ============================================================================
# VOXEL CONVERSION — LC GO level JSON → MC Bedrock blocks
# ============================================================================
# LC GO tile types → Bedrock block IDs
LCGO_TILE_TO_MC = {
    'floor_lit':    'calcite',       # Band 1: lit cream
    'floor_light':  'stone',         # Band 2: warm sand
    'floor_dark':   'deepslate',     # Band 3: warm brown
    'floor_shadow': 'bedrock',       # Band 4: deep shadow
    'wall':         'cobblestone',
    'sand':         'sand',
    'wood':         'oak_log',
    'leaves':       'leaves',
    'water':        'water',
    'gold_relic':   'gold_block',
    'jade_relic':   'emerald_block',
    'bronze_relic': 'copper_block',
}

def lcgo_level_to_blocks(level_json, origin=(0, 100, 0)):
    """
    Convert LC GO level JSON to a list of (x, y, z, block_id) tuples.
    LC GO tiles are 2D grid coordinates with optional elevation (y).
    """
    blocks = []
    base_x, base_y, base_z = origin
    for tile in level_json.get('tiles', []):
        x = base_x + tile['x']
        y = base_y + tile.get('y', 0)
        z = base_z + tile['z']
        block_type = LCGO_TILE_TO_MC.get(tile['type'], 'stone')
        # Some LC GO tile types map to multi-block features
        if tile['type'] == 'wall':
            # Wall is 2 blocks tall
            blocks.append((x, y, z, 'cobblestone'))
            blocks.append((x, y + 1, z, 'cobblestone'))
        elif tile['type'] == 'wood':
            # Wood is 3 blocks tall (log)
            blocks.append((x, y, z, 'oak_log'))
            blocks.append((x, y + 1, z, 'oak_log'))
            blocks.append((x, y + 2, z, 'oak_log'))
            # Leaves on top
            blocks.append((x, y + 3, z, 'leaves'))
        elif tile['type'] == 'leaves':
            blocks.append((x, y + 1, z, 'leaves'))
            blocks.append((x, y + 2, z, 'leaves'))
        else:
            blocks.append((x, y, z, block_type))
    return blocks

def blocks_to_setblock_commands(blocks, output_path):
    """Generate /setblock commands for Bedrock (paste into chat one at a time)."""
    with open(output_path, 'w') as f:
        f.write("# LC GO → MC Bedrock /setblock commands\n")
        f.write(f"# Total blocks: {len(blocks)}\n")
        f.write("# Run each line in-game as a slash command.\n\n")
        for x, y, z, block in blocks:
            f.write(f"setblock {x} {y} {z} {block}\n")

def blocks_to_mcfunction(blocks, output_path):
    """Generate a .mcfunction file (no leading slash)."""
    with open(output_path, 'w') as f:
        for x, y, z, block in blocks:
            f.write(f"setblock {x} {y} {z} {block}\n")

def blocks_to_python_list(blocks, output_path):
    """Generate a Python list literal (for embedding in other scripts)."""
    with open(output_path, 'w') as f:
        f.write("# Auto-generated LC GO voxel data\n")
        f.write("BLOCKS = [\n")
        for x, y, z, block in blocks:
            f.write(f"    ({x}, {y}, {z}, '{block}'),\n")
        f.write("]\n")

# ============================================================================
# PACK ASSEMBLY
# ============================================================================
def build_manifest():
    return {
        "format_version": 2,
        "header": {
            "name": "Lara Croft GO Diorama Pack",
            "description": "Sunlit outdoor LC GO aesthetic: warm stone + Holstein spots + 4-step cel + ink outlines",
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0]
        },
        "modules": [{
            "type": "resources",
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0]
        }]
    }

def generate_block_textures(output_dir):
    """Generate all block textures to output_dir/textures/blocks/."""
    blocks_dir = output_dir / 'textures' / 'blocks'
    blocks_dir.mkdir(parents=True, exist_ok=True)

    for block_name, spec in BLOCK_TEXTURES.items():
        if spec.get('log_top'):
            img = make_log_top_texture(spec['ring_color'], spec['seed'])
        elif spec.get('log_side'):
            img = make_log_side_texture(spec['bark_color'], spec['ring_color'], spec['seed'])
        elif spec.get('leaves'):
            img = make_leaves_texture(spec['base'], spec['lit'], spec['seed'])
        elif spec.get('water'):
            img = make_water_texture(spec['base'], spec['foam'], spec['seed'])
        elif spec.get('relic'):
            img = make_relic_block_texture(
                spec['lit'], spec['mid'], spec['dark'], spec['accent'], spec['seed'])
        else:
            min_r = spec.get('min_r', 2)
            max_r = spec.get('max_r', 5)
            spot_color = spec.get('spot_color')
            img = make_block_texture(
                spec['base'], spot_color=spot_color,
                spot_count=spec['spot_count'],
                min_r=min_r, max_r=max_r,
                seed=spec['seed'])

        # Save to vanilla override path
        vanilla_path = VANILLA_BLOCK_PATHS[block_name]
        out_file = output_dir / (vanilla_path + '.png')
        out_file.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_file)
        print(f"  [block] {block_name:18s} → {vanilla_path}.png")

def generate_item_textures(output_dir):
    """Generate all item textures to output_dir/textures/items/."""
    for item_name, spec in ITEM_TEXTURES.items():
        if spec['item'] == 'incan_bottle':
            img = make_incan_bottle(spec['seed'])
        elif spec['item'] == 'jade_mask':
            img = make_jade_mask(spec['seed'])
        elif spec['item'] == 'bronze_coin':
            img = make_bronze_coin(spec['seed'])
        elif spec['item'] == 'crystal_shard':
            img = make_crystal_shard(spec['seed'])
        elif spec['item'] == 'spear':
            img = make_spear_item(spec['seed'])
        else:
            continue
        vanilla_path = VANILLA_ITEM_PATHS[item_name]
        out_file = output_dir / (vanilla_path + '.png')
        out_file.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_file)
        print(f"  [item]  {item_name:18s} → {vanilla_path}.png")

def generate_ui_textures(output_dir):
    """Generate UI textures."""
    # Hotbar slot
    hotbar = make_hotbar_slot()
    out = output_dir / 'textures' / 'ui' / 'hotbar_start_cap.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    hotbar.save(out)
    print(f"  [ui]    hotbar_start_cap      → textures/ui/hotbar_start_cap.png")

    # Title background
    title = make_title_background()
    # Bedrock title screen expects specific dimensions — we provide 64x64
    out = output_dir / 'textures' / 'ui' / 'title.png'
    title.save(out)
    print(f"  [ui]    title background      → textures/ui/title.png")

def generate_pack_icon(output_dir):
    """Generate 256x256 pack_icon.png."""
    icon = make_pack_icon()
    out = output_dir / 'pack_icon.png'
    icon.save(out)
    print(f"  [icon]  pack_icon             → pack_icon.png (256x256)")

def assemble_pack(output_dir):
    """Assemble the .mcpack ZIP file."""
    # Write manifest
    manifest = build_manifest()
    with open(output_dir / 'manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  [meta]  manifest.json         → manifest.json")

    # Create .mcpack (ZIP)
    pack_zip_path = output_dir.parent / 'Lara_Croft_GO_Diorama.mcpack'
    with zipfile.ZipFile(pack_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(output_dir)
                zf.write(file_path, arcname)
    print(f"\n  [pack]  Assembled: {pack_zip_path}")
    print(f"          Size: {pack_zip_path.stat().st_size / 1024:.1f} KB")
    return pack_zip_path

# ============================================================================
# SAMPLE LEVEL
# ============================================================================
SAMPLE_LEVEL = {
    "name": "Cave of Snakes — Sample",
    "description": "Sunlit outdoor LC GO level fragment for testing voxel conversion",
    "width": 12,
    "depth": 12,
    "tiles": [
        # Front row (z=0): lit floor transitioning to shadow
        {"x": 0, "z": 0, "y": 0, "type": "floor_lit"},
        {"x": 1, "z": 0, "y": 0, "type": "floor_lit"},
        {"x": 2, "z": 0, "y": 0, "type": "floor_light"},
        {"x": 3, "z": 0, "y": 0, "type": "floor_light"},
        {"x": 4, "z": 0, "y": 0, "type": "floor_dark"},
        {"x": 5, "z": 0, "y": 0, "type": "floor_dark"},
        {"x": 6, "z": 0, "y": 0, "type": "floor_shadow"},
        {"x": 7, "z": 0, "y": 0, "type": "floor_shadow"},
        {"x": 8, "z": 0, "y": 0, "type": "wall"},
        {"x": 9, "z": 0, "y": 0, "type": "floor_shadow"},
        {"x": 10, "z": 0, "y": 0, "type": "floor_dark"},
        {"x": 11, "z": 0, "y": 0, "type": "floor_light"},

        # Middle (z=4): a tree
        {"x": 5, "z": 4, "y": 0, "type": "wood"},
        {"x": 6, "z": 4, "y": 0, "type": "leaves"},

        # Center (z=6): gold relic
        {"x": 5, "z": 6, "y": 0, "type": "floor_lit"},
        {"x": 6, "z": 6, "y": 0, "type": "gold_relic"},
        {"x": 7, "z": 6, "y": 0, "type": "floor_lit"},

        # Right side (z=8): water feature
        {"x": 8, "z": 8, "y": 0, "type": "water"},
        {"x": 9, "z": 8, "y": 0, "type": "water"},
        {"x": 10, "z": 8, "y": 0, "type": "floor_light"},
        {"x": 11, "z": 8, "y": 0, "type": "floor_light"},

        # Back row (z=11): jade relic and bronze relic
        {"x": 2, "z": 11, "y": 0, "type": "floor_dark"},
        {"x": 3, "z": 11, "y": 0, "type": "jade_relic"},
        {"x": 4, "z": 11, "y": 0, "type": "floor_dark"},
        {"x": 7, "z": 11, "y": 0, "type": "floor_dark"},
        {"x": 8, "z": 11, "y": 0, "type": "bronze_relic"},
        {"x": 9, "z": 11, "y": 0, "type": "floor_dark"},

        # Some scattered lit floor
        {"x": 2, "z": 3, "y": 0, "type": "floor_lit"},
        {"x": 3, "z": 3, "y": 0, "type": "floor_lit"},
        {"x": 4, "z": 3, "y": 0, "type": "floor_light"},
        {"x": 8, "z": 3, "y": 0, "type": "floor_lit"},
        {"x": 9, "z": 3, "y": 0, "type": "floor_light"},
        {"x": 2, "z": 7, "y": 0, "type": "floor_light"},
        {"x": 3, "z": 7, "y": 0, "type": "floor_dark"},
        {"x": 8, "z": 7, "y": 0, "type": "floor_lit"},
        {"x": 9, "z": 7, "y": 0, "type": "floor_light"},
        {"x": 2, "z": 9, "y": 0, "type": "floor_light"},
        {"x": 3, "z": 9, "y": 0, "type": "floor_dark"},
        {"x": 4, "z": 9, "y": 0, "type": "floor_shadow"},
        {"x": 8, "z": 9, "y": 0, "type": "floor_light"},
        {"x": 9, "z": 9, "y": 0, "type": "floor_dark"},

        # Elevated section (LC GO levels have height variation)
        {"x": 0, "z": 11, "y": 1, "type": "floor_lit"},
        {"x": 1, "z": 11, "y": 1, "type": "floor_lit"},
        {"x": 0, "z": 10, "y": 1, "type": "floor_lit"},
        {"x": 1, "z": 10, "y": 1, "type": "floor_lit"},
    ]
}

def write_sample_level(output_dir):
    """Write the sample level JSON for user reference."""
    out = output_dir / 'sample_level.json'
    with open(out, 'w') as f:
        json.dump(SAMPLE_LEVEL, f, indent=2)
    print(f"  [sample] sample_level.json  → {out}")
    return out

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description='LC GO MC Texture Pack Generator & Voxel Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lcgo_mc_tool.py --mode all
  python3 lcgo_mc_tool.py --mode textures --output ./out
  python3 lcgo_mc_tool.py --mode pack --output ./out
  python3 lcgo_mc_tool.py --mode convert --level sample_level.json
        """)
    parser.add_argument('--mode', choices=['textures', 'pack', 'convert', 'all'],
                        default='all',
                        help='Operation mode (default: all)')
    parser.add_argument('--level', help='LC GO level JSON file to convert')
    parser.add_argument('--origin', default='0,100,0',
                        help='World origin for voxel placement (x,y,z)')
    parser.add_argument('--output', default='./lcgo_mc_output',
                        help='Output directory (default: ./lcgo_mc_output)')
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    print(f"LC GO MC Tool — mode: {args.mode}")
    print(f"Output directory: {output}\n")

    # ─── TEXTURES ────────────────────────────────────────────
    if args.mode in ('textures', 'all'):
        print("─" * 60)
        print("Generating textures...")
        print("─" * 60)
        generate_block_textures(output)
        generate_item_textures(output)
        generate_ui_textures(output)
        generate_pack_icon(output)
        print()

    # ─── PACK ASSEMBLY ───────────────────────────────────────
    if args.mode in ('pack', 'all'):
        print("─" * 60)
        print("Assembling Bedrock pack...")
        print("─" * 60)
        pack_path = assemble_pack(output)
        print()

    # ─── VOXEL CONVERSION ────────────────────────────────────
    if args.mode in ('convert', 'all'):
        print("─" * 60)
        print("Voxel conversion...")
        print("─" * 60)

        # Write sample level if no --level provided
        level_file = args.level
        if not level_file:
            print("  No --level provided. Writing sample_level.json...")
            level_file = write_sample_level(output)
            level_data = SAMPLE_LEVEL
        else:
            print(f"  Loading level: {level_file}")
            with open(level_file) as f:
                level_data = json.load(f)

        # Parse origin
        origin = tuple(int(x) for x in args.origin.split(','))

        # Convert
        print(f"  Converting level '{level_data.get('name', '?')}'...")
        print(f"  Origin: {origin}")
        blocks = lcgo_level_to_blocks(level_data, origin=origin)
        print(f"  Generated {len(blocks)} block placements.")

        # Write outputs in multiple formats
        setblock_path = output / 'sample_level.setblock'
        blocks_to_setblock_commands(blocks, setblock_path)
        print(f"  [out] setblock commands → {setblock_path}")

        mcfunction_path = output / 'lcgo_level.mcfunction'
        blocks_to_mcfunction(blocks, mcfunction_path)
        print(f"  [out] mcfunction file   → {mcfunction_path}")

        python_path = output / 'lcgo_blocks.py'
        blocks_to_python_list(blocks, python_path)
        print(f"  [out] python list       → {python_path}")

        # Also write sample level JSON if not already
        if args.level:
            sample_out = output / 'sample_level.json'
            with open(sample_out, 'w') as f:
                json.dump(SAMPLE_LEVEL, f, indent=2)
            print(f"  [out] sample level JSON → {sample_out}")

    print()
    print("✓ Done.")

if __name__ == '__main__':
    main()
