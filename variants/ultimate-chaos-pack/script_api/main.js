/**
 * Cow Barn — breed, care, and collect unique cows (Script API).
 */
import {
  world,
  system,
  CustomCommandStatus,
  CommandPermissionLevel,
  ItemStack,
} from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const COW = "minecraft:cow";
const SPOT_COW = "bgcow:brindal_cow";
const STORM_COW = "bgcow:grayson_cow";
const ZOMBIE_CHICKEN = "bgcow:zombie_chicken";
const CHAOS_CHICKEN = "bgcow:chaos_chicken";
const CHAOS_CHICKENS = new Set([ZOMBIE_CHICKEN, CHAOS_CHICKEN]);
const CATCHABLE_COWS = new Set([COW, SPOT_COW, STORM_COW]);
const CATALOG_SLOTS = 15; // coats(5) + horns(3) + sizes(3) + marks(4)

const BARN_KEY = "bgcow:barn_v1";
const RANCH_BELL_ID = "bgcow:ranch_bell";
const FEED_BAG_ID = "bgcow:feed_bag";

const BELL_MODES = ["deploy", "feed", "breed", "recall"];
const COATS = ["brown", "gray", "spot", "storm", "shine"];
const HORNS = ["none", "short", "gold"];
const SIZES = ["small", "normal", "chunk"];
const MARKS = ["none", "star", "diamond"];

const COAT_LABELS = {
  brown: "Brown",
  gray: "Gray",
  spot: "Chaos Cow",
  storm: "Wild Cow",
  shine: "Shine Cow",
};

const RANKS = [
  { id: "pen", slots: 3, label: "Pen", minCows: 0 },
  { id: "yard", slots: 6, label: "Yard", minCows: 3 },
  { id: "ranch", slots: 10, label: "Ranch", minCows: 6 },
  { id: "spread", slots: 18, label: "Spread", minCows: 10 },
  { id: "legend", slots: 30, label: "Legend", minCows: 18 },
];

const TRAIT_DISCOVERY_LOOT = {
  coat_storm: () => new ItemStack("minecraft:gold_ingot", 4),
  coat_shine: () => new ItemStack("minecraft:diamond", 2),
  horns_gold: () => new ItemStack("minecraft:emerald", 4),
  mark_star: () => new ItemStack("minecraft:iron_ingot", 16),
  mark_diamond: () => new ItemStack("minecraft:diamond_block", 1),
  size_chunk: () => new ItemStack("minecraft:golden_apple", 1),
};

const BETA_APIS_HINT =
  "Turn on Beta APIs in a NEW world. Ask a grown-up for help!";
const HCF_HINT =
  "Turn on Holiday Creator Features in a NEW world.";
const CHAOS_PREFIX = "§d[Chaos] §f";

// Kid tutorial: one instruction at a time (action bar only after welcome).
const TUTORIAL_DONE = 9;

const deployedEntities = new Map();
const lastUiTick = new Map();
let scriptReady = false;
let commandsReady = false;
let simTick = 0;

// ─── Helpers ───────────────────────────────────────────────────────────────

function getPlayer(origin) {
  return origin?.sourceEntity ?? origin?.initiator ?? null;
}

function playerDim(player) {
  return player?.dimension ?? world.getDimension("overworld");
}

function near(player, offset = { x: 0, y: 0, z: 0 }) {
  const l = player.location;
  return { x: l.x + offset.x, y: l.y + offset.y, z: l.z + offset.z };
}

/** Stand on solid ground with headroom — avoids spawning cows inside blocks. */
function safeSpawnNear(player, dx, dz) {
  const dim = playerDim(player);
  const base = player.location;
  const x = Math.floor(base.x) + dx + 0.5;
  const z = Math.floor(base.z) + dz + 0.5;
  let y = Math.floor(base.y);
  try {
    for (let attempt = 0; attempt < 8; attempt++) {
      const below = dim.getBlock({ x: Math.floor(x), y: y - 1, z: Math.floor(z) });
      const feet = dim.getBlock({ x: Math.floor(x), y, z: Math.floor(z) });
      const head = dim.getBlock({ x: Math.floor(x), y: y + 1, z: Math.floor(z) });
      if (below?.isSolid && feet?.isAir && head?.isAir) {
        return { x, y: y + 0.05, z };
      }
      y += 1;
    }
  } catch (_) {
    /* ignore */
  }
  return { x: base.x + dx, y: base.y + 1, z: base.z + dz };
}

function trySpawnEntity(dim, typeId, loc) {
  try {
    return dim.spawnEntity(typeId, loc);
  } catch (_) {
    return null;
  }
}

function countNearbyCows(player, maxDistance = 16) {
  let n = 0;
  try {
    for (const entity of playerDim(player).getEntities({
      location: player.location,
      maxDistance,
    })) {
      if (CATCHABLE_COWS.has(entity.typeId)) n += 1;
    }
  } catch (_) {
    /* ignore */
  }
  return n;
}

