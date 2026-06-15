/**
 * Brindal & Grayson Cow World — Script API
 * Cowifier backup + tons of fun commands for kids!
 */
import {
  world,
  system,
  CustomCommandStatus,
  CommandPermissionLevel,
  ItemStack,
} from "@minecraft/server";

const COW = "minecraft:cow";
const BRINDAL = "bgcow:brindal_cow";
const GRAYSON = "bgcow:grayson_cow";
const SKIP_COWIFY = new Set([
  COW,
  "minecraft:mooshroom",
  "minecraft:player",
  BRINDAL,
  GRAYSON,
]);

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
    player.sendMessage(`§6[Cow World] §f${msg}`);
  } catch (_) {
    /* spectator etc */
  }
}

function title(player, msg) {
  try {
    player.onScreenDisplay.setActionBar(`§e🐄 ${msg} §e🐄`);
  } catch (_) {
    say(player, msg);
  }
}

function mooSound(player) {
  try {
    player.playSound("mob.cow.say", { volume: 1.0, pitch: 0.9 + Math.random() * 0.2 });
  } catch (_) {}
}

function spawn(dim, typeId, loc) {
  try {
    return dim.spawnEntity(typeId, loc);
  } catch (_) {
    return null;
  }
}

function spawnNamed(dim, typeId, loc, name) {
  const entity = spawn(dim, typeId, loc);
  if (!entity) return null;
  try {
    entity.nameTag = name;
  } catch (_) {
    /* older API */
  }
  return entity;
}

function spawnRing(player, typeId, count, radius = 4) {
  const dim = playerDim(player);
  const base = player.location;
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2;
    const loc = {
      x: base.x + Math.cos(angle) * radius,
      y: base.y,
      z: base.z + Math.sin(angle) * radius,
    };
    spawn(dim, typeId, loc);
  }
}

