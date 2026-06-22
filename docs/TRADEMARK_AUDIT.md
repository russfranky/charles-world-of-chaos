# Trademark & Franchise Term Audit

This document inventories every franchise/trademark reference in the deliverables and provides redaction recommendations for public distribution.

## Summary

| Term | Count in spec PDF | Risk level | Recommendation |
|---|---|---|---|
| "Lara Croft" / "Lara Croft GO" | 6 mentions (pages 1, 3, 13) | HIGH — registered trademark of Square Enix | Redact for any public release |
| "LC GO" | 52 mentions (every page) | MEDIUM — implies the franchise but is generic shorthand | Replace with generic term |
| "Tomb Raider" | 0 mentions in spec PDF | N/A | Already absent |
| "Square Enix" / "Square Enix Montréal" | 0 mentions in spec PDF | N/A | Already absent |
| Real person names (Doizon, Zgeb, Routon, Lutz) | 4 mentions (pages 3, 9, 20) | LOW — attributions, not trademarks | Optional redaction |
| "Cave of Snakes" | 3 mentions (pages 3, 11, 17) | LOW — in-game level name | Replace with generic name |
| "Hitman GO", "Deus Ex" | 0 mentions in spec PDF | N/A | Already absent |

## Files Audited

- `/home/z/my-project/download/Lara_Croft_GO_MC_Voxel_Spec.pdf` (20 pages, 34,374 chars)
- `/home/z/my-project/download/Lara_Croft_GO_Diorama.mcpack` (manifest.json: pack name "Lara Croft GO Diorama Pack")
- `/home/z/my-project/download/lcgo_mc_tool.py` (source: PALETTE comments, variable names)

## Detailed Findings

### 1. "Lara Croft" / "Lara Croft GO" — 6 mentions

**Locations in spec PDF:**
- Page 1 (cover): Title "Lara Croft GO Diorama Style for Minecraft"
- Page 1 (cover): Subtitle mentions "LC GO sunlit outdoor aesthetic"
- Page 3 (executive summary): "ports the Lara Croft GO diorama visual style into Minecraft"
- Page 3 (executive summary): References to LC GO levels and design
- Page 13 (gaps): "matches LC GO Lara's teal-tank + brown-shorts outfit"
- Page 20 (gaps): Reference to "Bronson Zgeb's articles describe for the LC GO DLC's URP variant"

**In .mcpack manifest.json:**
```json
"name": "Lara Croft GO Diorama Pack",
"description": "Sunlit outdoor LC GO aesthetic: warm stone + Holstein spots..."
```

**Risk:** "Lara Croft" and "Lara Croft GO" are registered trademarks of Square Enix. Using them in a publicly distributed texture pack, even for free, could trigger takedown notices. The pack's visual style is "inspired by" LC GO but does not reproduce any LC GO assets — it generates original textures procedurally.

**Recommendation:** Replace with a generic name. Suggested replacements:
- "Lara Croft GO Diorama Pack" → **"Sunlit Diorama Pack"** or **"Cel Band Diorama Pack"**
- "Lara Croft GO Diorama Style for Minecraft" → **"Sunlit Diorama Style for Minecraft"**
- "the Lara Croft GO diorama visual style" → **"the sunlit diorama visual style"**
- "LC GO Lara's teal-tank + brown-shorts outfit" → **"a teal-tank + brown-shorts explorer outfit"**

### 2. "LC GO" — 52 mentions

**Locations:** Throughout the spec PDF (every page). Used as shorthand for "Lara Croft GO".

**Risk:** "LC GO" is not itself a registered trademark, but in context it clearly refers to Lara Croft GO. A trademark examiner or Square Enix representative would recognize the reference.

**Recommendation:** Replace with a generic term throughout. Suggested:
- "LC GO" → **"the diorama style"** or **"the source aesthetic"** or just **"the source"**
- Example: "The LC GO banded lighting uses..." → **"The diorama style's banded lighting uses..."**

This requires a global find-replace across the spec PDF source (`scripts/lcgo_mc_spec_pdf.py`).

### 3. Real Person Names — 4 mentions

**Locations in spec PDF:**
- Page 3: "Daniel Lutz's 'cool 2015 low-poly' mandate from the Pocket Gamer interview"
- Page 3: "Thierry Doizon's graphic-illustration style"
- Page 9: "Routon's Pocket Gamer statement"
- Page 20: "Bronson Zgeb's articles describe for the LC GO DLC's URP variant"

**Risk:** Low. These are factual attributions to public figures who gave public interviews. Attributing a quote to its source is generally protected. However, if you want to be maximally cautious for commercial distribution, these can be genericized.

**Recommendation:** Optional. If redacting:
- "Daniel Lutz's mandate" → **"the game director's mandate"**
- "Thierry Doizon's style" → **"the art director's style"**
- "Routon's statement" → **"the lead engineer's statement"**
- "Bronson Zgeb's articles" → **"a developer's articles"** or **"the DLC developer's articles"**