/** Cows the player can catch with Feed Bag (excludes deployed barn cow). */
function countWildCows(player, maxDistance = 16) {
  const deployedId = deployedEntities.get(player.id);
  let n = 0;
  try {
    for (const entity of playerDim(player).getEntities({
      location: player.location,
      maxDistance,
    })) {
      if (!CATCHABLE_COWS.has(entity.typeId)) continue;
      if (deployedId && entity.id === deployedId) continue;
      n += 1;
    }
  } catch (_) {
    /* ignore */
  }
  return n;
}

function say(player, msg) {
  try {
    player.sendMessage(`${CHAOS_PREFIX}${msg}`);
  } catch (_) {
    /* spectator */
  }
}

function title(player, msg) {
  try {
    player.onScreenDisplay.setActionBar(`§d🐔 ${msg}`);
  } catch (_) {
    say(player, msg);
  }
}

function touchUi(player) {
  lastUiTick.set(player.id, simTick);
}

function mooSound(player) {
  try {
    player.playSound("mob.cow.say", { volume: 1.0, pitch: 0.85 + Math.random() * 0.3 });
  } catch (_) {}
}

function cluckSound(player) {
  try {
    player.playSound("mob.chicken.say", { volume: 1.0, pitch: 0.7 + Math.random() * 0.5 });
  } catch (_) {}
}

function cowParticles(player) {
  try {
    const l = player.location;
    player.runCommandAsync(
      `particle minecraft:villager_happy ${l.x} ${l.y + 1} ${l.z}`
    );
  } catch (_) {}
}

function ok(msg) {
  return { status: CustomCommandStatus.Success, message: msg };
}

function fail(msg) {
  return { status: CustomCommandStatus.Failure, message: msg };
}

function runFor(origin, fn) {
  const player = getPlayer(origin);
  if (!player) return fail("You need to be a player!");
  system.run(() => fn(player));
  return ok("Moo!");
}

