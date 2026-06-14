# Master Prompts

Prompts used to build and maintain the Brindal & Grayson Ultimate Cow Pack.

## Initial Project Prompt

> Build an aggressively cow-themed Bedrock resource + behavior pack for my daughter Brindal and son Grayson on iPad. Everything should look, sound, and (via behavior pack) become cows.

## Build Pipeline Prompt

> Create a Python build pipeline that:
> 1. Clones Mojang bedrock-samples (sparse: resource_pack + behavior_pack)
> 2. Cowifies all textures with tiled cow-hide patterns
> 3. Overrides all mob client entities to use geometry.cow.v2
> 4. Redirects all mob sounds to cow moos
> 5. Adds BP transform-on-spawn for all non-cow entities
> 6. Zeros spawn rules for non-cows
> 7. Replaces entity loot tables with cow loot
> 8. Personalizes for Brindal & Grayson (pack name, icon, painting, B/G blocks)
> 9. Packages .mcaddon (full) and .mcpack (visual-only)
> 10. Validates structure with automated checks

## CI Prompt

> GitHub Actions workflow: install requirements, clone bedrock-samples sparse, run full build, validate_pack.py, upload dist artifacts.

## Resource Pack UUID

```
d36a0504-4533-4271-b115-a49c53b7bc97
```

## Namespace

- Behavior transform group: `bgcow:transform_to_cow`
- Custom identifiers use `bgcow:` prefix if needed

## Testing Prompt

> Document what Linux CI can vs can't test. iPad install path: Safari → download .mcaddon → Open in Minecraft → new world + Holiday Creator Features + Beta APIs + both packs.