function cowifyEntity(entity) {
  if (!entity || SKIP_COWIFY.has(entity.typeId)) return;
  try {
    const loc = entity.location;
    const dim = entity.dimension;
    entity.remove();
    dim.spawnEntity(COW, loc);
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

// ─── Command handlers ──────────────────────────────────────────────────────

const HANDLERS = {
  moo(player) {
    mooSound(player);
    spawn(playerDim(player), COW, near(player, { x: 1, y: 0, z: 0 }));
    title(player, "MOOO!");
  },

  brindal(player) {
    mooSound(player);
    spawnNamed(playerDim(player), BRINDAL, near(player, { x: 2, y: 0, z: 0 }), "Brindal");
    say(player, "Brindal's cow appeared! §6🐄");
  },

  grayson(player) {
    mooSound(player);
    spawnNamed(playerDim(player), GRAYSON, near(player, { x: -2, y: 0, z: 0 }), "Grayson");
    say(player, "Grayson's cow appeared! §7🐄");
  },

  twins(player) {
    mooSound(player);
    spawnNamed(playerDim(player), BRINDAL, near(player, { x: 2, y: 0, z: 1 }), "Brindal");
    spawnNamed(playerDim(player), GRAYSON, near(player, { x: -2, y: 0, z: 1 }), "Grayson");
    title(player, "Brindal & Grayson cows!");
  },

  party(player) {
    mooSound(player);
    spawnRing(player, COW, 10, 5);
    spawnRing(player, BRINDAL, 2, 3);
    spawnRing(player, GRAYSON, 2, 3);
    title(player, "COW PARTY!");
    say(player, "Everyone's invited! 🎉🐄");
  },

  rain(player) {
    const dim = playerDim(player);
    const base = player.location;
    for (let i = 0; i < 12; i++) {
      const loc = {
        x: base.x + (Math.random() - 0.5) * 12,
        y: base.y + 8 + Math.random() * 6,
        z: base.z + (Math.random() - 0.5) * 12,
      };
      spawn(dim, Math.random() > 0.5 ? BRINDAL : GRAYSON, loc);
      if (i % 3 === 0) spawn(dim, COW, loc);
    }
    title(player, "IT'S RAINING COWS!");
    mooSound(player);
  },

  stampede(player) {
    const dim = playerDim(player);
    const base = player.location;
    const rot = player.getRotation();
    const yaw = (rot?.y ?? 0) * (Math.PI / 180);
    for (let i = 0; i < 15; i++) {
      const dist = 8 + i * 2;
      spawn(dim, COW, {
        x: base.x - Math.sin(yaw) * dist + (Math.random() - 0.5) * 4,
        y: base.y,
        z: base.z + Math.cos(yaw) * dist + (Math.random() - 0.5) * 4,
      });
    }
    title(player, "STAMPEDE!");
    mooSound(player);
  },

  mega(player) {
    mooSound(player);
    spawnRing(player, COW, 20, 8);
    spawnRing(player, BRINDAL, 5, 4);
    spawnRing(player, GRAYSON, 5, 4);
    title(player, "MEGA MOOOOO!");
    say(player, "§l§6ULTIMATE COW CHAOS§r");
  },

  heal(player) {
    try {
      const health = player.getComponent("minecraft:health");
      if (health) health.setCurrentValue(health.effectiveMax);
      player.addEffect("regeneration", 60, { amplifier: 2, showParticles: true });
    } catch (_) {}
    mooSound(player);
    say(player, "Cow magic healed you! 💚");
  },

  fly(player) {
    try {
      player.addEffect("levitation", 80, { amplifier: 2, showParticles: true });
      player.addEffect("slow_falling", 200, { amplifier: 0, showParticles: true });
    } catch (_) {}
    title(player, "Flying like a cow!");
    mooSound(player);
  },

  jump(player) {
    try {
      player.addEffect("jump_boost", 120, { amplifier: 4, showParticles: true });
    } catch (_) {}
    title(player, "Super cow jump!");
    mooSound(player);
  },

  sunny(player) {
    try {
      world.setTimeOfDay(1000);
      player.runCommandAsync("weather clear");
    } catch (_) {}
    spawnRing(player, COW, 4, 3);
    say(player, "Sunny cow day! ☀️🐄");
  },

  night(player) {
    try {
      world.setTimeOfDay(13000);
    } catch (_) {}
    say(player, "Cheese moon night! 🌙🧀");
    mooSound(player);
  },

  milk(player) {
    try {
      const inv = player.getComponent("minecraft:inventory")?.container;
      if (inv) inv.addItem(new ItemStack("minecraft:milk_bucket", 1));
    } catch (_) {
      try {
        player.runCommandAsync("give @s milk_bucket 1");
      } catch (_) {}
    }
    say(player, "Fresh milk! 🥛");
    mooSound(player);
  },

  feast(player) {
    try {
      player.runCommandAsync("give @s wheat 16");
      player.runCommandAsync("give @s milk_bucket 3");
      player.runCommandAsync("give @s cookie 8");
    } catch (_) {}
    spawnRing(player, COW, 6, 4);
    say(player, "Cow feast for Brindal & Grayson! 🌾🥛");
  },

  bell(player) {
    for (let i = 0; i < 5; i++) {
      system.runTimeout(() => mooSound(player), i * 4);
    }
    title(player, "DING DONG MOO!");
  },

  love(player) {
    spawnNamed(playerDim(player), BRINDAL, near(player, { x: 1, y: 0, z: 1 }), "Brindal");
    spawnNamed(playerDim(player), GRAYSON, near(player, { x: -1, y: 0, z: 1 }), "Grayson");
    try {
      player.addEffect("village_hero", 30, { amplifier: 0, showParticles: true });
    } catch (_) {}
    say(player, "Brindal & Grayson love cows! ❤️🐄");
    mooSound(player);
  },

  cowify(player) {
    const dim = playerDim(player);
    const loc = player.location;
    let count = 0;
    for (const entity of dim.getEntities({ location: loc, maxDistance: 16 })) {
      if (!SKIP_COWIFY.has(entity.typeId)) {
        cowifyEntity(entity);
        count++;
      }
    }
    say(player, `Cowified ${count} mobs nearby! 🐄`);
    mooSound(player);
  },

  help(player) {
    const lines = [
      "§6═══ Cow World Commands ═══",
      "§e/bgcow:moo §7— spawn a cow",
      "§e/bgcow:brindal §7— Brindal's cow",
      "§e/bgcow:grayson §7— Grayson's cow",
      "§e/bgcow:twins §7— both cows!",
      "§e/bgcow:party §7— cow party 🎉",
      "§e/bgcow:rain §7— raining cows",
      "§e/bgcow:stampede §7— cow stampede",
      "§e/bgcow:mega §7— MEGA chaos",
      "§e/bgcow:heal §7— cow magic heal",
      "§e/bgcow:fly §7— cow levitation",
      "§e/bgcow:jump §7— super jump",
      "§e/bgcow:sunny §7— sunny day + cows",
      "§e/bgcow:night §7— cheese moon night",
      "§e/bgcow:milk §7— free milk bucket",
      "§e/bgcow:feast §7— wheat + milk feast",
      "§e/bgcow:bell §7— cowbell concert",
      "§e/bgcow:love §7— Brindal & Grayson cows",
      "§e/bgcow:cowify §7— turn nearby mobs into cows",
      "§7Or type §e!moo !party !rain §7in chat!",
    ];
    for (const line of lines) say(player, line);
  },
};

// ─── Register slash commands ───────────────────────────────────────────────

let commandsReady = false;

const BETA_APIS_HINT =
  "Fun commands need Beta APIs ON when you create the world. Ask a grown-up to make a NEW world with Beta APIs enabled.";

function sayBetaApisHint(player) {
  say(player, BETA_APIS_HINT);
}

const COMMANDS = [
  { name: "bgcow:moo", desc: "Spawn a cow and moo!", fn: "moo" },
  { name: "bgcow:brindal", desc: "Summon Brindal's special cow", fn: "brindal" },
  { name: "bgcow:grayson", desc: "Summon Grayson's special cow", fn: "grayson" },
  { name: "bgcow:twins", desc: "Summon both Brindal & Grayson cows", fn: "twins" },
  { name: "bgcow:party", desc: "Cow party — herd all around you!", fn: "party" },
  { name: "bgcow:rain", desc: "Make it rain cows from the sky!", fn: "rain" },
  { name: "bgcow:stampede", desc: "Cow stampede incoming!", fn: "stampede" },
  { name: "bgcow:mega", desc: "MEGA cow chaos — so many cows!", fn: "mega" },
  { name: "bgcow:heal", desc: "Cow magic heals you", fn: "heal" },
  { name: "bgcow:fly", desc: "Float like a happy cow", fn: "fly" },
  { name: "bgcow:jump", desc: "Super cow jump boost", fn: "jump" },
  { name: "bgcow:sunny", desc: "Sunny day with friendly cows", fn: "sunny" },
  { name: "bgcow:night", desc: "Cheese moon night", fn: "night" },
  { name: "bgcow:milk", desc: "Get a milk bucket", fn: "milk" },
  { name: "bgcow:feast", desc: "Cow feast — wheat, milk, cookies!", fn: "feast" },
  { name: "bgcow:bell", desc: "Cowbell concert!", fn: "bell" },
  { name: "bgcow:love", desc: "Spawn Brindal & Grayson cows with love", fn: "love" },
  { name: "bgcow:cowify", desc: "Turn nearby mobs into cows", fn: "cowify" },
  { name: "bgcow:help", desc: "List all Cow World commands", fn: "help" },
];

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
    console.warn("[BG Cow World] Moo! 19 commands ready for Brindal & Grayson!");
  } catch (err) {
    console.warn("[BG Cow World] Command registration failed:", err);
  }
});

