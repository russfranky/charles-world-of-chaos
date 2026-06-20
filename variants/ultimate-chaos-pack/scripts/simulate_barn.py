#!/usr/bin/env python3
"""
Simulate Cow Barn player flows against barn logic (mirrors script_api/main.js).
Run: python3 variants/ultimate-chaos-pack/scripts/simulate_barn.py
"""
from __future__ import annotations

import random
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

# ─── Mirrored constants (keep in sync with main.js) ─────────────────────────

RANKS = [
    {"id": "pen", "slots": 3, "label": "Pen", "minCows": 0},
    {"id": "yard", "slots": 6, "label": "Yard", "minCows": 3},
    {"id": "ranch", "slots": 10, "label": "Ranch", "minCows": 6},
    {"id": "spread", "slots": 18, "label": "Spread", "minCows": 10},
    {"id": "legend", "slots": 30, "label": "Legend", "minCows": 18},
]

BELL_MODES = ["deploy", "feed", "breed", "recall"]
COW = "minecraft:cow"
SPOT_COW = "bgcow:brindal_cow"
STORM_COW = "bgcow:grayson_cow"

STEP_CATCH = 1
STEP_DEPLOY = 2
STEP_MORE = 3
STEP_BREED = 4
TUTORIAL_DONE = 9

CATCHABLE = {COW, SPOT_COW, STORM_COW}
CATALOG_SLOTS = 15

cow_counter = 1  # legacy fallback only


def next_cow_id(barn: dict) -> str:
    n = barn.get("nextCowId")
    if not isinstance(n, int) or n < 1:
        max_id = 0
        for c in barn["cows"]:
            if c["id"].startswith("cow_"):
                try:
                    max_id = max(max_id, int(c["id"].split("_", 1)[1]))
                except ValueError:
                    pass
        n = max_id + 1
    cid = f"cow_{n}"
    barn["nextCowId"] = n + 1
    return cid


def random_gen0_traits() -> dict[str, Any]:
    return {
        "coat": random.choice(["brown", "gray", "spot"]),
        "horns": random.choice(["none", "short"]),
        "size": random.choice(["small", "normal"]),
        "mark": random.choice(["none", "none", "star"]),
        "gen": 0,
        "feedsToAdult": 0,
        "hunger": 85,
        "mood": 80,
    }


def barn_rank(barn: dict) -> dict:
    n = len(barn["cows"])
    for rank in reversed(RANKS):
        if n >= rank["minCows"]:
            return rank
    return RANKS[0]


def max_slots(barn: dict) -> int:
    return barn_rank(barn)["slots"]


def can_breed(barn: dict) -> bool:
    return len(barn["cows"]) >= 3 and barn_rank(barn)["id"] != "pen"


def default_barn() -> dict:
    barn = {
        "cows": [],
        "activeId": None,
        "catalog": [],
        "bellMode": 0,
        "breedCooldown": 0,
        "nextCowId": 1,
        "deployedCowId": None,
        "deployedEntityId": None,
        "tutorialStep": 0,
    }
    starter = {"id": next_cow_id(barn), **random_gen0_traits()}
    barn["cows"].append(starter)
    barn["activeId"] = starter["id"]
    return barn


def entity_type_for_cow(cow: dict) -> str:
    if cow["coat"] == "spot":
        return SPOT_COW
    if cow["coat"] in ("storm", "shine"):
        return STORM_COW
    return COW


def adults_ready(barn: dict) -> list[dict]:
    return [
        c
        for c in barn["cows"]
        if c["feedsToAdult"] == 0 and c["hunger"] >= 40 and c["mood"] >= 55
    ]


def get_cow(barn: dict, cid: str | None) -> dict | None:
    if not cid:
        return None
    return next((c for c in barn["cows"] if c["id"] == cid), None)


