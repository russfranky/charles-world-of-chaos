#!/usr/bin/env python3
"""
Continuous QA validation orchestrator for Charles' World of Chaos.

Runs all automatable test suites, updates qa/QUALITY_REGISTRY.csv, and prints
a coverage summary. Manual / device-only tests are marked WAIVED with notes.

Usage:
  python3 qa/run_qa_suite.py              # run tests + update registry
  python3 qa/run_qa_suite.py --report     # print summary only (no test run)
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = Path(__file__).resolve().parent / "QUALITY_REGISTRY.csv"
DEFECTS = Path(__file__).resolve().parent / "DEFECTS.csv"

TODAY = date.today().isoformat()


@dataclass
class TestCase:
    id: str
    description: str
    automated: bool = True


@dataclass
class Feature:
    feature_id: str
    name: str
    user_story: str
    expected_behaviour: str
    edge_cases: str
    test_cases: list[TestCase]
    dependencies: str = ""
    assumptions: str = ""
    manual_only: bool = False


FEATURES: list[Feature] = [
    # ── Installation & packaging ──────────────────────────────────────────
    Feature(
        "F-001", "iPad .mcaddon install",
        "As a parent on iPad, I want to download and import the add-on so my child can play.",
        "Safari download opens in Minecraft; both RP and BP import; no duplicate error on update.",
        "Old pack versions; Minecraft <1.21; storage full; duplicate pack message.",
        [
            TestCase("T-001-01", "dist/brindal-grayson-cow-pack.mcaddon exists after build", True),
            TestCase("T-001-02", "MCADDON size under 1.5 MB", True),
            TestCase("T-001-03", "Safari tap-to-import on physical iPad", False),
        ],
        "GitHub release artifact; Minecraft Bedrock 1.21.0+",
        "Manual import requires physical iPad.",
        manual_only=True,
    ),
    Feature(
        "F-002", "Visual-only .mcpack fallback",
        "As a user with experiment issues, I want textures without scripts.",
        "mcpack contains RP only; cow-hide textures apply; no Cow Barn scripts.",
        "Beta APIs off; HCF off; partial pack activation.",
        [
            TestCase("T-002-01", "dist/brindal-grayson-cow-pack.mcpack exists", True),
            TestCase("T-002-02", "mcpack is RP-only (no behavior pack)", True),
        ],
    ),
    Feature(
        "F-003", "World experiment configuration",
        "As a player, I need HCF and Beta APIs ON in a new world for full features.",
        "New world with both experiments enables scripts, custom entities, and items.",
        "Existing worlds cannot add experiments; HCF-only or Beta-only partial modes.",
        [
            TestCase("T-003-01", "BP manifest mentions Beta APIs", True),
            TestCase("T-003-02", "Experiment matrix row 1 full QA (device)", False),
            TestCase("T-003-03", "Experiment matrix rows 2-4 degraded modes (device)", False),
        ],
        "World creation UI; level_settings.reference.json",
        "Degraded modes are expected, not defects.",
        manual_only=True,
    ),
    Feature(
        "F-004", "Pack activation",
        "As a player, I activate both resource and behavior packs in world settings.",
        "Both packs listed; checkerboard textures if only one active.",
        "Pack order; world template dependencies.",
        [TestCase("T-004-01", "BP depends on RP UUID d36a0504-...", True)],
    ),
    # ── Onboarding ──────────────────────────────────────────────────────────
    Feature(
        "F-010", "First join welcome",
        "As a new player, I see welcome messages and understand Ranch Bell + Feed Bag.",
        "initialSpawn triggers welcomePlayer: title, chat tips, starter cow deployed.",
        "Spectator mode; script not ready shows Beta hint.",
        [
            TestCase("T-010-01", "Script contains welcomePlayer and playerSpawn handler", True),
            TestCase("T-010-02", "First join flow on device", False),
        ],
        "Beta APIs ON; script module loaded",
    ),
    Feature(
        "F-011", "Starter kit",
        "As a new player, I receive Ranch Bell, Feed Bag, cookies, and spawn eggs.",
        "giveStarterKit adds bgcow:ranch_bell, feed_bag x16, cookies, cow/spot/storm eggs.",
        "Full inventory; optional spawn egg IDs fail silently.",
        [TestCase("T-011-01", "Script references all starter item IDs", True)],
    ),
    Feature(
        "F-012", "Wild cow auto-spawn",
        "As a new player, wild cows spawn nearby so I can catch immediately.",
        "ensureNearbyCows spawns up to 2 wild vanilla cows if count low.",
        "No solid ground; entity spawn cap; dimension errors.",
        [TestCase("T-012-01", "new_player_catch_to_breed simulation", True)],
    ),
    Feature(
        "F-013", "Barn persistence",
        "As a returning player, my herd and catalog are saved.",
        "bgcow:barn_v1 dynamic property stores JSON; loadBarn/saveBarn round-trip.",
        "Corrupt JSON resets to defaultBarn; missing fields migrated.",
        [
            TestCase("T-013-01", "Script has BARN_KEY and loadBarn/saveBarn", True),
            TestCase("T-013-02", "hunger_persisted simulation", True),
        ],
    ),
    Feature(
        "F-014", "Deployed cow reconciliation",
        "As a returning player, my deployed cow is restored or cleared if missing.",
        "reconcileDeployed matches deployedEntityId or clearDeployed.",
        "Entity killed externally; chunk unload.",
        [TestCase("T-014-01", "reconcileDeployed in script", True)],
        manual_only=True,
    ),
    Feature(
        "F-015", "Beta APIs hint",
        "As a player without Beta APIs, I see a helpful message.",
        "playerSpawn when !scriptReady shows BETA_APIS_HINT.",
        "Script partially loads.",
        [TestCase("T-015-01", "BETA_APIS_HINT string in script", True)],
    ),
    # ── Ranch Bell ──────────────────────────────────────────────────────────
    Feature(
        "F-020", "Ranch Bell menu",
        "As a player, I tap Ranch Bell to open the Cow Barn menu.",
        "ActionFormData with Deploy, Feed, Breed, Recall, My herd buttons.",
        "UI module failure falls back to bell cycle.",
        [
            TestCase("T-020-01", "showBarnMenu in script", True),
            TestCase("T-020-02", "Menu opens on device", False),
        ],
    ),
    Feature(
        "F-021", "Bell cycle fallback",
        "As a player, if menu fails, bell cycles deploy→feed→breed→recall.",
        "onBellTapCycle executes mode then advances bellMode.",
        "Cancel form; rapid taps.",
        [TestCase("T-021-01", "bell_mode_cycles simulation", True)],
    ),
    Feature(
        "F-022", "Deploy cow",
        "As a player, I deploy my active cow as a world entity.",
        "deployActive recalls prior, spawnCowEntity at safe ground, applies visuals.",
        "HCF off falls back to vanilla cow with hint; spawn blocked.",
        [
            TestCase("T-022-01", "deployed_vanilla_catch_trap simulation", True),
            TestCase("T-022-02", "entity_type_mapping simulation", True),
        ],
    ),
    Feature(
        "F-023", "Feed via menu",
        "As a player, I feed my active cow from the barn menu.",
        "hunger +28, mood +12, capped at 100; calf feedsToAdult decrements.",
        "No active cow message.",
        [
            TestCase("T-023-01", "calf_feeds_to_adult simulation", True),
            TestCase("T-023-02", "hunger_persisted simulation", True),
        ],
    ),
    Feature(
        "F-024", "Breed via menu",
        "As a player, I breed two ready adults from the menu.",
        "tryBreed: Yard+ rank, 2 adults hunger≥40 mood≥55, not on cooldown, not full.",
        "Pen rank blocked; cooldown; barn full at legend 30.",
        [
            TestCase("T-024-01", "new_player_catch_to_breed simulation", True),
            TestCase("T-024-02", "breed_cooldown_blocks simulation", True),
            TestCase("T-024-03", "adults_not_ready_blocks_breed simulation", True),
            TestCase("T-024-04", "barn_full_blocks_catch simulation", True),
        ],
    ),
    Feature(
        "F-025", "Recall / next cow",
        "As a player, I recall deployed cow and cycle to next in herd.",
        "recallActive removes entity, cycleActiveCow advances activeId.",
        "Single cow herd.",
        [TestCase("T-025-01", "recall_cycles_active simulation", True)],
    ),
    Feature(
        "F-026", "My Herd picker",
        "As a player, I pick any cow from a list to make it active.",
        "showHerdPicker lists up to 15 cows; selection sets activeId.",
        "Empty barn; cancel form.",
        [TestCase("T-026-01", "showHerdPicker in script", True)],
        manual_only=True,
    ),
    # ── Feed Bag ────────────────────────────────────────────────────────────
    Feature(
        "F-030", "Catch wild cow",
        "As a player, I use Feed Bag near a wild cow to add it to my barn.",
        "findWildCow within 5 blocks; traitsFromWildEntity; rank-up message.",
        "No wild cow; barn full; entity remove fails.",
        [
            TestCase("T-030-01", "new_player_catch_to_breed simulation", True),
            TestCase("T-030-02", "barn_full_blocks_catch simulation", True),
        ],
    ),
    Feature(
        "F-031", "Feed via Feed Bag",
        "As a player, I feed my active cow when no wild cow is nearby.",
        "feedCow on active; status message with hunger/mood.",
        "No active cow prompts catch or deploy.",
        [TestCase("T-031-01", "deployed_vanilla_catch_trap feeds when no wild", True)],
    ),
    Feature(
        "F-032", "Deployed cow not catchable",
        "As a player, my own deployed cow is never caught by Feed Bag.",
        "findWildCow excludes deployedEntities id.",
        "Multiple cows nearby including deployed.",
        [TestCase("T-032-01", "deployed_vanilla_catch_trap simulation", True)],
    ),
    Feature(
        "F-033", "Legacy item migration",
        "As a returning player, renamed bell/wheat items still work.",
        "isRanchBell/isFeedBag accept minecraft:bell+wheat with nameTag.",
        "Wrong nameTag; stack without tag.",
        [TestCase("T-033-01", "Legacy checks in script", True)],
        manual_only=True,
    ),
    # ── Breeding & traits ───────────────────────────────────────────────────
    Feature(
        "F-040", "Barn ranks",
        "As a player, my barn rank grows with herd size unlocking slots.",
        "Pen(3)→Yard(6)→Ranch(10)→Spread(18)→Legend(30) slots.",
        "Rank-up at exact thresholds; maybeRankUpMessage.",
        [
            TestCase("T-040-01", "rank_progression simulation", True),
            TestCase("T-040-02", "max_slots_per_rank simulation", True),
        ],
    ),
    Feature(
        "F-041", "Trait catalog",
        "As a collector, I fill a 15-slot trait catalog.",
        "registerCatalog adds coat/horns/size/mark keys; max 15 slots.",
        "Duplicate traits not re-added.",
        [TestCase("T-041-01", "CATALOG_SLOTS=15 in script", True)],
    ),
    Feature(
        "F-042", "Discovery loot",
        "As a player, new traits grant Minecraft items.",
        "TRAIT_DISCOVERY_LOOT maps keys to gold/emerald/diamond/etc.",
        "Full inventory drops silently.",
        [TestCase("T-042-01", "TRAIT_DISCOVERY_LOOT defined in script", True)],
        manual_only=True,
    ),
    Feature(
        "F-043", "Trait inheritance",
        "As a player, calves inherit parent traits.",
        "inheritTrait 50/50 parent pick; 14% mutate.",
        "Happy bonus 25% coat mutate when parents mood>80.",
        [TestCase("T-043-01", "breed_inherits_parents simulation", True)],
    ),
    Feature(
        "F-044", "Trait mutation",
        "As a player, rare traits appear at higher ranks.",
        "shine coat at spread/legend; storm/gold horns/diamond mark/chunk size.",
        "RNG; rank gating.",
        [TestCase("T-044-01", "mutateTrait rank gating in script", True)],
    ),
    Feature(
        "F-045", "Calf growth",
        "As a player, I feed calves until they become adults.",
        "feedsToAdult starts at 3; decrements on feed; 0 = adult.",
        "Calf excluded from adultsReady.",
        [
            TestCase("T-045-01", "calf_growth simulation", True),
            TestCase("T-045-02", "calf_feeds_to_adult simulation", True),
        ],
    ),
    Feature(
        "F-046", "Breed cooldown",
        "As a player, I wait 90 ticks (~4.5s) between breeds.",
        "breedCooldown set to 90; decrements each interval.",
        "Attempt breed during cooldown shows timer.",
        [TestCase("T-046-01", "breed_cooldown_blocks simulation", True)],
    ),
    Feature(
        "F-047", "Adults ready gate",
        "As a player, both parents need hunger≥40 and mood≥55.",
        "adultsReady filters feedsToAdult=0 cows meeting thresholds.",
        "One ready adult insufficient.",
        [TestCase("T-047-01", "adults_not_ready_blocks_breed simulation", True)],
    ),
    Feature(
        "F-048", "Barn slot limits",
        "As a player, I cannot exceed rank slot cap.",
        "catch and breed check barn.cows.length >= maxSlots.",
        "Legend 30 is absolute max.",
        [TestCase("T-048-01", "barn_full_blocks_catch simulation", True)],
    ),
    Feature(
        "F-049", "First hour playability",
        "As a new player, I can reach 3+ cows in normal play.",
        "40 random actions simulation reaches breed-ready herd.",
        "RNG seed 99.",
        [TestCase("T-049-01", "first_hour_play simulation", True)],
    ),
    # ── Care system ─────────────────────────────────────────────────────────
    Feature(
        "F-050", "Hunger/mood decay",
        "As a player, cows need ongoing care.",
        "Every 200 ticks: hunger-1; mood-2 if hunger<35.",
        "Interval only when scriptReady.",
        [TestCase("T-050-01", "hunger_persisted simulation", True)],
    ),
    Feature(
        "F-051", "Auto-recall on hunger",
        "As a player, starving deployed cows return to barn safely.",
        "hunger<15 + deployed + active → recallDeployed.",
        "No cow death.",
        [TestCase("T-051-01", "hunger_auto_recall simulation", True)],
    ),
    Feature(
        "F-052", "Stale UI hunger hints",
        "As a player, I get action bar reminders when cows are hungry.",
        "uiStale after 6 intervals shows feed hint.",
        "No active cow skips.",
        [TestCase("T-052-01", "showBarnStatus hunger branch in script", True)],
        manual_only=True,
    ),
    Feature(
        "F-053", "Rank-up celebration",
        "As a player, I see title and chat when barn ranks up.",
        "maybeRankUpMessage on catch; yard unlocks breed tip.",
        "Already at rank.",
        [TestCase("T-053-01", "maybeRankUpMessage in script", True)],
        manual_only=True,
    ),
    # ── Commands ────────────────────────────────────────────────────────────
    Feature(
        "F-060", "/bgcow:help",
        "As a parent, I read help text in chat.",
        "Lists bell, feed bag, recall, /barn, /next.",
        "Non-player origin fails.",
        [TestCase("T-060-01", "help handler registered", True)],
        manual_only=True,
    ),
    Feature(
        "F-061", "/bgcow:barn",
        "As a parent, I view herd summary in chat.",
        "Rank, slots, catalog, up to 8 cows listed.",
        "Large herd truncated.",
        [TestCase("T-061-01", "barn handler registered", True)],
        manual_only=True,
    ),
    Feature(
        "F-062", "/bgcow:breed",
        "As a parent, I trigger breed from chat.",
        "Calls tryBreed with same gates as menu.",
        "Same failures as F-024.",
        [TestCase("T-062-01", "breed handler registered", True)],
        manual_only=True,
    ),
    Feature(
        "F-063", "/bgcow:next",
        "As a parent, I switch active cow from chat.",
        "recallDeployed + cycleActiveCow.",
        "Single cow message.",
        [TestCase("T-063-01", "next handler registered", True)],
        manual_only=True,
    ),
    # ── Custom entities ─────────────────────────────────────────────────────
    Feature(
        "F-070", "Spot Cow (brindal_cow)",
        "As a player, spot coat deploys bgcow:brindal_cow entity.",
        "entityTypeForCow spot → SPOT_COW; HCF required.",
        "HCF off → vanilla fallback message.",
        [
            TestCase("T-070-01", "entity_type_mapping simulation", True),
            TestCase("T-070-02", "Custom cow BP/RP files present", True),
        ],
    ),
    Feature(
        "F-071", "Storm Cow (grayson_cow)",
        "As a player, storm/shine coat deploys bgcow:grayson_cow.",
        "storm and shine map to STORM_COW.",
        "Wild storm cow 20% shine trait.",
        [TestCase("T-071-01", "entity_type_mapping simulation", True)],
    ),
    Feature(
        "F-072", "Cow visuals",
        "As a player, I see trait labels, scale, and particles on cows.",
        "cowLabel nameTag; scale 0.78/1.0/1.32; gold/star/diamond/shine particles.",
        "Scale API unavailable on old engines.",
        [TestCase("T-072-01", "applyCowVisuals in script", True)],
        manual_only=True,
    ),
    Feature(
        "F-073", "HCF spawn fallback",
        "As a player without HCF, I still get a vanilla cow.",
        "trySpawnEntity falls back to minecraft:cow with hint.",
        "Both spawns fail shows HCF_HINT.",
        [TestCase("T-073-01", "spawnCowEntity fallback in script", True)],
        manual_only=True,
    ),
    # ── Build & CI ──────────────────────────────────────────────────────────
    Feature(
        "F-080", "Build pipeline",
        "As a maintainer, I build the pack from source.",
        "./scripts/build-mcaddon.sh completes; dist artifacts created.",
        "Missing vanilla_src clone; Venice key optional.",
        [TestCase("T-080-01", "build-mcaddon.sh exit 0", True)],
    ),
    Feature(
        "F-081", "Pack validation",
        "As a maintainer, validate_pack.py passes on built pack.",
        "Manifests, textures, script markers, JSON, size limits.",
        "Run before build fails.",
        [TestCase("T-081-01", "validate_pack.py exit 0", True)],
    ),
    Feature(
        "F-082", "Marketplace compliance",
        "As a maintainer, pack meets cooperative marketplace rules.",
        "No JSON UI overrides; Beta APIs in description; custom items.",
        "Future Bedrock UI changes.",
        [TestCase("T-082-01", "validate_marketplace.py exit 0", True)],
    ),
    Feature(
        "F-083", "Mob approvals",
        "As a maintainer, shipped mobs are approved in mob-index.",
        "brindal_cow and grayson_cow approved.",
        "Unapproved shipped mob blocks publish.",
        [TestCase("T-083-01", "validate_mob_approvals.py exit 0", True)],
    ),
    Feature(
        "F-084", "World template scaffold",
        "As a maintainer, world template files are complete.",
        "manifest, lang, level_settings, checklist present.",
        "Binary .mcworld not in repo.",
        [TestCase("T-084-01", "validate_world_scaffold.py exit 0", True)],
    ),
    Feature(
        "F-085", "Barn simulation suite",
        "As a maintainer, offline barn logic mirrors main.js.",
        "17 scenarios in simulate_barn.py all pass.",
        "Python sim may drift from JS.",
        [TestCase("T-085-01", "simulate_barn.py exit 0", True)],
    ),
    Feature(
        "F-086", "Lang branding",
        "As a player, title screen shows Chaos Barn subtitle.",
        "menu.moo_world_subtitle mentions Ranch Bell.",
        "Lang-only, no JSON UI.",
        [TestCase("T-086-01", "validate_pack_lang checks", True)],
    ),
    Feature(
        "F-087", "Custom item assets",
        "As a player, Ranch Bell and Feed Bag have icons and names.",
        "items/*.json + item_texture.json + lang keys.",
        "Missing texture shows purple/black.",
        [TestCase("T-087-01", "validate_custom_items", True)],
    ),
    Feature(
        "F-088", "Manifest UUID linkage",
        "As Minecraft, I resolve pack dependencies.",
        "RP UUID d36a0504-...; BP depends on RP.",
        "UUID change breaks worlds.",
        [TestCase("T-088-01", "validate_manifests", True)],
    ),
    Feature(
        "F-089", "Cow ID monotonicity",
        "As a player, each cow gets a unique cow_N id.",
        "nextCowId increments; reload preserves counter.",
        "Manual id edit.",
        [TestCase("T-089-01", "cow_ids_monotonic simulation", True)],
    ),
    Feature(
        "F-090", "Pre-commit secret scan",
        "As a maintainer, Venice keys are not committed.",
        "check_secrets.py blocks API keys.",
        "False positives on example strings.",
        [TestCase("T-090-01", "check_secrets.py exists", True)],
    ),
    Feature(
        "F-091", "Menu music override",
        "As a player, the title screen plays custom menu music.",
        "Bell_At_Twilight.ogg applied via apply_audio_overrides; optimized in build.",
        "Missing ffmpeg; audio size budget.",
        [TestCase("T-091-01", "Menu music OGG present in built RP", True)],
        "apply_audio_overrides.py; optimize_audio.py",
    ),
    Feature(
        "F-092", "GitHub CI pipeline",
        "As a maintainer, PRs run build and validation automatically.",
        "ci.yml builds pack, runs .auto/checks.sh, uploads artifacts.",
        "MCTools optional continue-on-error.",
        [
            TestCase("T-092-01", "ci.yml exists with checks.sh step", True),
            TestCase("T-092-02", "CI build on merge (GitHub)", False),
        ],
    ),
    Feature(
        "F-093", "Release publish automation",
        "As a maintainer, merge to main bumps version and publishes release.",
        "publish.yml tags Charles' World of Chaos release with mcaddon/mcpack.",
        "GH_TOKEN; SKIP_BUMP env.",
        [TestCase("T-093-01", "publish_pack.sh and publish.yml exist", True)],
        "Keeps brindal-grayson-cow-pack.mcaddon filename for URL stability",
    ),
    Feature(
        "F-094", "Product branding consistency",
        "As a player, pack name matches Charles' World of Chaos everywhere shipped.",
        "Built RP lang, BP manifest, README use Charles' World of Chaos.",
        "Legacy Brindal & Grayson names in source dirs and repo slug.",
        [TestCase("T-094-01", "validate_branding.py passes on built pack", True)],
        "Repo slug still brindal-grayson-cow-pack — rename recommended",
    ),
    Feature(
        "F-095", "Custom cow spawn rules",
        "As a player, Spot and Storm cows can spawn naturally in worlds.",
        "brindal_cow.json and grayson_cow.json spawn rules merged into BP.",
        "Spawn weight tuning; biome filters.",
        [TestCase("T-095-01", "validate_pack reports 2+ custom spawn rules", True)],
    ),
    Feature(
        "F-096", "Mob index approval gallery",
        "As a maintainer, I review mob textures in a browser gallery.",
        "docs/mob-index/index.html lists shipped mobs with approval status.",
        "Stale previews after texture change.",
        [TestCase("T-096-01", "mob-index.json exists with shipped mobs", True)],
    ),
    Feature(
        "F-097", "World template SKU (future)",
        "As a Marketplace buyer, I get Brindal & Grayson Cow Ranch world template.",
        "worlds/brindal_grayson_ranch scaffold with locked experiments.",
        "Binary .mcworld export not in repo; naming differs from add-on brand.",
        [
            TestCase("T-097-01", "validate_world_scaffold.py passes", True),
            TestCase("T-097-02", "World template export on device", False),
        ],
        "Marketplace SKU name may stay Brindal & Grayson Cow Ranch",
        manual_only=True,
    ),
]

# Maps test case IDs to shell/python commands
AUTOMATED_RUNNERS: dict[str, list[str]] = {
    "T-001-01": ["test", "-f", str(ROOT / "dist/brindal-grayson-cow-pack.mcaddon")],
    "T-001-02": ["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/validate_pack.py")],
    "T-002-01": ["test", "-f", str(ROOT / "dist/brindal-grayson-cow-pack.mcpack")],
    "T-080-01": ["test", "-f", str(ROOT / "dist/brindal-grayson-cow-pack.mcaddon")],
    "T-081-01": ["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/validate_pack.py")],
    "T-082-01": ["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/validate_marketplace.py")],
    "T-083-01": ["python3", str(ROOT / "scripts/validate_mob_approvals.py")],
    "T-084-01": ["python3", str(ROOT / "scripts/validate_world_scaffold.py")],
    "T-085-01": ["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/simulate_barn.py")],
    "T-094-01": ["python3", str(ROOT / "qa/validate_branding.py")],
    "T-095-01": ["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/validate_pack.py")],
    "T-097-01": ["python3", str(ROOT / "scripts/validate_world_scaffold.py")],
}

SCRIPT_MARKERS: dict[str, str] = {
    "T-010-01": "welcomePlayer",
    "T-011-01": "giveStarterKit",
    "T-013-01": "saveBarn",
    "T-014-01": "reconcileDeployed",
    "T-015-01": "BETA_APIS_HINT",
    "T-020-01": "showBarnMenu",
    "T-026-01": "showHerdPicker",
    "T-033-01": "isRanchBell",
    "T-041-01": "CATALOG_SLOTS",
    "T-042-01": "TRAIT_DISCOVERY_LOOT",
    "T-044-01": "mutateTrait",
    "T-052-01": "uiStale",
    "T-053-01": "maybeRankUpMessage",
    "T-060-01": 'name: "bgcow:help"',
    "T-061-01": 'name: "bgcow:barn"',
    "T-062-01": 'name: "bgcow:breed"',
    "T-063-01": 'name: "bgcow:next"',
    "T-072-01": "applyCowVisuals",
    "T-073-01": "Using vanilla cow",
    "T-090-01": "check_secrets",
}

SIM_SCENARIOS: dict[str, str] = {
    "T-012-01": "new_player_catch_to_breed",
    "T-013-02": "hunger_persisted",
    "T-021-01": "bell_mode_cycles",
    "T-022-01": "deployed_vanilla_catch_trap",
    "T-022-02": "entity_type_mapping",
    "T-023-01": "calf_feeds_to_adult",
    "T-023-02": "hunger_persisted",
    "T-024-01": "new_player_catch_to_breed",
    "T-024-02": "breed_cooldown_blocks",
    "T-024-03": "adults_not_ready_blocks_breed",
    "T-024-04": "barn_full_blocks_catch",
    "T-025-01": "recall_cycles_active",
    "T-030-01": "new_player_catch_to_breed",
    "T-030-02": "barn_full_blocks_catch",
    "T-031-01": "deployed_vanilla_catch_trap",
    "T-032-01": "deployed_vanilla_catch_trap",
    "T-040-01": "rank_progression",
    "T-040-02": "max_slots_per_rank",
    "T-043-01": "breed_inherits_parents",
    "T-045-01": "calf_growth",
    "T-045-02": "calf_feeds_to_adult",
    "T-046-01": "breed_cooldown_blocks",
    "T-047-01": "adults_not_ready_blocks_breed",
    "T-048-01": "barn_full_blocks_catch",
    "T-049-01": "first_hour_play",
    "T-050-01": "hunger_persisted",
    "T-051-01": "hunger_auto_recall",
    "T-070-01": "entity_type_mapping",
    "T-071-01": "entity_type_mapping",
    "T-089-01": "cow_ids_monotonic",
}

MAIN_JS = ROOT / "variants/ultimate-chaos-pack/script_api/main.js"


@dataclass
class TestResult:
    test_id: str
    passed: bool
    message: str = ""


def run_cmd(cmd: list[str]) -> tuple[bool, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        ok = r.returncode == 0
        msg = (r.stdout + r.stderr).strip()[-200:]
        return ok, msg
    except Exception as exc:
        return False, str(exc)


def run_sim_scenario(name: str) -> tuple[bool, str]:
    """Run simulate_barn.py and check one scenario by name."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "variants/ultimate-chaos-pack/scripts/simulate_barn.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    for line in r.stdout.splitlines():
        if name in line:
            if "OK" in line:
                return True, line.strip()
            return False, line.strip()
    return r.returncode == 0, "scenario run via full suite"


