"""pi-autoresearch-compatible confidence scoring (MAD noise floor)."""

from __future__ import annotations

from typing import Literal


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    mid = len(s) // 2
    if len(s) % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]


def compute_confidence(
    metrics: list[float],
    baseline: float | None,
    best_kept: float | None,
    direction: Literal["lower", "higher"] = "lower",
) -> float | None:
    """Return |best_delta| / MAD, or None if insufficient data."""
    positive = [m for m in metrics if m > 0]
    if len(positive) < 3 or baseline is None or best_kept is None:
        return None

    med = median(positive)
    mad = median([abs(v - med) for v in positive])
    if mad == 0:
        return None

    if direction == "lower":
        delta = baseline - best_kept
    else:
        delta = best_kept - baseline
    return abs(delta) / mad


def confidence_label(score: float | None) -> str:
    if score is None:
        return "—"
    if score >= 2.0:
        return f"{score:.1f}× (likely real)"
    if score >= 1.0:
        return f"{score:.1f}× (marginal)"
    return f"{score:.1f}× (within noise)"