function randomOf(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function traitKey(slot, value) {
  return `${slot}_${value}`;
}

function isRanchBell(stack) {
  if (!stack) return false;
  if (stack.typeId === RANCH_BELL_ID) return true;
  // Legacy worlds: renamed vanilla bell before custom item migration
  return stack.typeId === "minecraft:bell" && (stack.nameTag ?? "").includes("Ranch Bell");
}

function isFeedBag(stack) {
  if (!stack) return false;
  if (stack.typeId === FEED_BAG_ID) return true;
  return stack.typeId === "minecraft:wheat" && (stack.nameTag ?? "").includes("Feed Bag");
}

function barnRank(barn) {
  const n = barn.cows.length;
  for (let i = RANKS.length - 1; i >= 0; i -= 1) {
    if (n >= RANKS[i].minCows) return RANKS[i];
  }
  return RANKS[0];
}

function maxSlots(barn) {
  return barnRank(barn).slots;
}

function canBreed(barn) {
  return barn.cows.length >= 3 && barnRank(barn).id !== "pen";
}

function cowsToNextRank(barn) {
  const rank = barnRank(barn);
  const idx = RANKS.findIndex((r) => r.id === rank.id);
  if (idx < 0 || idx >= RANKS.length - 1) return 0;
  return Math.max(0, RANKS[idx + 1].minCows - barn.cows.length);
}

function nextCowId(barn) {
  if (typeof barn.nextCowId !== "number" || barn.nextCowId < 1) {
    let max = 0;
    for (const c of barn.cows) {
      const m = /^cow_(\d+)$/.exec(c.id);
      if (m) max = Math.max(max, parseInt(m[1], 10));
    }
    barn.nextCowId = max + 1;
  }
  const id = `cow_${barn.nextCowId}`;
  barn.nextCowId += 1;
  return id;
}

function breedCooldownLabel(ticks) {
  const sec = Math.max(1, Math.ceil(ticks / 20));
  return `${sec}s`;
}

function hornPrefix(horns) {
  if (horns === "gold") return "§6⌇ ";
  if (horns === "short") return "§7⌇ ";
  return "";
}

function markSuffix(mark) {
  if (mark === "star") return " §e★";
  if (mark === "diamond") return " §b◆";
  return "";
}

function randomGen0Traits() {
  return {
    coat: randomOf(["brown", "gray", "spot"]),
    horns: randomOf(["none", "short"]),
    size: randomOf(["small", "normal"]),
    mark: randomOf(["none", "none", "star"]),
    gen: 0,
    feedsToAdult: 0,
    hunger: 85,
    mood: 80,
  };
}

/** First barn cow — always vanilla-deployable (no HCF required). */
function starterTraits() {
  return {
    coat: randomOf(["brown", "gray"]),
    horns: randomOf(["none", "short"]),
    size: "normal",
    mark: "none",
    gen: 0,
    feedsToAdult: 0,
    hunger: 85,
    mood: 80,
  };
}

function defaultBarn() {
  const barn = {
    cows: [],
    activeId: null,
    catalog: [],
    bellMode: 0,
    breedCooldown: 0,
    nextCowId: 1,
    deployedCowId: null,
    deployedEntityId: null,
    tutorialStep: 0,
  };
  const starter = { id: nextCowId(barn), ...starterTraits() };
  barn.cows.push(starter);
  barn.activeId = starter.id;
  registerCatalog(barn, starter);
  return barn;
}

function loadBarn(player) {
  try {
    const raw = player.getDynamicProperty(BARN_KEY);
    if (typeof raw === "string" && raw) {
      const barn = JSON.parse(raw);
      if (barn?.cows?.length) {
        if (!barn.catalog) barn.catalog = [];
        if (typeof barn.bellMode !== "number") barn.bellMode = 0;
        if (typeof barn.breedCooldown !== "number") barn.breedCooldown = 0;
        if (typeof barn.nextCowId !== "number") {
          let max = 0;
          for (const c of barn.cows) {
            const m = /^cow_(\d+)$/.exec(c.id);
            if (m) max = Math.max(max, parseInt(m[1], 10));
          }
          barn.nextCowId = max + 1;
        }
        if (!("deployedCowId" in barn)) barn.deployedCowId = null;
        if (!("deployedEntityId" in barn)) barn.deployedEntityId = null;
        if (typeof barn.tutorialStep !== "number") barn.tutorialStep = 3;
        if (barn.deployedEntityId) deployedEntities.set(player.id, barn.deployedEntityId);
        return barn;
      }
    }
  } catch (_) {
    /* ignore */
  }
  const barn = defaultBarn();
  saveBarn(player, barn);
  return barn;
}

function saveBarn(player, barn) {
  try {
    player.setDynamicProperty(BARN_KEY, JSON.stringify(barn));
  } catch (_) {
    /* ignore */
  }
}

function getCow(barn, id) {
  return barn.cows.find((c) => c.id === id);
}

function cowLabel(cow) {
  const shine = cow.coat === "shine" ? "§b✦ " : "";
  const coat = COAT_LABELS[cow.coat] ?? cow.coat;
  const sizeTag = cow.size === "chunk" ? "§6Big " : cow.size === "small" ? "§7Lil " : "";
  const calf = cow.feedsToAdult > 0 ? " §7(calf)" : "";
  return `${shine}${hornPrefix(cow.horns)}${sizeTag}${coat}${markSuffix(cow.mark)}${calf}`;
}

/** Short name for kids — no stats, horns, or catalog jargon. */
function simpleCowName(cow) {
  if (!cow) return "Cow";
  if (cow.feedsToAdult > 0) return "Baby Cow";
  const names = {
    brown: "Brown Cow",
    gray: "Gray Cow",
    spot: "Spotted Cow",
    storm: "Wild Cow",
    shine: "Shiny Cow",
  };
  if (cow.size === "chunk") return `Big ${names[cow.coat] ?? "Cow"}`;
  if (cow.size === "small") return `Tiny ${names[cow.coat] ?? "Cow"}`;
  return names[cow.coat] ?? "Cow";
}

function entityTypeForCow(cow) {
  if (cow.coat === "spot") return SPOT_COW;
  if (cow.coat === "storm" || cow.coat === "shine") return STORM_COW;
  return COW;
}

function applyCowVisuals(entity, cow, opts = {}) {
  const { particles = true } = opts;
  entity.nameTag = simpleCowName(cow);
  try {
    if (cow.size === "small") entity.setScale(0.78);
    else if (cow.size === "chunk") entity.setScale(1.32);
    else entity.setScale(1.0);
  } catch (_) {
    /* scale API unavailable on older engines */
  }
  if (!particles) return;
  const l = entity.location;
  const px = l.x;
  const py = l.y + 1;
  const pz = l.z;
  if (cow.horns === "gold") {
    try {
      entity.addEffect("glowing", 40, { showParticles: true });
    } catch (_) {
      /* ignore */
    }
    try {
      entity.runCommandAsync(`particle minecraft:totem_particle ${px} ${py} ${pz}`);
    } catch (_) {
      /* ignore */
    }
  }
  if (cow.mark === "star") {
    try {
      entity.runCommandAsync(`particle minecraft:villager_happy ${px} ${py} ${pz}`);
    } catch (_) {
      /* ignore */
    }
  } else if (cow.mark === "diamond") {
    try {
      entity.runCommandAsync(`particle minecraft:endrod ${px} ${py} ${pz}`);
    } catch (_) {
      /* ignore */
    }
  }
  if (cow.coat === "shine") {
    try {
      entity.runCommandAsync(`particle minecraft:villager_happy ${px} ${py} ${pz}`);
    } catch (_) {
      /* ignore */
    }
  }
}

function refreshDeployedVisuals(player, barn) {
  const eid = deployedEntities.get(player.id) ?? barn?.deployedEntityId;
  if (!eid || !barn?.deployedCowId) return;
  const cow = getCow(barn, barn.deployedCowId);
  if (!cow) return;
  try {
    for (const entity of playerDim(player).getEntities()) {
      if (entity.id === eid) {
        applyCowVisuals(entity, cow, { particles: false });
        return;
      }
    }
  } catch (_) {
    /* ignore */
  }
}

function persistDeployed(player, barn, cow, entityId) {
  barn.deployedCowId = cow.id;
  barn.deployedEntityId = entityId;
  deployedEntities.set(player.id, entityId);
  saveBarn(player, barn);
}

function clearDeployed(player, barn) {
  barn.deployedCowId = null;
  barn.deployedEntityId = null;
  deployedEntities.delete(player.id);
  saveBarn(player, barn);
}

function spawnCowEntity(player, barn, cow) {
  const dim = playerDim(player);
  const loc = safeSpawnNear(player, 2, 1);
  let typeId = entityTypeForCow(cow);
  let entity = trySpawnEntity(dim, typeId, loc);
  if (!entity && typeId !== COW) {
    entity = trySpawnEntity(dim, COW, loc);
  }
  if (!entity) {
    return null;
  }
  applyCowVisuals(entity, cow);
  persistDeployed(player, barn, cow, entity.id);
  return entity;
}

function recallDeployed(player, barn) {
  const eid = deployedEntities.get(player.id) ?? barn?.deployedEntityId;
  if (!eid) return false;
  try {
    for (const entity of playerDim(player).getEntities()) {
      if (entity.id === eid) {
        entity.remove();
        break;
      }
    }
  } catch (_) {
    /* ignore */
  }
  if (barn) clearDeployed(player, barn);
  else deployedEntities.delete(player.id);
  return true;
}

function traitsFromWildEntity(entity) {
  if (entity.typeId === SPOT_COW) {
    return {
      coat: "spot",
      horns: randomOf(HORNS),
      size: randomOf(SIZES),
      mark: randomOf(["none", "none", "star"]),
      gen: 0,
      feedsToAdult: 0,
      hunger: 85,
      mood: 80,
    };
  }
  if (entity.typeId === STORM_COW) {
    return {
      coat: Math.random() < 0.2 ? "shine" : "storm",
      horns: randomOf(HORNS),
      size: randomOf(SIZES),
      mark: randomOf(MARKS),
      gen: 0,
      feedsToAdult: 0,
      hunger: 85,
      mood: 80,
    };
  }
  return randomGen0Traits();
}

function findWildCow(player) {
  const deployedId = deployedEntities.get(player.id);
  const dim = playerDim(player);
  const loc = player.location;
  for (const entity of dim.getEntities({ location: loc, maxDistance: 5 })) {
    if (!CATCHABLE_COWS.has(entity.typeId)) continue;
    if (deployedId && entity.id === deployedId) continue;
    return entity;
  }
  return null;
}

function spawnTutorialWildCow(player) {
  const dim = playerDim(player);
  const offsets = [
    [3, 2],
    [3, -2],
    [-2, 3],
  ];
  let spawned = 0;
  for (const [dx, dz] of offsets) {
    const loc = safeSpawnNear(player, dx, dz);
    if (trySpawnEntity(dim, COW, loc)) spawned += 1;
    if (spawned >= 2) break;
  }
  return spawned;
}

function spawnNearbyChaosChickens(player, target = 4) {
  const dim = playerDim(player);
  const types = [ZOMBIE_CHICKEN, CHAOS_CHICKEN, CHAOS_CHICKEN, ZOMBIE_CHICKEN];
  const offsets = [
    [2, 1],
    [-2, 2],
    [4, -1],
    [-3, -2],
    [1, 4],
    [-4, 1],
  ];
  let spawned = 0;
  for (let i = 0; i < offsets.length && spawned < target; i += 1) {
    const [dx, dz] = offsets[i];
    const typeId = types[i % types.length];
    const loc = safeSpawnNear(player, dx, dz);
    if (trySpawnEntity(dim, typeId, loc)) spawned += 1;
  }
  return spawned;
}

function countNearbyChickens(player, maxDistance = 24) {
  let n = 0;
  try {
    for (const entity of playerDim(player).getEntities({
      location: player.location,
      maxDistance,
    })) {
      if (CHAOS_CHICKENS.has(entity.typeId)) n += 1;
    }
  } catch (_) {
    /* ignore */
  }
  return n;
}

function pulseLaserEyes() {
  if (!scriptReady) return;
  for (const player of world.getPlayers()) {
    try {
      const dim = playerDim(player);
      for (const entity of dim.getEntities({
        location: player.location,
        maxDistance: 20,
        type: ZOMBIE_CHICKEN,
      })) {
        if (Math.random() > 0.35) continue;
        const l = entity.location;
        player.runCommandAsync(
          `particle minecraft:redstone_particle ${l.x} ${l.y + 0.55} ${l.z + 0.2}`
        );
      }
    } catch (_) {
      /* ignore */
    }
  }
}

function ensureNearbyCows(player, barn, wildTarget = 2) {
  let spawned = 0;
  while (countWildCows(player) < wildTarget && spawned < wildTarget) {
    const batch = spawnTutorialWildCow(player);
    if (!batch) break;
    spawned += batch;
  }
  return countWildCows(player);
}

function reconcileDeployed(player, barn) {
  const eid = barn.deployedEntityId;
  if (!eid) return;
  try {
    for (const entity of playerDim(player).getEntities()) {
      if (entity.id === eid) {
        deployedEntities.set(player.id, eid);
        const cow = getCow(barn, barn.deployedCowId);
        if (cow) applyCowVisuals(entity, cow, { particles: false });
        return;
      }
    }
  } catch (_) {
    /* ignore */
  }
  clearDeployed(player, barn);
}

function cycleActiveCow(player, barn) {
  if (barn.cows.length < 2) return null;
  const idx = barn.cows.findIndex((c) => c.id === barn.activeId);
  const next = barn.cows[(idx + 1) % barn.cows.length];
  barn.activeId = next.id;
  return next;
}

function maybeRankUpMessage(player, barn, beforeRank) {
  const after = barnRank(barn);
  if (after.id !== beforeRank.id) {
    try {
      player.onScreenDisplay.setTitle("§a§lBIGGER BARN!");
    } catch (_) {
      /* ignore */
    }
    mooSound(player);
    cowParticles(player);
  }
}

function showNextStep(player, barn, extra = "") {
  touchUi(player);
  if (extra) {
    title(player, extra);
    return;
  }
  const step = barn.tutorialStep ?? 0;
  const cows = barn.cows.length;
  const hasOut = Boolean(barn.deployedEntityId || deployedEntities.get(player.id));

  if (step < TUTORIAL_DONE) {
    if (step < 1) {
      title(player, "Zombie chickens! Walk to a cow…");
      return;
    }
    if (cows < 2 && countWildCows(player) > 0) {
      title(player, "Stand by a cow → tap Feed Bag!");
      return;
    }
    if (cows >= 2 && !hasOut) {
      title(player, "Tap the Bell → Put cow outside!");
      return;
    }
    if (cows < 3) {
      title(player, `Catch ${3 - cows} more cow(s) — Feed Bag!`);
      return;
    }
    if (cows >= 3 && canBreed(barn)) {
      title(player, "Tap Bell → Make baby cow!");
      return;
    }
  }

  const active = getCow(barn, barn.activeId);
  if (active && active.hunger < 40) {
    title(player, "Your cow is hungry — tap Feed Bag!");
    return;
  }
  title(player, `${cows} cow(s) · Tap Bell · Have fun!`);
}

function mutateTrait(slot, current, barn) {
  const rank = barnRank(barn);
  const allowShine = rank.id === "spread" || rank.id === "legend";
  if (slot === "coat") {
    if (allowShine && Math.random() < 0.15) return "shine";
    if (Math.random() < 0.35) return "storm";
    return randomOf(COATS);
  }
  if (slot === "horns" && Math.random() < 0.2) return "gold";
  if (slot === "mark" && Math.random() < 0.15) return "diamond";
  if (slot === "size" && Math.random() < 0.2) return "chunk";
  return current;
}

function inheritTrait(parentA, parentB, slot, barn) {
  const pick = Math.random() < 0.5 ? parentA[slot] : parentB[slot];
  if (Math.random() < 0.14) return mutateTrait(slot, pick, barn);
  return pick;
}

function registerCatalog(barn, cow) {
  const added = [];
  for (const slot of ["coat", "horns", "size", "mark"]) {
    const key = traitKey(slot, cow[slot]);
    if (!barn.catalog.includes(key)) {
      barn.catalog.push(key);
      added.push(key);
    }
  }
  return added;
}

function giveDiscoveryLoot(player, keys) {
  try {
    const inv = player.getComponent("minecraft:inventory")?.container;
    if (!inv) return;
    for (const key of keys) {
      const factory = TRAIT_DISCOVERY_LOOT[key];
      if (factory) inv.addItem(factory());
    }
  } catch (_) {
    /* ignore */
  }
}

function adultsReady(barn) {
  return barn.cows.filter((c) => c.feedsToAdult === 0 && c.hunger >= 40 && c.mood >= 55);
}

function showBarnStatus(player, barn, extra = "") {
  showNextStep(player, barn, extra);
}

function feedCow(player, barn, cow) {
  cow.hunger = Math.min(100, cow.hunger + 28);
  cow.mood = Math.min(100, cow.mood + 12);
  if (cow.feedsToAdult > 0) {
    cow.feedsToAdult -= 1;
    if (cow.feedsToAdult === 0) say(player, "§aYour cow grew up! 🐄");
  }
  mooSound(player);
  cowParticles(player);
  if (barn.deployedCowId === cow.id) refreshDeployedVisuals(player, barn);
  saveBarn(player, barn);
}

function deployActive(player, barn) {
  const cow = getCow(barn, barn.activeId);
  if (!cow) {
    say(player, "No cow yet — catch one with Feed Bag!");
    return;
  }
  recallDeployed(player, barn);
  if (spawnCowEntity(player, barn, cow)) {
    if (barn.tutorialStep < 3) {
      barn.tutorialStep = 3;
      saveBarn(player, barn);
    }
    say(player, "§aYour cow is outside! 🐄");
    showBarnStatus(player, barn);
  }
}

function recallActive(player, barn) {
  const hadDeployed = recallDeployed(player, barn);
  const next = cycleActiveCow(player, barn);
  mooSound(player);
  if (next) {
    say(player, hadDeployed ? `Recalled. Next cow: ${cowLabel(next)}` : `Selected ${cowLabel(next)}`);
  } else {
    say(player, hadDeployed ? "Cow recalled to barn." : "Only one cow in the barn.");
  }
  showBarnStatus(player, barn);
}

function tryBreed(player, barn) {
  if (!canBreed(barn)) {
    const need = Math.max(0, 3 - barn.cows.length);
    say(player, need > 0 ? `§eCatch ${need} more cow(s) first!` : "§eNeed more cows!");
    showBarnStatus(player, barn);
    return;
  }
  if (barn.breedCooldown > 0) {
    say(player, "§eWait a moment, then try again!");
    return;
  }
  const adults = adultsReady(barn);
  if (adults.length < 2) {
    say(player, "§eFeed your cows first, then tap Make baby cow!");
    showBarnStatus(player, barn);
    return;
  }
  adults.sort((a, b) => b.mood + b.hunger - (a.mood + a.hunger));
  const parentA = adults[0];
  const parentB = adults[1];
  if (barn.cows.length >= maxSlots(barn)) {
    say(player, "§eBarn full — play more to get more room!");
    return;
  }

  const child = {
    id: nextCowId(barn),
    coat: inheritTrait(parentA, parentB, "coat", barn),
    horns: inheritTrait(parentA, parentB, "horns", barn),
    size: inheritTrait(parentA, parentB, "size", barn),
    mark: inheritTrait(parentA, parentB, "mark", barn),
    gen: Math.max(parentA.gen, parentB.gen) + 1,
    feedsToAdult: 3,
    hunger: 70,
    mood: 75,
  };

  const happyBonus = parentA.mood > 80 && parentB.mood > 80 && Math.random() < 0.25;
  if (happyBonus) child.coat = mutateTrait("coat", child.coat, barn);

  barn.cows.push(child);
  barn.activeId = child.id;
  barn.breedCooldown = 90;
  parentA.mood = Math.max(35, parentA.mood - 15);
  parentB.mood = Math.max(35, parentB.mood - 15);

  const discovered = registerCatalog(barn, child);
  if (discovered.length) giveDiscoveryLoot(player, discovered);

  say(player, "§d§lBaby cow! 🐣");
  if (barn.tutorialStep < TUTORIAL_DONE) {
    barn.tutorialStep = TUTORIAL_DONE;
  }
  mooSound(player);
  cowParticles(player);
  try {
    player.runCommandAsync("summon fireworks_rocket ~ ~2 ~");
  } catch (_) {
    /* ignore */
  }
  saveBarn(player, barn);
  showBarnStatus(player, barn);
}

function catchWildCow(player, barn) {
  const beforeRank = barnRank(barn);
  const limit = maxSlots(barn);
  if (barn.cows.length >= limit) {
    say(player, "§eBarn full!");
    return;
  }
  const target = findWildCow(player);
  if (!target) {
    say(player, "§eWalk closer to a cow, then tap Feed Bag!");
    return;
  }
  let caughtTraits;
  try {
    caughtTraits = traitsFromWildEntity(target);
    target.remove();
  } catch (_) {
    say(player, "Could not catch that cow — try again.");
    return;
  }
  const caught = { id: nextCowId(barn), ...caughtTraits };
  barn.cows.push(caught);
  const discovered = registerCatalog(barn, caught);
  if (discovered.length) giveDiscoveryLoot(player, discovered);
  maybeRankUpMessage(player, barn, beforeRank);
  say(player, "§a§lYou got a cow! 🐄");
  if (barn.tutorialStep < 2) {
    barn.tutorialStep = 2;
  }
  mooSound(player);
  saveBarn(player, barn);
  showBarnStatus(player, barn);
}

function onBellTapCycle(player) {
  const barn = loadBarn(player);
  deployActive(player, barn);
}

async function showHerdPicker(player) {
  const barn = loadBarn(player);
  if (barn.cows.length === 0) {
    say(player, "Your barn is empty — catch a wild cow!");
    return;
  }

  const form = new ActionFormData()
    .title("§6My Herd")
    .body(
      `Tap a cow to make it active.\n` +
        `${barnRank(barn).label} · ${barn.cows.length}/${maxSlots(barn)} · Catalog ${barn.catalog.length}/${CATALOG_SLOTS}`
    );

  const listed = barn.cows.slice(0, 15);
  for (const cow of listed) {
    const star = cow.id === barn.activeId ? "★ " : "";
    const hungry = cow.hunger < 40 ? " §c!" : "";
    form.button(`${star}${cowLabel(cow)} · H${cow.hunger}${hungry}`);
  }

  const response = await form.show(player);
  if (response.canceled || response.selection === undefined) return;

  const picked = listed[response.selection];
  if (!picked) return;

  recallDeployed(player, barn);
  barn.activeId = picked.id;
  saveBarn(player, barn);
  say(player, `§eActive cow:§f ${cowLabel(picked)}`);
  showBarnStatus(player, barn);
}

async function showBarnMenu(player) {
  const barn = loadBarn(player);

  const form = new ActionFormData()
    .title("§dWhat now?")
    .body(`You have ${barn.cows.length} cow(s).`)
    .button("§a🐄 Put cow outside")
    .button("§e🌾 Feed my cow")
    .button("§d🐣 Make baby cow");

  const response = await form.show(player);
  if (response.canceled) return;

  switch (response.selection) {
    case 0:
      deployActive(player, barn);
      break;
    case 1: {
      const cow = getCow(barn, barn.activeId);
      if (cow) {
        feedCow(player, barn, cow);
        say(player, "§aYum! 🌾");
        showBarnStatus(player, barn);
      } else {
        say(player, "§eCatch a cow with Feed Bag first!");
      }
      break;
    }
    case 2:
      tryBreed(player, barn);
      break;
    default:
      break;
  }
}

function onBellTap(player) {
  system.run(async () => {
    try {
      await showBarnMenu(player);
    } catch (err) {
      console.warn("[Cow Barn] Menu failed, using bell cycle fallback:", err);
      onBellTapCycle(player);
    }
  });
}

function hasRanchBell(player) {
  try {
    const inv = player.getComponent("minecraft:inventory")?.container;
    if (!inv) return false;
    for (let slot = 0; slot < inv.size; slot++) {
      const stack = inv.getItem(slot);
      if (stack?.typeId === RANCH_BELL_ID) return true;
    }
  } catch (_) {
    /* ignore */
  }
  return false;
}

function ensureOnboarded(player) {
  if (hasRanchBell(player)) return false;
  giveStarterKit(player);
  const barn = loadBarn(player);
  ensureNearbyCows(player, barn);
  spawnNearbyChaosChickens(player, 3);
  barn.tutorialStep = Math.max(barn.tutorialStep ?? 0, 1);
  saveBarn(player, barn);
  showNextStep(player, barn);
  return true;
}

function giveStarterKit(player) {
  try {
    const inv = player.getComponent("minecraft:inventory")?.container;
    if (!inv) return;
    const stacks = [
      [RANCH_BELL_ID, 1],
      [FEED_BAG_ID, 8],
      ["minecraft:cow_spawn_egg", 2],
      ["bgcow:zombie_chicken_spawn_egg", 2],
      ["bgcow:chaos_chicken_spawn_egg", 2],
    ];
    for (const [id, count] of stacks) {
      try {
        inv.addItem(new ItemStack(id, count));
      } catch (_) {
        /* optional spawn eggs */
      }
    }
  } catch (_) {
    /* ignore */
  }
}

function welcomePlayer(player) {
  const barn = loadBarn(player);
  reconcileDeployed(player, barn);
  giveStarterKit(player);
  spawnNearbyChaosChickens(player, 5);
  ensureNearbyCows(player, barn, 2);
  try {
    player.onScreenDisplay.setTitle("§d§lCHAOS WORLD!");
  } catch (_) {
    /* ignore */
  }
  barn.tutorialStep = Math.max(barn.tutorialStep ?? 0, 1);
  saveBarn(player, barn);
  cluckSound(player);
  showNextStep(player, barn);
}

// ─── Slash commands (parents) ──────────────────────────────────────────────

const HANDLERS = {
  help(player) {
    say(player, "§d══ Grown-up help ══");
    say(player, "§eBell§f = cow menu · §eFeed Bag§f = catch or feed cows");
    say(player, "§7NEW world needs Beta APIs + Holiday Creator Features ON.");
    say(player, "/bgcow:barn — full herd stats");
  },
  barn(player) {
    const barn = loadBarn(player);
    const rank = barnRank(barn);
    say(player, `Rank ${rank.label} · ${barn.cows.length}/${maxSlots(barn)} cows · Catalog ${barn.catalog.length}/${CATALOG_SLOTS}`);
    for (const cow of barn.cows.slice(0, 8)) {
      const active = cow.id === barn.activeId ? " §e★" : "";
      say(player, `  ${cowLabel(cow)} · H${cow.hunger} M${cow.mood}${active}`);
    }
    if (barn.cows.length > 8) say(player, `  ... +${barn.cows.length - 8} more`);
    showBarnStatus(player, barn);
  },
  breed(player) {
    tryBreed(player, loadBarn(player));
  },
  next(player) {
    const barn = loadBarn(player);
    recallDeployed(player, barn);
    const nextCow = cycleActiveCow(player, barn);
    if (nextCow) {
      say(player, `Active cow: ${cowLabel(nextCow)}`);
      saveBarn(player, barn);
      showBarnStatus(player, barn);
    } else {
      say(player, "Only one cow in the barn.");
    }
  },
};

const COMMANDS = [
  { name: "bgcow:help", desc: "Cow Barn help", fn: "help" },
  { name: "bgcow:barn", desc: "Show your barn and herd", fn: "barn" },
  { name: "bgcow:breed", desc: "Breed your two best adults", fn: "breed" },
  { name: "bgcow:next", desc: "Switch to your next cow", fn: "next" },
];

// ─── Register commands ─────────────────────────────────────────────────────

function sayBetaApisHint(player) {
  say(player, BETA_APIS_HINT);
}

system.beforeEvents.startup.subscribe((init) => {
  scriptReady = true;
  try {
    const reg = init.customCommandRegistry;
    for (const cmd of COMMANDS) {
      const handler = HANDLERS[cmd.fn];
      reg.registerCommand(
        {
          name: cmd.name,
          description: cmd.desc,
          permissionLevel: CommandPermissionLevel.Any,
          cheatsRequired: false,
        },
        (origin) => runFor(origin, handler)
      );
    }
    commandsReady = true;
    console.warn("[Chaos] Ready — cows, chickens, barn.");
  } catch (err) {
    console.warn("[Cow Barn] Command registration failed (bell/items still work):", err);
  }
});

// ─── Items ─────────────────────────────────────────────────────────────────

world.beforeEvents.itemUse.subscribe((event) => {
  const player = event.source;
  const stack = event.itemStack;
  if (!player || !stack || !scriptReady) return;

  if (isRanchBell(stack)) {
    event.cancel = true;
    system.run(() => onBellTap(player));
    return;
  }

  if (isFeedBag(stack)) {
    event.cancel = true;
    system.run(() => {
      const barn = loadBarn(player);
      const wild = findWildCow(player);
      if (wild) {
        catchWildCow(player, barn);
        return;
      }
      const cow = getCow(barn, barn.activeId);
      if (cow) {
        feedCow(player, barn, cow);
        say(player, "§aYum! 🌾");
        showBarnStatus(player, barn);
      } else {
        say(player, "§eWalk to a cow and tap Feed Bag!");
      }
    });
  }
});

// ─── Care decay ────────────────────────────────────────────────────────────

system.runInterval(() => {
  if (!scriptReady) return;
  simTick += 1;
  for (const player of world.getPlayers()) {
    const barn = loadBarn(player);
    let changed = false;
    if (barn.breedCooldown > 0) {
      barn.breedCooldown -= 1;
      changed = true;
    }
    for (const cow of barn.cows) {
      const prevH = cow.hunger;
      cow.hunger = Math.max(0, cow.hunger - 1);
      if (cow.hunger < 35) cow.mood = Math.max(0, cow.mood - 2);
      if (cow.hunger !== prevH || cow.mood < 100) changed = true;
      if (cow.hunger < 15 && deployedEntities.has(player.id) && barn.activeId === cow.id) {
        recallDeployed(player, barn);
      }
    }
    if (changed) saveBarn(player, barn);

    const lastUi = lastUiTick.get(player.id) ?? 0;
    const uiStale = simTick - lastUi > 8;
    if (uiStale) showNextStep(player, barn);
  }
}, 200);

system.runInterval(() => {
  pulseLaserEyes();
}, 80);

// ─── Join ──────────────────────────────────────────────────────────────────

world.afterEvents.playerSpawn.subscribe((event) => {
  const player = event.player;
  system.run(() => {
    if (!scriptReady) {
      sayBetaApisHint(player);
      return;
    }
    loadBarn(player);
    if (event.initialSpawn) welcomePlayer(player);
    else {
      const barn = loadBarn(player);
      reconcileDeployed(player, barn);
      if (countNearbyCows(player) === 0 && !barn.deployedEntityId) {
        ensureNearbyCows(player, barn);
      }
      showBarnStatus(player, barn);
    }
  });
});