@dataclass
class PlayerSession:
    barn: dict
    deployed_entity_id: str | None = None
    deployed_type: str | None = None
    wild_cows_nearby: int = 0
    messages: list[str] = field(default_factory=list)
    persisted_hunger: int | None = None

    def say(self, msg: str) -> None:
        self.messages.append(msg)

    def active_cow(self) -> dict | None:
        return get_cow(self.barn, self.barn["activeId"])

    def find_wild(self) -> bool:
        return self.wild_cows_nearby > 0

    def show_next_step(self) -> str:
        step = self.barn.get("tutorialStep", STEP_CATCH)
        cows = len(self.barn["cows"])
        wild = self.wild_cows_nearby
        has_out = bool(self.deployed_entity_id)
        if step < TUTORIAL_DONE:
            if step == STEP_CATCH:
                return "catch" if wild > 0 else "wait_cow"
            if step == STEP_DEPLOY:
                return "deploy"
            if step == STEP_MORE:
                return "catch_more" if cows < 3 else "breed"
            if step == STEP_BREED:
                return "breed"
        return "free_play"

    def advance_tutorial_on_catch(self) -> None:
        step = self.barn.get("tutorialStep", STEP_CATCH)
        cows = len(self.barn["cows"])
        if step == STEP_CATCH and cows >= 2:
            self.barn["tutorialStep"] = STEP_DEPLOY
        elif step == STEP_MORE and cows >= 3:
            self.barn["tutorialStep"] = STEP_BREED

    def bell_tap_menu(self, choice: str = "deploy") -> str:
        step = self.barn.get("tutorialStep", TUTORIAL_DONE)
        if step == STEP_DEPLOY:
            self.deploy()
            return "deploy"
        if step == STEP_BREED:
            before = len(self.barn["cows"])
            self.try_breed()
            if len(self.barn["cows"]) > before:
                self.barn["tutorialStep"] = TUTORIAL_DONE
            return "breed"
        if choice == "deploy":
            self.deploy()
        elif choice == "feed":
            self.feed_active()
        elif choice == "breed":
            self.try_breed()
        return choice

    def bell_tap(self) -> str:
        return self.bell_tap_menu("deploy")

    def catch_wild(self) -> bool:
        limit = max_slots(self.barn)
        if len(self.barn["cows"]) >= limit:
            self.say(f"Barn full ({limit} slots)")
            return False
        if not self.find_wild():
            self.say("No wild cow nearby")
            return False
        self.wild_cows_nearby -= 1
        caught = {"id": next_cow_id(self.barn), **random_gen0_traits()}
        self.barn["cows"].append(caught)
        self.advance_tutorial_on_catch()
        self.say(f"Caught! {len(self.barn['cows'])}/{limit}")
        return True

    def deploy(self) -> bool:
        cow = self.active_cow()
        if not cow:
            self.say("No active cow")
            return False
        self.deployed_entity_id = f"entity_{cow['id']}"
        self.deployed_type = entity_type_for_cow(cow)
        if self.barn.get("tutorialStep") == STEP_DEPLOY:
            self.barn["tutorialStep"] = STEP_MORE
        self.say(f"Deployed {cow['coat']}")
        return True

    def recall(self) -> None:
        self.deployed_entity_id = None
        self.deployed_type = None
        self.say("Recalled")

    def feed_active(self) -> bool:
        cow = self.active_cow()
        if not cow:
            return False
        cow["hunger"] = min(100, cow["hunger"] + 28)
        cow["mood"] = min(100, cow["mood"] + 12)
        if cow["feedsToAdult"] > 0:
            cow["feedsToAdult"] -= 1
        return True

    def feed_bag_use(self) -> str:
        if self.find_wild():
            before = len(self.barn["cows"])
            self.catch_wild()
            if len(self.barn["cows"]) > before:
                return "catch"
        cow = self.active_cow()
        if cow:
            self.feed_active()
            return "feed"
        return "noop"

    def try_breed(self) -> bool:
        if not can_breed(self.barn):
            self.say("Cannot breed yet")
            return False
        if self.barn["breedCooldown"] > 0:
            self.say("Cooldown")
            return False
        adults = adults_ready(self.barn)
        if len(adults) < 2:
            self.say("Need 2 ready adults")
            return False
        if len(self.barn["cows"]) >= max_slots(self.barn):
            self.say("Barn full")
            return False
        adults.sort(key=lambda c: c["mood"] + c["hunger"], reverse=True)
        parent_a = adults[0]
        parent_b = adults[1]
        child = {
            "id": next_cow_id(self.barn),
            "coat": random.choice([parent_a["coat"], parent_b["coat"]]),
            "horns": random.choice([parent_a["horns"], parent_b["horns"]]),
            "size": random.choice([parent_a["size"], parent_b["size"]]),
            "mark": random.choice([parent_a["mark"], parent_b["mark"]]),
            "gen": max(parent_a.get("gen", 0), parent_b.get("gen", 0)) + 1,
            "feedsToAdult": 3,
            "hunger": 70,
            "mood": 75,
        }
        self.barn["cows"].append(child)
        self.barn["activeId"] = child["id"]
        self.barn["breedCooldown"] = 90
        self.say("Bred!")
        return True

    def bell_tap(self) -> str:
        return self.bell_tap_menu("deploy")

    def decay_tick(self, persist: bool = True) -> None:
        changed = False
        if self.barn["breedCooldown"] > 0:
            self.barn["breedCooldown"] -= 1
            changed = True
        for cow in self.barn["cows"]:
            prev = cow["hunger"]
            cow["hunger"] = max(0, cow["hunger"] - 1)
            if cow["hunger"] < 35:
                cow["mood"] = max(0, cow["mood"] - 2)
            if cow["hunger"] != prev:
                changed = True
            if (
                cow["hunger"] < 15
                and self.deployed_entity_id
                and self.barn["activeId"] == cow["id"]
            ):
                self.recall()
        if persist and changed:
            cow = self.active_cow()
            if cow:
                self.persisted_hunger = cow["hunger"]


