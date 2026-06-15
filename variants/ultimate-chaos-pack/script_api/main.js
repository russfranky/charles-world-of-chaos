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

const COW = "minecraft:cow";
const SPOT_COW = "bgcow:brindal_cow";
const STORM_COW = "bgcow:grayson_cow";

const BARN_KEY = "bgcow:barn_v1";
const RANCH_BELL = "Ranch Bell";
const FEED_BAG = "Feed Bag";

const BELL_MODES = ["deploy", "feed", "breed", "recall"];
const COATS = ["brown", "gray", "spot", "storm", "shine"];
const HORNS = ["none", "short", "gold"];
const SIZES = ["small", "normal", "chunk"];
const MARKS = ["none", "star", "diamond"];

const RANKS = [
  { id: "pen", slots: 2, label: "Pen" },
  { id: "yard", slots: 4, label: "Yard" },
  { id: "ranch", slots: 8, label: "Ranch" },
  { id: "spread", slots: 15, label: "Spread" },
  { id: "legend", slots: 30, label: "Legend" },
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
let commandsReady = false;
let cowCounter = 1;

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

function maxSlots(barn) {
  return barnRank(barn).slots;
}

function barnRank(barn) {
  const n = barn.cows.length;
  if (n >= 30) return RANKS[4];
  if (n >= 15) return RANKS[3];
  if (n >= 8) return RANKS[2];
  if (n >= 3) return RANKS[1];
  return RANKS[0];
}

function canBreed(barn) {
  return barn.cows.length >= 3 && barnRank(barn).id !== "pen";
}

function newCowId() {
  const id = `cow_${cowCounter}`;
  cowCounter += 1;
  return id;
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
  const starter = { id: newCowId(), ...randomGen0Traits() };
  return {
    cows: [starter],
    activeId: starter.id,
    catalog: [],
    bellMode: 0,
    breedCooldown: 0,
  };
}

function loadBarn(player) {
  try {
    const raw = player.getDynamicProperty(BARN_KEY);
    if (typeof raw === "string" && raw) {
      const barn = JSON.parse(raw);
      if (barn?.cows?.length) return barn;
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
  const parts = [cow.coat, cow.horns !== "none" ? cow.horns : null, cow.mark !== "none" ? cow.mark : null]
    .filter(Boolean)
    .join(" ");
  return `${shine}Gen${cow.gen} ${parts}`;
}

function entityTypeForCow(cow) {
  if (cow.coat === "spot") return SPOT_COW;
  if (cow.coat === "storm" || cow.coat === "shine") return STORM_COW;
  return COW;
}

function spawnCowEntity(player, cow) {
  const dim = playerDim(player);
  const loc = near(player, { x: 2, y: 0, z: 1 });
  try {
    const entity = dim.spawnEntity(entityTypeForCow(cow), loc);
    if (!entity) {
      say(player, HCF_HINT);
      return null;
    }
    entity.nameTag = cowLabel(cow);
    if (cow.coat === "shine") cowParticles(player);
    deployedEntities.set(player.id, entity.id);
    return entity;
  } catch (_) {
    say(player, HCF_HINT);
    return null;
  }
}

function recallDeployed(player) {
  const eid = deployedEntities.get(player.id);
  if (!eid) return;
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
  deployedEntities.delete(player.id);
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
  const rank = barnRank(barn);
  const active = getCow(barn, barn.activeId);
  const next = BELL_MODES[barn.bellMode].toUpperCase();
  const activeTxt = active ? ` · ${cowLabel(active)}` : "";
  title(
    player,
    extra || `${rank.label} · ${barn.cows.length}/${maxSlots(barn)} cows · Catalog ${barn.catalog.length}${activeTxt} · Bell: ${next}`
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
  recallDeployed(player);
  if (spawnCowEntity(player, cow)) {
    say(player, `Deployed ${cowLabel(cow)}`);
    showBarnStatus(player, barn);
  }
}

function recallActive(player, barn) {
  recallDeployed(player);
  mooSound(player);
  say(player, "Cow recalled to barn.");
  showBarnStatus(player, barn);
}

function tryBreed(player, barn) {
  if (!canBreed(barn)) {
    say(player, "Need Yard rank (3+ cows) to breed. Catch wild cows with Feed Bag!");
    return;
  }
  if (barn.breedCooldown > 0) {
    say(player, "Breed cooling down — feed your cows and try again soon.");
    return;
  }
  const adults = adultsReady(barn);
  if (adults.length < 2) {
    say(player, "Need 2 adults with hunger 40+ and mood 55+. Feed them!");
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
    id: newCowId(),
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
  const limit = maxSlots(barn);
  if (barn.cows.length >= limit) {
    say(player, `Barn full (${limit} slots). Breed or rank up.`);
    return;
  }
  const dim = playerDim(player);
  const loc = player.location;
  let target = null;
  for (const entity of dim.getEntities({ location: loc, maxDistance: 5 })) {
    if (entity.typeId === COW) {
      target = entity;
      break;
    }
  }
  if (!target) {
    say(player, "Stand near a wild cow to catch it with Feed Bag.");
    return;
  }
  try {
    target.remove();
  } catch (_) {
    /* ignore */
  }
  const caught = { id: newCowId(), ...randomGen0Traits() };
  barn.cows.push(caught);
  const discovered = registerCatalog(barn, caught);
  if (discovered.length) giveDiscoveryLoot(player, discovered);
  say(player, `§aCaught ${cowLabel(caught)}!§f Barn: ${barn.cows.length}/${limit}`);
  mooSound(player);
  saveBarn(player, barn);
  showBarnStatus(player, barn);
}

function onBellTap(player) {
  const barn = loadBarn(player);
  const mode = BELL_MODES[barn.bellMode];
  barn.bellMode = (barn.bellMode + 1) % BELL_MODES.length;

  switch (mode) {
    case "deploy":
      deployActive(player, barn);
      break;
    case "feed": {
      const cow = getCow(barn, barn.activeId);
      if (cow) {
        feedCow(player, barn, cow);
        say(player, `Fed ${cowLabel(cow)} · hunger ${cow.hunger} · mood ${cow.mood}`);
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
  saveBarn(player, barn);
  showBarnStatus(player, barn, `Next bell: ${BELL_MODES[barn.bellMode].toUpperCase()}`);
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
  giveStarterKit(player);
  const starter = getCow(barn, barn.activeId);
  say(player, "§eCow Barn§f — cycle Ranch Bell: DEPLOY · FEED · BREED · RECALL");
  say(player, "Feed Bag near a wild cow = catch. Breed at 3+ cows.");
  if (starter) say(player, `Starter: ${cowLabel(starter)}`);
  mooSound(player);
  showBarnStatus(player, barn);
}

// ─── Slash commands (parents) ──────────────────────────────────────────────

const HANDLERS = {
  help(player) {
    say(player, "§6══ Cow Barn ══");
    say(player, "§eRanch Bell§f cycles: DEPLOY → FEED → BREED → RECALL");
    say(player, "§eFeed Bag§f on your cow = feed. Near wild cow = catch.");
    say(player, "Breed two happy adults for new traits + loot.");
    say(player, "/bgcow:barn — barn status");
  },
  barn(player) {
    const barn = loadBarn(player);
    const rank = barnRank(barn);
    say(player, `Rank ${rank.label} · ${barn.cows.length} cows · Catalog ${barn.catalog.length}/24`);
    for (const cow of barn.cows.slice(0, 8)) {
      say(player, `  ${cow.id}: ${cowLabel(cow)} · H${cow.hunger} M${cow.mood}`);
    }
    if (barn.cows.length > 8) say(player, `  ... +${barn.cows.length - 8} more`);
    showBarnStatus(player, barn);
  },
  breed(player) {
    tryBreed(player, loadBarn(player));
  },
};

const COMMANDS = [
  { name: "bgcow:help", desc: "Cow Barn help", fn: "help" },
  { name: "bgcow:barn", desc: "Show your barn and herd", fn: "barn" },
  { name: "bgcow:breed", desc: "Breed your two best adults", fn: "breed" },
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
    system.run(() => {
      const barn = loadBarn(player);
      const dim = playerDim(player);
      const loc = player.location;
      let wild = false;
      for (const entity of dim.getEntities({ location: loc, maxDistance: 5 })) {
        if (entity.typeId === COW) {
          wild = true;
          break;
        }
      }
      if (wild) {
        catchWildCow(player, barn);
      } else {
        const cow = getCow(barn, barn.activeId);
        if (cow) {
          feedCow(player, barn, cow);
          say(player, `Fed ${cowLabel(cow)} · hunger ${cow.hunger} · mood ${cow.mood}`);
          showBarnStatus(player, barn);
        } else {
          say(player, "Stand near a wild cow to catch, or set an active cow.");
        }
      }
    });
  }
});

// ─── Care decay ────────────────────────────────────────────────────────────

system.runInterval(() => {
  if (!commandsReady) return;
  for (const player of world.getPlayers()) {
    const barn = loadBarn(player);
    let changed = false;
    if (barn.breedCooldown > 0) {
      barn.breedCooldown -= 1;
      changed = true;
    }
    for (const cow of barn.cows) {
      cow.hunger = Math.max(0, cow.hunger - 1);
      if (cow.hunger < 35) cow.mood = Math.max(0, cow.mood - 2);
      if (cow.hunger < 15 && deployedEntities.has(player.id) && barn.activeId === cow.id) {
        recallDeployed(player);
        say(player, `${cowLabel(cow)} got hungry and returned to the barn.`);
      }
    }
    if (changed) saveBarn(player, barn);
    if (barn.cows.some((c) => c.hunger < 40)) {
      title(player, `Feed your cows — active hunger ${getCow(barn, barn.activeId)?.hunger ?? "?"}`);
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
    else showBarnStatus(player, loadBarn(player));
  });
});