// ─── Chat shortcuts (!moo, !party, etc.) ─────────────────────────────────

const CHAT_ALIASES = {
  "!moo": "moo",
  "!brindal": "brindal",
  "!grayson": "grayson",
  "!twins": "twins",
  "!party": "party",
  "!rain": "rain",
  "!stampede": "stampede",
  "!mega": "mega",
  "!heal": "heal",
  "!fly": "fly",
  "!jump": "jump",
  "!sunny": "sunny",
  "!night": "night",
  "!milk": "milk",
  "!feast": "feast",
  "!bell": "bell",
  "!love": "love",
  "!cowify": "cowify",
  "!help": "help",
  "!cowhelp": "help",
  "!b": "brindal",
  "!g": "grayson",
};

world.beforeEvents.chatSend.subscribe((event) => {
  const msg = event.message;
  if (!msg.startsWith("!")) return;
  const key = msg.trim().toLowerCase().split(/\s+/)[0];
  const fnName = CHAT_ALIASES[key];
  if (!fnName || !HANDLERS[fnName]) return;
  event.cancel = true;
  const player = event.sender;
  system.run(() => HANDLERS[fnName](player));
});

// ─── Welcome new players ───────────────────────────────────────────────────

function welcomePlayer(player) {
  mooSound(player);
  title(player, "Welcome to Moo World!");
  say(player, "Meet Brindal & Grayson! Try §e!moo §f§e!b §f§e!g §f§e!party §f— or §e/bgcow:help");
  const dim = playerDim(player);
  spawnNamed(dim, BRINDAL, near(player, { x: 3, y: 0, z: 2 }), "Brindal");
  spawnNamed(dim, GRAYSON, near(player, { x: -3, y: 0, z: 2 }), "Grayson");
  try {
    const inv = player.getComponent("minecraft:inventory")?.container;
    if (inv) inv.addItem(new ItemStack("wheat", 8));
  } catch (_) {
    /* ignore */
  }
}

world.afterEvents.playerSpawn.subscribe((event) => {
  if (!event.initialSpawn) return;
  const player = event.player;
  system.run(() => {
    if (!commandsReady) {
      sayBetaApisHint(player);
      return;
    }
    welcomePlayer(player);
  });
});