### 4. "Cave of Snakes" — 3 mentions

**Locations:**
- Page 3: "Cave of Snakes, Maze of Snakes"
- Page 11: "called 'Cave of Snakes — Sample'"
- Page 17: references to the sample level

**Risk:** Low. "Cave of Snakes" is an in-game level name from LC GO. Level names are typically not trademarked individually, but they are clearly franchise-specific.

**Recommendation:** Replace the sample level name. Suggested:
- "Cave of Snakes — Sample" → **"Sunlit Ruins — Sample"** or **"Diorama Sample Level"**

This requires updating `SAMPLE_LEVEL` in `lcgo_mc_tool.py` and regenerating.

### 5. .mcpack Internal Naming

**Risk:** The .mcpack manifest contains the name "Lara Croft GO Diorama Pack" which will appear in Bedrock's resource pack list. This is the most visible trademark use.

**Recommendation:** Update the `build_manifest()` function in `lcgo_mc_tool.py`:

```python
# Current (trademarked):
"name": "Lara Croft GO Diorama Pack",
"description": "Sunlit outdoor LC GO aesthetic: warm stone + Holstein spots + 4-step cel + ink outlines",

# Suggested (genericized):
"name": "Sunlit Diorama Pack",
"description": "Sunlit outdoor diorama aesthetic: warm stone + Holstein spots + 4-step cel + ink outlines",
```

## Files That Need Updates for Public Release

If you intend to distribute this pack publicly (especially on CurseForge, Planet Minecraft, or the Minecraft Marketplace), update these files:

1. **`scripts/lcgo_mc_tool.py`** — Update `build_manifest()` function (pack name and description), update `SAMPLE_LEVEL` dict (sample level name), update docstring at top of file.

2. **`scripts/lcgo_mc_spec_pdf.py`** — Global find-replace of all trademark terms throughout the source. Regenerate the spec PDF.

3. **`download/WORKFLOW.md`** — Already uses generic terminology; no changes needed.

4. **`download/Lara_Croft_GO_Diorama.mcpack`** — Rename the file itself to something generic (e.g., `Sunlit_Diorama_Pack.mcpack`). Regenerate after updating the tool.

5. **`download/Lara_Croft_GO_MC_Voxel_Spec.pdf`** — Rename the file itself (e.g., `Sunlit_Diorama_MC_Voxel_Spec.pdf`). Regenerate after updating the spec script.

## Minecraft Marketplace Considerations

If you intend to publish on the Minecraft Marketplace (Bedrock's official store):

1. **Trademark policy:** Marketplace submissions are reviewed by Mojang. Any use of third-party trademarks (including "Lara Croft", "Tomb Raider", etc.) will be rejected. The pack name, description, and all internal content must be original.

2. **Asset originality:** All textures must be original work. This pack's procedurally-generated textures are original (no LC GO assets are reproduced), but the visual style is clearly derivative. Marketplace review may still reject it for being "too similar" to a known franchise.

3. **Naming:** The pack name cannot reference any franchise. "Sunlit Diorama Pack" or "Cel Band Diorama Pack" would pass review; "Lara Croft GO Diorama Pack" would not.

4. **Description:** Cannot mention LC GO, Tomb Raider, or any Square Enix franchise. The description should focus on the visual technique: "warm stone with Holstein spots, 4-step cel-shaded bands, and ink outlines."

5. **Pricing:** Marketplace packs can be free or paid (using Minecoins). Free is recommended for a fan-style pack.

## Recommendation Summary

For **personal use or private sharing**: no changes needed. The current naming is fine.

For **public free distribution** (CurseForge, Planet Minecraft, GitHub): apply the redactions in sections 1, 2, 4, and 5 above. Estimated effort: 30 minutes of find-replace + regeneration.

For **Minecraft Marketplace submission**: apply all redactions (sections 1-5) AND consult Mojang's creator guidelines before submission. The pack may still be rejected for visual similarity to LC GO even after redactions.

## Audit Date

2026-06-22

## Verification Method

```bash
python3 << 'EOF'
import pypdf
r = pypdf.PdfReader('Lara_Croft_GO_MC_Voxel_Spec.pdf')
full_text = ""
for page in r.pages:
    full_text += page.extract_text() + "\n"

terms = ['Lara Croft', 'Lara Croft GO', 'LC GO', 'Tomb Raider',
         'Square Enix', 'Thierry Doizon', 'Bronson Zgeb',
         'Antoine Routon', 'Daniel Lutz', 'Cave of Snakes',
         'Hitman GO', 'Deus Ex']
for term in terms:
    count = full_text.count(term)
    if count > 0:
        print(f"{term}: {count} mentions")
EOF
```
