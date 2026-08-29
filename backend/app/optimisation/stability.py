from __future__ import annotations

from typing import Dict, List

import numpy as np


def calculate_curve_metrics(curve: List[float], threshold: float = 1e-3) -> Dict[str, float | int | bool]:
    values = np.asarray(curve, dtype=float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return {
            "final_loss": float("inf"),
            "best_loss": float("inf"),
            "iterations_to_threshold": -1,
            "average_improvement": 0.0,
            "convergence_speed": 0.0,
            "loss_variance_final_window": float("inf"),
            "oscillation_score": 1.0,
            "smoothness_score": 0.0,
            "stability_score": 0.0,
            "divergence_flag": True,
        }

    deltas = np.diff(finite)
    sign_changes = np.sum(np.diff(np.sign(deltas)) != 0) if deltas.size > 1 else 0
    oscillation = float(sign_changes / max(len(deltas) - 1, 1))
    second_diff = np.diff(finite, n=2)
    smoothness = float(1 / (1 + np.std(second_diff))) if second_diff.size else 1.0
    final_window = finite[-min(25, len(finite)) :]
    variance = float(np.var(final_window))
    best = float(np.min(finite))
    final = float(finite[-1])
    threshold_hits = np.where(finite <= threshold)[0]
    iterations_to_threshold = int(threshold_hits[0]) if threshold_hits.size else -1
    improvement = float((finite[0] - best) / max(len(finite), 1))
    convergence_speed = float((finite[0] - final) / max(len(finite), 1))
    divergence = bool(not np.isfinite(values[-1]) or final > finite[0] * 10 or final > 1e8)
    stability_score = 100 * (0.45 * (1 - min(oscillation, 1)) + 0.35 * min(smoothness, 1) + 0.2 * (0 if divergence else 1))

    return {
        "final_loss": round(final, 8),
        "best_loss": round(best, 8),
        "iterations_to_threshold": iterations_to_threshold,
        "average_improvement": round(improvement, 8),
        "convergence_speed": round(convergence_speed, 8),
        "loss_variance_final_window": round(variance, 8),
        "oscillation_score": round(oscillation, 4),
        "smoothness_score": round(smoothness, 4),
        "stability_score": round(float(stability_score), 2),
        "divergence_flag": divergence,
    }


def rank_convergence(curves: Dict[str, List[float]]) -> List[Dict[str, float | str]]:
    rows = []
    for name, curve in curves.items():
        metrics = calculate_curve_metrics(curve)
        rows.append({"optimiser": name, "best_loss": metrics["best_loss"], "stability_score": metrics["stability_score"]})
    return sorted(rows, key=lambda row: (float(row["best_loss"]), -float(row["stability_score"])))