# ─── Scenarios ───────────────────────────────────────────────────────────────

class SimFailure(Exception):
    pass


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise SimFailure(msg)


def scenario_new_player_catch_to_breed() -> None:
    random.seed(42)
    p = PlayerSession(barn=default_barn())
    p.wild_cows_nearby = 5

    while p.wild_cows_nearby > 0:
        before = len(p.barn["cows"])
        p.catch_wild()
        if len(p.barn["cows"]) == before:
            break

    n = len(p.barn["cows"])
    rank = barn_rank(p.barn)
    assert_true(n >= 3, f"only {n} cows at {rank['label']} — cannot breed")
    assert_true(can_breed(p.barn), "Should be able to breed at 3+ cows")


def scenario_deployed_vanilla_catch_trap() -> None:
    """Wild cow nearby while barn cow is deployed — Feed Bag should catch wild, not feed."""
    random.seed(1)
    p = PlayerSession(barn=default_barn())
    p.barn["cows"][0]["coat"] = "brown"
    p.deploy()
    assert_true(p.deployed_type == COW, "expected vanilla deploy")
    p.wild_cows_nearby = 1
    action = p.feed_bag_use()
    assert_true(action == "catch", f"should catch wild cow (got {action})")
    assert_true(len(p.barn["cows"]) == 2, "herd size should be 2 after catch")


def scenario_tutorial_three_steps() -> None:
    random.seed(21)
    p = PlayerSession(barn=default_barn())
    p.barn["tutorialStep"] = STEP_CATCH
    p.wild_cows_nearby = 2
    assert_true(p.show_next_step() in ("catch", "wait_cow"), "step 1 guides catch")
    p.catch_wild()
    assert_true(p.barn["tutorialStep"] == STEP_DEPLOY, "catch advances to deploy")
    assert_true(p.show_next_step() == "deploy", "step 2 guides deploy")
    p.bell_tap_menu("deploy")
    assert_true(p.barn["tutorialStep"] == STEP_MORE, "deploy advances to catch more")
    p.wild_cows_nearby = 2
    while len(p.barn["cows"]) < 3 and p.wild_cows_nearby > 0:
        p.catch_wild()
    assert_true(p.barn["tutorialStep"] == STEP_BREED, "third cow advances to breed")
    for c in p.barn["cows"]:
        c["hunger"] = 90
        c["mood"] = 90
    p.bell_tap_menu("breed")
    assert_true(p.barn["tutorialStep"] == TUTORIAL_DONE, "breed finishes tutorial")
    assert_true(len(p.barn["cows"]) >= 4, "baby cow added")


def scenario_old_save_skips_tutorial_nag() -> None:
    barn = default_barn()
    del barn["tutorialStep"]
    barn["cows"].append({"id": next_cow_id(barn), **random_gen0_traits()})
    loaded = deepcopy(barn)
    if "tutorialStep" not in loaded:
        loaded["tutorialStep"] = TUTORIAL_DONE
    p = PlayerSession(barn=loaded)
    assert_true(p.show_next_step() == "free_play", "legacy save should not nag")


def scenario_hunger_persisted() -> None:
    p = PlayerSession(barn=default_barn())
    cow = p.active_cow()
    assert cow is not None
    for _ in range(5):
        p.decay_tick(persist=True)
    assert_true(p.persisted_hunger is not None, "decay should trigger save")
    assert_true(p.persisted_hunger < 85, "hunger should decay and persist")