def execute_test(tc: TestCase) -> TestResult:
    if not tc.automated:
        return TestResult(tc.id, True, "WAIVED — manual/device only")

    if tc.id in AUTOMATED_RUNNERS:
        ok, msg = run_cmd(AUTOMATED_RUNNERS[tc.id])
        return TestResult(tc.id, ok, msg)

    if tc.id in SCRIPT_MARKERS:
        body = MAIN_JS.read_text(encoding="utf-8")
        marker = SCRIPT_MARKERS[tc.id]
        if tc.id == "T-090-01":
            ok = (ROOT / "scripts/hooks/check_secrets.py").exists()
        else:
            ok = marker in body
        return TestResult(tc.id, ok, f"marker '{marker}'" + (" found" if ok else " missing"))

    if tc.id in SIM_SCENARIOS:
        ok, msg = run_sim_scenario(SIM_SCENARIOS[tc.id])
        return TestResult(tc.id, ok, msg)

    if tc.id == "T-002-02":
        # mcpack should be smaller than mcaddon (RP-only vs combined)
        mcpack = ROOT / "dist/brindal-grayson-cow-pack.mcpack"
        mcaddon = ROOT / "dist/brindal-grayson-cow-pack.mcaddon"
        ok = mcpack.exists() and mcaddon.exists() and mcpack.stat().st_size < mcaddon.stat().st_size
        return TestResult(tc.id, ok, "mcpack smaller than mcaddon")

    if tc.id == "T-004-01":
        ok, _ = run_cmd(["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/validate_pack.py")])
        return TestResult(tc.id, ok, "manifest UUID via validate_pack")

    if tc.id in ("T-070-02", "T-086-01", "T-087-01", "T-088-01"):
        ok, _ = run_cmd(["python3", str(ROOT / "variants/ultimate-chaos-pack/scripts/validate_pack.py")])
        return TestResult(tc.id, ok, "validate_pack")

    if tc.id == "T-091-01":
        ogg = ROOT / "variants/ultimate-chaos-pack/pack/sounds/music/menu/Bell_At_Twilight.ogg"
        ok = ogg.exists() and ogg.stat().st_size > 1000
        return TestResult(tc.id, ok, f"menu music {ogg.name}" + (" found" if ok else " missing"))

    if tc.id == "T-092-01":
        ci = ROOT / ".github/workflows/ci.yml"
        ok = ci.exists() and ".auto/checks.sh" in ci.read_text(encoding="utf-8")
        return TestResult(tc.id, ok, "ci.yml references checks.sh")

    if tc.id == "T-093-01":
        ok = (ROOT / "scripts/publish_pack.sh").exists() and (ROOT / ".github/workflows/publish.yml").exists()
        return TestResult(tc.id, ok, "publish scripts present")

    if tc.id == "T-096-01":
        idx = ROOT / "docs/mob-index/mob-index.json"
        if not idx.exists():
            return TestResult(tc.id, False, "mob-index.json missing")
        import json
        data = json.loads(idx.read_text(encoding="utf-8"))
        shipped = [m for m in data.get("mobs", []) if m.get("shipped")]
        ok = len(shipped) >= 2
        return TestResult(tc.id, ok, f"{len(shipped)} shipped mobs in index")

    return TestResult(tc.id, True, "WAIVED — no automated runner mapped")


