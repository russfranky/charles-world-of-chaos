#!/usr/bin/env python3
"""Append pi-autoresearch-compatible entries to .auto/log.jsonl."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from confidence import compute_confidence

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / ".auto" / "log.jsonl"
DIRECTION = "lower"


def git_short_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def load_lines() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    entries = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def write_config_if_missing(entries: list[dict]) -> None:
    if any(e.get("type") == "config" for e in entries):
        return
    config = {
        "type": "config",
        "name": "Brindal & Grayson Cow World",
        "metricName": "mcaddon_kb",
        "metricUnit": "kb",
        "bestDirection": DIRECTION,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(config) + "\n")


def next_run(entries: list[dict]) -> int:
    runs = [e["run"] for e in entries if "run" in e and e.get("type") != "hook"]
    return max(runs, default=0) + 1


def baseline_metric(entries: list[dict]) -> float | None:
    for e in entries:
        if e.get("type") == "hook":
            continue
        if e.get("run") == 1 and e.get("status") == "keep":
            return float(e["metric"])
    for e in entries:
        if e.get("type") == "hook":
            continue
        if "metric" in e:
            return float(e["metric"])
    return None


def best_kept_metric(entries: list[dict], direction: str) -> float | None:
    best = None
    for e in entries:
        if e.get("type") == "hook" or e.get("status") != "keep":
            continue
        m = float(e["metric"])
        if best is None:
            best = m
        elif direction == "lower" and m < best:
            best = m
        elif direction == "higher" and m > best:
            best = m
    return best


def all_metrics(entries: list[dict]) -> list[float]:
    return [
        float(e["metric"])
        for e in entries
        if e.get("type") != "hook" and "metric" in e and float(e["metric"]) > 0
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Log an autoresearch experiment result")
    parser.add_argument("--metric", type=float, required=True, help="Primary metric (mcaddon_kb)")
    parser.add_argument("--status", choices=["keep", "discard", "crash", "checks_failed"], required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--metrics", default="{}", help="JSON dict of secondary metrics")
    parser.add_argument("--asi", default="{}", help="JSON dict of agent signal (hypothesis, learned, ...)")
    args = parser.parse_args()

    secondary = json.loads(args.metrics)
    asi = json.loads(args.asi)
    entries = load_lines()
    write_config_if_missing(entries)
    entries = load_lines()

    run = next_run(entries)
    base = baseline_metric(entries)
    metrics_list = all_metrics(entries) + [args.metric]
    best = best_kept_metric(entries, DIRECTION)
    if args.status == "keep":
        if best is None or args.metric < best:
            best = args.metric

    conf = compute_confidence(metrics_list, base, best, DIRECTION)

    entry = {
        "run": run,
        "commit": git_short_commit(),
        "metric": args.metric,
        "metrics": secondary,
        "status": args.status,
        "description": args.description,
        "timestamp": int(time.time()),
        "segment": 0,
        "confidence": conf,
    }
    if asi:
        entry["asi"] = asi

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    conf_str = f"{conf:.1f}×" if conf is not None else "—"
    print(f"Logged run {run} status={args.status} mcaddon_kb={args.metric} confidence={conf_str}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