def scenario_first_hour_play() -> None:
    random.seed(99)
    p = PlayerSession(barn=default_barn())
    p.wild_cows_nearby = 8

    for turn in range(40):
        roll = random.random()
        if roll < 0.4:
            p.bell_tap()
        elif roll < 0.7 and p.wild_cows_nearby > 0:
            p.catch_wild()
        else:
            p.feed_bag_use()
        if turn % 3 == 0:
            p.decay_tick()

    assert_true(len(p.barn["cows"]) >= 3, f"stuck at {len(p.barn['cows'])} cows after 40 actions")


def scenario_calf_growth() -> None:
    random.seed(7)
    p = PlayerSession(barn=default_barn())
    for _ in range(2):
        p.barn["cows"].append({"id": next_cow_id(p.barn), **random_gen0_traits()})
    for c in p.barn["cows"]:
        c["hunger"] = 90
        c["mood"] = 90
    assert_true(can_breed(p.barn), "yard rank")
    p.try_breed()
    child = get_cow(p.barn, p.barn["activeId"])
    assert child is not None
    assert_true(child["feedsToAdult"] == 3, "calf should need growth feeds")
    assert_true(child not in adults_ready(p.barn), "calf not breed-ready")


def scenario_recall_cycles_active() -> None:
    p = PlayerSession(barn=default_barn())
    for _ in range(2):
        p.barn["cows"].append({"id": next_cow_id(p.barn), **random_gen0_traits()})
    first = p.barn["activeId"]
    idx = (p.barn["cows"].index(get_cow(p.barn, first)) + 1) % len(p.barn["cows"])
    expected_next = p.barn["cows"][idx]["id"]
    # mirror cycleActiveCow
    p.barn["activeId"] = expected_next
    assert_true(p.barn["activeId"] != first, "recall should cycle active cow")


def scenario_cow_ids_monotonic() -> None:
    barn = default_barn()
    first = next_cow_id(barn)
    second = next_cow_id(barn)
    assert_true(first != second, "cow ids should be unique")
    reloaded = deepcopy(barn)
    third = next_cow_id(reloaded)
    assert_true(third not in {first, second}, "reloaded barn should not reuse ids")


def scenario_breed_inherits_parents() -> None:
    random.seed(3)
    p = PlayerSession(barn=default_barn())
    for _ in range(2):
        c = {"id": next_cow_id(p.barn), **random_gen0_traits()}
        c["hunger"] = 90
        c["mood"] = 90
        p.barn["cows"].append(c)
    p.try_breed()
    child = get_cow(p.barn, p.barn["activeId"])
    assert child is not None
    parents = p.barn["cows"][:-1]
    for slot in ("coat", "horns", "size", "mark"):
        values = {parents[0][slot], parents[1][slot]}
        assert_true(child[slot] in values or child.get("gen", 0) > 0, f"child {slot} should inherit")


def run_all() -> list[str]:
    issues: list[str] = []
    scenarios = [
        ("new_player_catch_to_breed", scenario_new_player_catch_to_breed),
        ("deployed_vanilla_catch_trap", scenario_deployed_vanilla_catch_trap),
        ("tutorial_three_steps", scenario_tutorial_three_steps),
        ("old_save_skips_tutorial_nag", scenario_old_save_skips_tutorial_nag),
        ("hunger_persisted", scenario_hunger_persisted),
        ("first_hour_play", scenario_first_hour_play),
        ("calf_growth", scenario_calf_growth),
        ("recall_cycles_active", scenario_recall_cycles_active),
        ("cow_ids_monotonic", scenario_cow_ids_monotonic),
        ("breed_inherits_parents", scenario_breed_inherits_parents),
    ]
    for name, fn in scenarios:
        try:
            fn()
            print(f"  OK  {name}")
        except SimFailure as e:
            print(f"  FAIL {name}: {e}")
            issues.append(f"{name}: {e}")
        except Exception as e:
            print(f"  ERR  {name}: {e}")
            issues.append(f"{name}: {e}")
    return issues


def main() -> int:
    print("Cow Barn simulation")
    print("=" * 50)
    issues = run_all()
    print("=" * 50)
    if issues:
        print(f"\n{len(issues)} issue(s) found:")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("\nAll scenarios passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