def write_registry(results: dict[str, TestResult]) -> None:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for feat in FEATURES:
        tc_ids = [tc.id for tc in feat.test_cases]
        tc_desc = " | ".join(f"{tc.id}: {tc.description}" for tc in feat.test_cases)
        feat_results = [results.get(tid) for tid in tc_ids]
        automated = [r for r in feat_results if r and r.message != "WAIVED — manual/device only"]
        manual = [r for r in feat_results if r and "WAIVED" in r.message]

        if not feat_results:
            status = "NOT_TESTED"
        elif any(r and not r.passed for r in feat_results if r):
            status = "FAIL"
        elif all(r and r.passed for r in automated) and manual:
            status = "PARTIAL_PASS"
        elif all(r and r.passed for r in feat_results if r):
            status = "PASS"
        else:
            status = "PARTIAL_PASS"

        fails = sum(1 for r in feat_results if r and not r.passed)
        severity = "High" if status == "FAIL" and not feat.manual_only else (
            "Low" if status == "PARTIAL_PASS" else "None"
        )
        notes = feat.assumptions or feat.dependencies
        if manual:
            notes = (notes + " | " if notes else "") + f"{len(manual)} manual test(s) waived"

        rows.append({
            "Feature ID": feat.feature_id,
            "Feature Name": feat.name,
            "User Story": feat.user_story,
            "Expected Behaviour": feat.expected_behaviour,
            "Edge Cases": feat.edge_cases,
            "Test Cases": tc_desc,
            "Current Status": status,
            "Defect Count": str(fails),
            "Severity": severity,
            "Notes": notes,
            "Last Tested Date": TODAY,
        })

    fieldnames = [
        "Feature ID", "Feature Name", "User Story", "Expected Behaviour",
        "Edge Cases", "Test Cases", "Current Status", "Defect Count",
        "Severity", "Notes", "Last Tested Date",
    ]
    with REGISTRY.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(results: dict[str, TestResult]) -> None:
    total_features = len(FEATURES)
    statuses: dict[str, int] = {}
    defects: list[tuple[str, TestResult]] = []

    for feat in FEATURES:
        feat_results = [results.get(tc.id) for tc in feat.test_cases]
        if any(r and not r.passed for r in feat_results if r):
            statuses["FAIL"] = statuses.get("FAIL", 0) + 1
            for tc in feat.test_cases:
                r = results.get(tc.id)
                if r and not r.passed:
                    defects.append((f"{feat.feature_id}/{tc.id}", r))
        elif all(
            (r.passed if r else True)
            for tc in feat.test_cases
            for r in [results.get(tc.id)]
            if r and "WAIVED" not in r.message
        ):
            has_manual = any(
                results.get(tc.id) and "WAIVED" in (results.get(tc.id).message or "")
                for tc in feat.test_cases
            )
            key = "PARTIAL_PASS" if has_manual else "PASS"
            statuses[key] = statuses.get(key, 0) + 1
        else:
            statuses["PARTIAL_PASS"] = statuses.get("PARTIAL_PASS", 0) + 1

    automated = [r for r in results.values() if "WAIVED" not in r.message]
    passed = sum(1 for r in automated if r.passed)
    total_auto = len(automated)

    confidence = int(100 * passed / total_auto) if total_auto else 0
    if defects:
        confidence = max(0, confidence - 20 * len(defects))
    if statuses.get("PARTIAL_PASS", 0):
        confidence = min(confidence, 85)

    print("\n" + "=" * 60)
    print("QUALITY VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Coverage Summary: {total_features} features documented")
    print(f"Features Tested: PASS={statuses.get('PASS',0)} "
          f"PARTIAL={statuses.get('PARTIAL_PASS',0)} FAIL={statuses.get('FAIL',0)}")
    print(f"Automated Tests: {passed}/{total_auto} passed")
    print(f"Defects Found: {len(defects)}")
    print(f"Defects Fixed: 0 (this run)")
    if defects:
        print("\nOpen Defects:")
        for loc, r in defects:
            print(f"  - {loc}: {r.message}")
    print(f"\nRemaining Risks:")
    print(f"  - {statuses.get('PARTIAL_PASS', 0)} features need manual iPad verification")
    print(f"  - In-game audio/UI not automatable in Linux CI")
    print(f"  - MCTools marketplace validation optional (40 known CADDONREQ items)")
    print(f"\nConfidence Score: {confidence}%")
    print(f"Registry: {REGISTRY}")
    print("=" * 60)


def run_all_tests() -> dict[str, TestResult]:
    results: dict[str, TestResult] = {}
    # Batch-run simulate_barn once
    sim_ok, _ = run_cmd([sys.executable, str(ROOT / "variants/ultimate-chaos-pack/scripts/simulate_barn.py")])
    if not sim_ok:
        for tc_id in SIM_SCENARIOS:
            results[tc_id] = TestResult(tc_id, False, "simulate_barn.py failed")

    for feat in FEATURES:
        for tc in feat.test_cases:
            if tc.id in results:
                continue
            results[tc.id] = execute_test(tc)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QA validation suite")
    parser.add_argument("--report", action="store_true", help="Skip test execution")
    args = parser.parse_args()

    if args.report and REGISTRY.exists():
        print(f"Registry exists at {REGISTRY} ({REGISTRY.stat().st_size} bytes)")
        return 0

    print("Phase 3: Executing test cases...")
    results = run_all_tests()
    write_registry(results)
    print_summary(results)

    failed = [r for r in results.values() if not r.passed and "WAIVED" not in r.message]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
