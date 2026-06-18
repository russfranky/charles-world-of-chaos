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
const CATCHABLE_COWS = new Set([COW, SPOT_COW, STORM_COW]);
const CATALOG_SLOTS = 15; // coats(5) + horns(3) + sizes(3) + marks(4)

const BARN_KEY = "bgcow:barn_v1";
const RANCH_BELL = "Ranch Bell";
const FEED_BAG = "Feed Bag";

const BELL_MODES = ["deploy", "feed", "breed", "recall"];
const COATS = ["brown", "gray", "spot", "storm", "shine"];
const HORNS = ["none", "short", "gold"];
const SIZES = ["small", "normal", "chunk"];
const MARKS = ["none", "star", "diamond"];

const COAT_LABELS = {
  brown: "Brown",
  gray: "Gray",
  spot: "Spot Cow",
  storm: "Storm Cow",
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
  "Cow Barn needs Beta APIs ON in a NEW world. Ask a grown-up to turn on Beta APIs.";
const HCF_HINT =
  "Custom cows need Holiday Creator Features ON in a NEW world.";

const deployedEntities = new Map();
const lastUiTick = new Map();
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

function say(player, msg) {
  try {
    player.sendMessage(`§6[Cow Barn] §f${msg}`);
  } catch (_) {
    /* spectator */
  }
}

function title(player, msg) {
  try {
    player.onScreenDisplay.setActionBar(`§e🐄 ${msg}`);
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
  return stack?.typeId === "minecraft:bell" && (stack.nameTag ?? "").includes(RANCH_BELL);
}

function isFeedBag(stack) {
  return stack?.typeId === "minecraft:wheat" && (stack.nameTag ?? "").includes(FEED_BAG);
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
  const starter = { id: nextCowId(barn), ...randomGen0Traits() };
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

function entityTypeForCow(cow) {
  if (cow.coat === "spot") return SPOT_COW;
  if (cow.coat === "storm" || cow.coat === "shine") return STORM_COW;
  return COW;
}

function applyCowVisuals(entity, cow) {
  entity.nameTag = cowLabel(cow);
  try {
    if (cow.size === "small") entity.setScale(0.78);
    else if (cow.size === "chunk") entity.setScale(1.32);
    else entity.setScale(1.0);
  } catch (_) {
    /* scale API unavailable on older engines */
  }
  if (cow.coat === "shine" || cow.mark === "star") {
    try {
      const l = entity.location;
      entity.runCommandAsync(
        `particle minecraft:villager_happy ${l.x} ${l.y + 1} ${l.z}`
      );
    } catch (_) {
      /* ignore */
    }
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
  const loc = near(player, { x: 2, y: 0, z: 1 });
  try {
    const entity = dim.spawnEntity(entityTypeForCow(cow), loc);
    if (!entity) {
      say(player, HCF_HINT);
      return null;
    }
    applyCowVisuals(entity, cow);
    persistDeployed(player, barn, cow, entity.id);
    return entity;
  } catch (_) {
    say(player, HCF_HINT);
    return null;
  }
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
  try {
    playerDim(player).spawnEntity(COW, near(player, { x: 4, y: 0, z: 2 }));
  } catch (_) {
    /* ignore */
  }
}

function reconcileDeployed(player, barn) {
  const eid = barn.deployedEntityId;
  if (!eid) return;
  try {
    for (const entity of playerDim(player).getEntities()) {
      if (entity.id === eid) {
        deployedEntities.set(player.id, eid);
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
    say(player, `§a§lBARN UP!§f ${after.label} rank — room for ${after.slots} cows!`);
    if (after.id === "yard") {
      say(player, "§eYou can breed now!§f Bell → BREED when two adults are happy.");
    }
    mooSound(player);
    cowParticles(player);
  }
}

function progressHint(player, barn) {
  const need = cowsToNextRank(barn);
  if (need === 1) {
    say(player, "§eTip:§f Catch §l1 more cow§f with Feed Bag to rank up!");
  } else if (need === 2) {
    say(player, "§eTip:§f Catch §l2 more cows§f with Feed Bag near wild cows.");
  } else if (canBreed(barn) && adultsReady(barn).length < 2) {
    say(player, "§eTip:§f Feed your adults (hunger 40+, mood 55+) then bell → BREED.");
  }
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
  touchUi(player);
  const rank = barnRank(barn);
  const active = getCow(barn, barn.activeId);
  const next = BELL_MODES[barn.bellMode].toUpperCase();
  const activeTxt = active ? ` · ${cowLabel(active)}` : "";
  const hungry = active && active.hunger < 40 ? " §c· feed me!" : "";
  title(
    player,
    extra || `${rank.label} · ${barn.cows.length}/${maxSlots(barn)} · Catalog ${barn.catalog.length}/${CATALOG_SLOTS}${activeTxt}${hungry} · Tap Bell`
  );
}

function feedCow(player, barn, cow) {
  cow.hunger = Math.min(100, cow.hunger + 28);
  cow.mood = Math.min(100, cow.mood + 12);
  if (cow.feedsToAdult > 0) {
    cow.feedsToAdult -= 1;
    if (cow.feedsToAdult === 0) say(player, `§a${cowLabel(cow)}§f is now an adult!`);
  }
  mooSound(player);
  cowParticles(player);
  saveBarn(player, barn);
}

function deployActive(player, barn) {
  const cow = getCow(barn, barn.activeId);
  if (!cow) {
    say(player, "No active cow. Your barn is empty.");
    return;
  }
  recallDeployed(player, barn);
  if (spawnCowEntity(player, barn, cow)) {
    say(player, `Deployed ${cowLabel(cow)}`);
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
    if (need > 0) {
      say(player, `Need ${need} more cow(s) — Feed Bag near wild cows to catch them!`);
    } else {
      say(player, "Need Yard rank (3+ cows) to breed.");
    }
    progressHint(player, barn);
    return;
  }
  if (barn.breedCooldown > 0) {
    say(player, `Breed cooling down (${breedCooldownLabel(barn.breedCooldown)}) — feed your cows!`);
    return;
  }
  const adults = adultsReady(barn);
  if (adults.length < 2) {
    say(player, "Need 2 adults with hunger 40+ and mood 55+. Feed them!");
    progressHint(player, barn);
    return;
  }
  adults.sort((a, b) => b.mood + b.hunger - (a.mood + a.hunger));
  const parentA = adults[0];
  const parentB = adults[1];
  if (barn.cows.length >= maxSlots(barn)) {
    say(player, "Barn full. Breed when you have space.");
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
  if (discovered.length) {
    say(player, `§dNEW TRAIT!§f ${discovered.join(", ")}`);
    giveDiscoveryLoot(player, discovered);
  }

  say(player, `§aBred ${cowLabel(child)}§f from ${cowLabel(parentA)} × ${cowLabel(parentB)}`);
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
    say(player, `Barn full (${limit} slots). Breed for more room!`);
    return;
  }
  const target = findWildCow(player);
  if (!target) {
    say(player, "Stand near a §lwild§f cow (not your deployed cow) to catch it.");
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
  if (discovered.length) {
    say(player, `§dNEW TRAIT!§f ${discovered.join(", ")}`);
    giveDiscoveryLoot(player, discovered);
  }
  maybeRankUpMessage(player, barn, beforeRank);
  say(player, `§aCaught ${cowLabel(caught)}!§f Barn: ${barn.cows.length}/${limit}`);
  if (barn.tutorialStep < 2) {
    barn.tutorialStep = 2;
    say(player, "§eNice catch!§f Tap Ranch Bell → Breed when you have 3 cows.");
  }
  progressHint(player, barn);
  mooSound(player);
  saveBarn(player, barn);
  showBarnStatus(player, barn);
}

function onBellTapCycle(player) {
  const barn = loadBarn(player);
  const mode = BELL_MODES[barn.bellMode];
  const modeLabel = mode.toUpperCase();

  switch (mode) {
    case "deploy":
      deployActive(player, barn);
      break;
    case "feed": {
      const cow = getCow(barn, barn.activeId);
      if (cow) {
        feedCow(player, barn, cow);
        say(player, `Fed ${cowLabel(cow)} · hunger ${cow.hunger} · mood ${cow.mood}`);
      } else {
        say(player, "No active cow to feed.");
      }
      break;
    }
    case "breed":
      tryBreed(player, barn);
      break;
    case "recall":
      recallActive(player, barn);
      break;
    default:
      break;
  }

  barn.bellMode = (barn.bellMode + 1) % BELL_MODES.length;
  saveBarn(player, barn);
  showBarnStatus(player, barn, `${modeLabel} done · Next: ${BELL_MODES[barn.bellMode].toUpperCase()}`);
}

async function showBarnMenu(player) {
  const barn = loadBarn(player);
  const rank = barnRank(barn);
  const active = getCow(barn, barn.activeId);
  const activeLine = active
    ? `${cowLabel(active)} · H${active.hunger} M${active.mood}`
    : "No active cow";

  const form = new ActionFormData()
    .title("§6Cow Barn")
    .body(
      `${rank.label} · ${barn.cows.length}/${maxSlots(barn)} cows\n` +
        `Catalog ${barn.catalog.length}/${CATALOG_SLOTS}\n` +
        `${activeLine}\n\n` +
        `Feed Bag near wild cows catches them.`
    )
    .button("Deploy my cow")
    .button("Feed my cow")
    .button("Breed cows")
    .button("Recall / next cow")
    .button("My herd");

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
        say(player, `Fed ${cowLabel(cow)} · hunger ${cow.hunger} · mood ${cow.mood}`);
        showBarnStatus(player, barn);
      } else {
        say(player, "No active cow — deploy one first.");
      }
      break;
    }
    case 2:
      tryBreed(player, barn);
      break;
    case 3:
      recallActive(player, barn);
      break;
    case 4:
      HANDLERS.barn(player);
      break;
    default:
      break;
  }
}

function onBellTap(player) {
  system.run(async () => {
    try {
      await showBarnMenu(player);
    } catch (_) {
      onBellTapCycle(player);
    }
  });
}

function giveStarterKit(player) {
  try {
    const inv = player.getComponent("minecraft:inventory")?.container;
    if (!inv) return;
    const bell = new ItemStack("minecraft:bell", 1);
    bell.nameTag = RANCH_BELL;
    inv.addItem(bell);
    const bag = new ItemStack("wheat", 16);
    bag.nameTag = FEED_BAG;
    inv.addItem(bag);
    inv.addItem(new ItemStack("cookie", 4));
  } catch (_) {
    /* ignore */
  }
}

function welcomePlayer(player) {
  const barn = loadBarn(player);
  reconcileDeployed(player, barn);
  giveStarterKit(player);
  const starter = getCow(barn, barn.activeId);
  try {
    player.onScreenDisplay.setTitle("§6Cow Barn!");
  } catch (_) {
    /* ignore */
  }
  say(player, "§eTap Ranch Bell§f for a menu — Deploy, Feed, Breed, Recall.");
  say(player, "§eFeed Bag§f near a wild cow catches it. Need 3 cows to breed!");
  if (starter) say(player, `Starter: ${cowLabel(starter)}`);
  if (barn.tutorialStep < 1) {
    barn.tutorialStep = 1;
    spawnTutorialWildCow(player);
    say(player, "§aA wild cow appeared nearby!§f Use Feed Bag on it.");
    saveBarn(player, barn);
  }
  progressHint(player, barn);
  mooSound(player);
  deployActive(player, barn);
  showBarnStatus(player, barn);
}

// ─── Slash commands (parents) ──────────────────────────────────────────────

const HANDLERS = {
  help(player) {
    say(player, "§6══ Cow Barn ══");
    say(player, "§eRanch Bell§f opens the barn menu (Deploy · Feed · Breed · Recall)");
    say(player, "§eFeed Bag§f feeds your cow. Near a wild cow = catch.");
    say(player, "Recall also switches to your next cow.");
    say(player, "/bgcow:barn — herd list · /bgcow:next — switch active cow");
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
    console.warn("[Cow Barn] Ready — breed, deploy, collect.");
  } catch (err) {
    console.warn("[Cow Barn] Command registration failed:", err);
  }
});

// ─── Items ─────────────────────────────────────────────────────────────────

world.beforeEvents.itemUse.subscribe((event) => {
  const player = event.source;
  const stack = event.itemStack;
  if (!player || !stack || !commandsReady) return;

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
        say(player, `Fed ${cowLabel(cow)} · hunger ${cow.hunger} · mood ${cow.mood}`);
        showBarnStatus(player, barn);
      } else {
        say(player, "Stand near a wild cow to catch, or deploy a cow first.");
      }
    });
  }
});

// ─── Care decay ────────────────────────────────────────────────────────────

system.runInterval(() => {
  if (!commandsReady) return;
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
        say(player, `${cowLabel(cow)} got hungry and returned to the barn.`);
      }
    }
    if (changed) saveBarn(player, barn);

    const active = getCow(barn, barn.activeId);
    const lastUi = lastUiTick.get(player.id) ?? 0;
    const uiStale = simTick - lastUi > 6;
    if (uiStale && active && active.hunger < 40) {
      showBarnStatus(player, barn, `§cFeed ${cowLabel(active)}!§f · Bell: ${BELL_MODES[barn.bellMode].toUpperCase()}`);
    }
  }
}, 200);

// ─── Join ──────────────────────────────────────────────────────────────────

world.afterEvents.playerSpawn.subscribe((event) => {
  const player = event.player;
  system.run(() => {
    if (!commandsReady) {
      sayBetaApisHint(player);
      return;
    }
    loadBarn(player);
    if (event.initialSpawn) welcomePlayer(player);
    else {
      const barn = loadBarn(player);
      reconcileDeployed(player, barn);
      showBarnStatus(player, barn);
    }
  });
});
