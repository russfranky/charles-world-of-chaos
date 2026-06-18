#!/usr/bin/env python3
"""Summarize .auto/log.jsonl with pi-autoresearch-style MAD confidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from confidence import confidence_label, compute_confidence

LOG_PATH = REPO_ROOT / ".auto" / "log.jsonl"


def load_entries() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    out = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def main() -> int:
    entries = load_entries()
    if not entries:
        print("No .auto/log.jsonl — run ./.auto/measure.sh then log_experiment.py")
        return 0

    config = next((e for e in entries if e.get("type") == "config"), {})
    name = config.get("name", "session")
    metric_name = config.get("metricName", "metric")
    direction = config.get("bestDirection", "lower")

    runs = [e for e in entries if "run" in e and e.get("type") != "hook"]
    if not runs:
        print("No runs in log yet.")
        return 0

    baseline = None
    for e in runs:
        if e.get("run") == 1:
            baseline = float(e["metric"])
            break
    if baseline is None:
        baseline = float(runs[0]["metric"])

    best = None
    for e in runs:
        if e.get("status") != "keep":
            continue
        m = float(e["metric"])
        if best is None or (direction == "lower" and m < best) or (direction == "higher" and m > best):
            best = m

    metrics = [float(e["metric"]) for e in runs if float(e.get("metric", 0)) > 0]
    conf = compute_confidence(metrics, baseline, best, direction)

    best_str = f"{best:.2f}" if best is not None else "—"
    print(f"Autoresearch: {name}")
    print(f"Primary: {metric_name} ({direction} is better)")
    print(f"Baseline: {baseline:.2f}  Best kept: {best_str}  Confidence: {confidence_label(conf)}")
    print()
    print(f"{'Run':>4}  {'Status':<14}  {'Metric':>10}  {'Conf':>6}  Description")
    print("-" * 72)
    for e in runs:
        c = e.get("confidence")
        cstr = f"{c:.1f}×" if isinstance(c, (int, float)) and c is not None else "—"
        print(
            f"{e.get('run', '?'):>4}  {e.get('status', '?'):<14}  "
            f"{float(e.get('metric', 0)):>10.2f}  {cstr:>6}  {e.get('description', '')[:40]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
