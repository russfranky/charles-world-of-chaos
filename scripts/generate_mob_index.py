#!/usr/bin/env python3
"""Generate docs/mob-index — visual mob catalog for pre-publish approval."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
MOB_INDEX_DIR = ROOT / "docs" / "mob-index"
PREVIEWS_DIR = MOB_INDEX_DIR / "previews"
APPROVALS_FILE = MOB_INDEX_DIR / "mob-approvals.json"
INDEX_JSON = MOB_INDEX_DIR / "mob-index.json"
INDEX_MD = MOB_INDEX_DIR / "MOB_INDEX.md"
INDEX_HTML = MOB_INDEX_DIR / "index.html"

CUSTOM_RP = ROOT / "resource_packs" / "brindal_grayson_cow_rp"
PROMPTS_FILE = ROOT / "variants" / "ultimate-chaos-pack" / "prompts" / "venice_prompts.json"
SHIPPED_MOBS_FILE = ROOT / "variants" / "ultimate-chaos-pack" / "shipped_mobs.json"
VENICE_CACHE = ROOT / "variants" / "ultimate-chaos-pack" / "venice_cache"
BUILT_RP = ROOT / "variants" / "ultimate-chaos-pack" / "pack"
VANILLA_RP = ROOT / "variants" / "ultimate-chaos-pack" / "vanilla_src" / "resource_pack"


def load_shipped_mob_ids() -> frozenset[str]:
    if SHIPPED_MOBS_FILE.exists():
        data = json.loads(SHIPPED_MOBS_FILE.read_text(encoding="utf-8"))
        return frozenset(data.get("ids", []))
    return frozenset({"brindal_cow", "grayson_cow"})

CUSTOM_MOBS = (
    {
        "id": "brindal_cow",
        "name": "Brindal Cow",
        "identifier": "bgcow:brindal_cow",
        "source": "custom",
        "texture_path": "textures/entity/brindal_cow.png",
        "entity_json": CUSTOM_RP / "entity/brindal_cow.entity.json",
        "texture_file": CUSTOM_RP / "textures/entity/brindal_cow.png",
    },
    {
        "id": "grayson_cow",
        "name": "Grayson Cow",
        "identifier": "bgcow:grayson_cow",
        "source": "custom",
        "texture_path": "textures/entity/grayson_cow.png",
        "entity_json": CUSTOM_RP / "entity/grayson_cow.entity.json",
        "texture_file": CUSTOM_RP / "textures/entity/grayson_cow.png",
    },
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_approvals() -> dict:
    if not APPROVALS_FILE.exists():
        return {"version": 1, "mobs": {}}
    with open(APPROVALS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_approvals(data: dict) -> None:
    MOB_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(APPROVALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def merge_approval(approvals: dict, mob_id: str, *, shipped: bool) -> dict:
    mobs = approvals.setdefault("mobs", {})
    entry = mobs.get(mob_id, {})
    shipped_ids = load_shipped_mob_ids()
    if mob_id not in mobs:
        entry = {
            "approved": mob_id in shipped_ids,
            "shipped": shipped,
            "reviewer": "",
            "note": "Auto-added — set approved true after visual review",
        }
        mobs[mob_id] = entry
    else:
        entry["shipped"] = shipped
    return entry


def resolve_texture(mob_id: str, pack_path: str, target_size: int) -> Path | None:
    candidates = [
        BUILT_RP / pack_path,
        VENICE_CACHE / f"{mob_id}_{target_size}.png",
        CUSTOM_RP / pack_path,
        VANILLA_RP / pack_path,
    ]
    for custom in CUSTOM_MOBS:
        if custom["id"] == mob_id:
            candidates.insert(0, custom["texture_file"])
    for path in candidates:
        if path.exists():
            return path
    return None


def extract_face_preview(tex: Image.Image) -> Image.Image | None:
    """Best-effort head/face crop from a 64×64 entity UV sheet."""
    w, h = tex.size
    if w < 32 or h < 32:
        return None
    # Common Bedrock/Java entity head region on 64×64 sheets.
    crop = tex.crop((w // 4, h // 4, w // 2, h // 2))
    if crop.getbbox() is None:
        return None
    return crop


def render_preview_card(
    mob_id: str,
    name: str,
    tex: Image.Image,
    *,
    approved: bool,
    shipped: bool,
    identifier: str,
) -> Image.Image:
    scale = max(4, min(12, 192 // max(tex.size)))
    sheet = tex.resize((tex.width * scale, tex.height * scale), Image.Resampling.NEAREST)

    card_w, card_h = 280, 360
    card = Image.new("RGBA", (card_w, card_h), (32, 36, 44, 255))
    draw = ImageDraw.Draw(card)

    status = "APPROVED" if approved else "PENDING"
    status_color = (72, 160, 90) if approved else (200, 140, 50)
    if shipped and not approved:
        status = "BLOCKED"
        status_color = (200, 70, 70)

    draw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=12, outline=(80, 90, 110), width=2)
    draw.rounded_rectangle([12, 12, 120, 36], radius=8, fill=status_color)
    draw.text((66, 24), status, fill=(255, 255, 255), font=font(11, True), anchor="mm")

    if shipped:
        draw.rounded_rectangle([130, 12, 220, 36], radius=8, fill=(60, 100, 160))
        draw.text((175, 24), "IN PACK", fill=(255, 255, 255), font=font(10, True), anchor="mm")

    draw.text((card_w // 2, 52), name, fill=(240, 240, 245), font=font(16, True), anchor="mm")
    draw.text((card_w // 2, 74), identifier, fill=(160, 170, 190), font=font(10), anchor="mm")

    sw, sh = sheet.size
    px, py = (card_w - sw) // 2, 100 + (180 - sh) // 2
    card.paste(sheet, (px, py), sheet)

    face = extract_face_preview(tex)
    if face:
        face_up = face.resize((face.width * 6, face.height * 6), Image.Resampling.NEAREST)
        card.paste(face_up, (card_w - face_up.width - 16, 88), face_up)

    draw.text((card_w // 2, card_h - 28), mob_id, fill=(120, 130, 150), font=font(10), anchor="mm")
    return card


def load_entity_meta(entity_json: Path | None) -> dict:
    if not entity_json or not entity_json.exists():
        return {}
    with open(entity_json, encoding="utf-8") as f:
        data = json.load(f)
    desc = data.get("minecraft:client_entity", {}).get("description", {})
    geo = desc.get("geometry", {}).get("default", "")
    egg = desc.get("spawn_egg", {})
    return {
        "geometry": geo,
        "spawn_egg_base": egg.get("base_color"),
        "spawn_egg_overlay": egg.get("overlay_color"),
    }


def collect_mobs() -> list[dict]:
    shipped_ids = load_shipped_mob_ids()
    mobs: list[dict] = []

    for custom in CUSTOM_MOBS:
        meta = load_entity_meta(custom["entity_json"])
        mobs.append({
            "id": custom["id"],
            "name": custom["name"],
            "identifier": custom["identifier"],
            "source": custom["source"],
            "category": "entity",
            "pack_path": custom["texture_path"],
            "target_size": 64,
            "shipped": custom["id"] in shipped_ids,
            "prompt": "",
            **meta,
        })

    if PROMPTS_FILE.exists():
        manifest = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
        seen = {m["id"] for m in mobs}
        for entry in manifest.get("textures", []):
            if entry.get("category") != "entity" or entry["id"] in seen:
                continue
            mobs.append({
                "id": entry["id"],
                "name": entry["id"].replace("_", " ").title(),
                "identifier": f"minecraft:{entry['id']}" if not entry["id"].startswith("bgcow") else f"bgcow:{entry['id']}",
                "source": "venice",
                "category": "entity",
                "pack_path": entry["pack_path"],
                "target_size": entry.get("target_size", 64),
                "shipped": entry["id"] in shipped_ids,
                "prompt": entry.get("prompt", "")[:240],
                "geometry": "",
            })
            seen.add(entry["id"])

    return sorted(mobs, key=lambda m: (not m["shipped"], m["name"].lower()))
    # shipped first


def generate_previews(mobs: list[dict], approvals: dict) -> list[dict]:
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    entries = []

    for mob in mobs:
        tex_path = resolve_texture(mob["id"], mob["pack_path"], mob["target_size"])
        approval = merge_approval(approvals, mob["id"], shipped=mob["shipped"])
        preview_name = f"{mob['id']}.png"
        preview_rel = f"previews/{preview_name}"

        has_texture = tex_path is not None
        if has_texture:
            tex = Image.open(tex_path).convert("RGBA")
            card = render_preview_card(
                mob["id"],
                mob["name"],
                tex,
                approved=bool(approval.get("approved")),
                shipped=mob["shipped"],
                identifier=mob["identifier"],
            )
            card.save(PREVIEWS_DIR / preview_name)

        entries.append({
            **mob,
            "approved": bool(approval.get("approved")),
            "reviewer": approval.get("reviewer", ""),
            "note": approval.get("note", ""),
            "has_texture": has_texture,
            "texture_source": str(tex_path.relative_to(ROOT)) if tex_path else None,
            "preview": preview_rel if has_texture else None,
        })

    save_approvals(approvals)
    return entries


def write_index_json(entries: list[dict]) -> None:
    shipped_ids = sorted(load_shipped_mob_ids())
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": 1,
        "shipped_ids": shipped_ids,
        "summary": {
            "total": len(entries),
            "shipped": sum(1 for e in entries if e["shipped"]),
            "approved": sum(1 for e in entries if e["approved"]),
            "pending_ship_blockers": sum(
                1 for e in entries if e["shipped"] and not e["approved"]
            ),
        },
        "mobs": entries,
    }
    with open(INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_index_md(entries: list[dict]) -> None:
    lines = [
        "# Mob Index — Pre-publish approval",
        "",
        "Visual catalog of every mob texture in the pack. **Approve mobs in",
        "[`mob-approvals.json`](mob-approvals.json)** before publishing.**",
        "",
        "Regenerate after texture changes:",
        "",
        "```bash",
        "python3 scripts/generate_mob_index.py",
        "```",
        "",
        "Open [`index.html`](index.html) in a browser for the full gallery.",
        "",
    ]
    summary = {
        "total": len(entries),
        "shipped": sum(1 for e in entries if e["shipped"]),
        "approved": sum(1 for e in entries if e["approved"]),
    }
    lines.append(f"**{summary['shipped']} shipped** · **{summary['approved']} approved** · {summary['total']} total")
    lines.append("")

    for section, pred in [
        ("Shipped in pack", lambda e: e["shipped"]),
        ("Venice catalog (not shipped)", lambda e: not e["shipped"]),
    ]:
        group = [e for e in entries if pred(e)]
        if not group:
            continue
        lines.append(f"## {section}")
        lines.append("")
        for e in group:
            status = "✅" if e["approved"] else ("🚫" if e["shipped"] else "⏳")
            preview = f"![{e['name']}]({e['preview']})" if e.get("preview") else "_no preview_"
            lines.append(f"### {status} {e['name']} (`{e['id']}`)")
            lines.append("")
            lines.append(preview)
            lines.append("")
            lines.append(f"- **Identifier:** `{e['identifier']}`")
            lines.append(f"- **Texture:** `{e['pack_path']}`")
            if e.get("note"):
                lines.append(f"- **Note:** {e['note']}")
            lines.append("")

    INDEX_MD.write_text("\n".join(lines), encoding="utf-8")


def write_index_html(entries: list[dict]) -> None:
    cards = []
    for e in entries:
        badge = "approved" if e["approved"] else ("blocked" if e["shipped"] else "pending")
        img = f'<img src="{e["preview"]}" alt="{e["name"]}" loading="lazy">' if e.get("preview") else "<div class='missing'>No texture</div>"
        cards.append(f"""
        <article class="card {badge}" data-shipped="{'1' if e['shipped'] else '0'}">
          {img}
          <div class="meta">
            <h2>{e['name']}</h2>
            <p class="id">{e['identifier']}</p>
            <p class="tags">
              <span class="tag {badge}">{'approved' if e['approved'] else badge}</span>
              {'<span class="tag shipped">in pack</span>' if e['shipped'] else '<span class="tag catalog">catalog</span>'}
            </p>
            {f'<p class="note">{_esc(e["note"])}</p>' if e.get('note') else ''}
          </div>
        </article>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Brindal &amp; Grayson — Mob Index</title>
  <style>
    :root {{ font-family: system-ui, sans-serif; background: #1a1d24; color: #e8eaef; }}
    body {{ margin: 0; padding: 1.5rem; max-width: 1400px; margin-inline: auto; }}
    h1 {{ margin-top: 0; }}
    .toolbar {{ display: flex; gap: .5rem; flex-wrap: wrap; margin: 1rem 0 1.5rem; }}
    button {{ background: #2d3548; color: inherit; border: 1px solid #4a5568; padding: .45rem .9rem; border-radius: 8px; cursor: pointer; }}
    button.active {{ background: #4a7c59; border-color: #6aa87a; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }}
    .card {{ background: #232833; border-radius: 12px; overflow: hidden; border: 2px solid #333a48; }}
    .card.approved {{ border-color: #4a7c59; }}
    .card.blocked {{ border-color: #a44; }}
    .card img {{ width: 100%; display: block; background: #111; }}
    .missing {{ padding: 4rem 1rem; text-align: center; color: #888; }}
    .meta {{ padding: .75rem 1rem 1rem; }}
    .meta h2 {{ margin: 0 0 .25rem; font-size: 1.1rem; }}
    .id {{ margin: 0; font-size: .8rem; color: #9aa3b5; word-break: break-all; }}
    .tags {{ margin: .5rem 0 0; display: flex; gap: .35rem; flex-wrap: wrap; }}
    .tag {{ font-size: .7rem; text-transform: uppercase; letter-spacing: .04em; padding: .15rem .45rem; border-radius: 4px; background: #3a4254; }}
    .tag.approved {{ background: #2d5a3a; }}
    .tag.blocked {{ background: #6b2d2d; }}
    .tag.shipped {{ background: #2d4a6b; }}
    .tag.catalog {{ background: #4a4a2d; }}
    .note {{ font-size: .8rem; color: #b0b8c8; margin: .5rem 0 0; }}
    .help {{ background: #2a3140; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; font-size: .95rem; }}
    code {{ background: #11151c; padding: .1rem .35rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Mob Index</h1>
  <div class="help">
    Approve mobs in <code>docs/mob-index/mob-approvals.json</code>, then run
    <code>python3 scripts/validate_mob_approvals.py</code> before publishing.
    Regenerate previews: <code>python3 scripts/generate_mob_index.py</code>
  </div>
  <div class="toolbar">
    <button class="active" data-filter="all">All</button>
    <button data-filter="shipped">In pack</button>
    <button data-filter="pending">Needs approval</button>
    <button data-filter="catalog">Catalog only</button>
  </div>
  <div class="grid" id="grid">
    {''.join(cards)}
  </div>
  <script>
    const buttons = document.querySelectorAll('.toolbar button');
    const cards = document.querySelectorAll('.card');
    buttons.forEach(btn => btn.addEventListener('click', () => {{
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.filter;
      cards.forEach(c => {{
        const shipped = c.dataset.shipped === '1';
        const approved = c.classList.contains('approved');
        let show = true;
        if (f === 'shipped') show = shipped;
        else if (f === 'catalog') show = !shipped;
        else if (f === 'pending') show = shipped && !approved;
        c.style.display = show ? '' : 'none';
      }});
    }}));
  </script>
</body>
</html>"""
    INDEX_HTML.write_text(html, encoding="utf-8")


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mob index for approval")
    parser.add_argument("--init-approvals", action="store_true", help="Create mob-approvals.json only")
    args = parser.parse_args()

    MOB_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    approvals = load_approvals()
    mobs = collect_mobs()

    if args.init_approvals:
        for mob in mobs:
            merge_approval(approvals, mob["id"], shipped=mob["shipped"])
        save_approvals(approvals)
        print(f"Wrote {APPROVALS_FILE}")
        return

    entries = generate_previews(mobs, approvals)
    write_index_json(entries)
    write_index_md(entries)
    write_index_html(entries)

    s = {
        "total": len(entries),
        "with_preview": sum(1 for e in entries if e.get("preview")),
        "shipped": sum(1 for e in entries if e["shipped"]),
        "blockers": sum(1 for e in entries if e["shipped"] and not e["approved"]),
    }
    print(f"Mob index → {MOB_INDEX_DIR}/")
    print(f"  {s['with_preview']} previews · {s['shipped']} shipped · {s['blockers']} approval blockers")
    if s["blockers"]:
        print("  ⚠ Shipped mobs need approval in mob-approvals.json before publish")


if __name__ == "__main__":
    main()
