from typing import Any, Dict, List

from app.optimisation.stability import calculate_curve_metrics, rank_convergence


def analyse_convergence(curves: Dict[str, List[float]], threshold: float = 1e-3) -> Dict[str, Any]:
    metrics = {name: calculate_curve_metrics(curve, threshold) for name, curve in curves.items()}
    ranking = rank_convergence(curves)
    return {"metrics": metrics, "ranking": ranking}


def analyse_stability(
    curves: Dict[str, List[float]],
    learning_rates: List[float] | None = None,
    alphas: List[float] | None = None,
) -> Dict[str, Any]:
    metrics = {name: calculate_curve_metrics(curve) for name, curve in curves.items()}
    sensitivity = {
        "learning_rates": learning_rates or [0.005, 0.01, 0.02, 0.05],
        "alphas": alphas or [0.3, 0.5, 0.7, 0.9],
        "interpretation": "Higher stability score means lower oscillation, smoother tail behaviour, and no divergence flag.",
    }
    return {"metrics": metrics, "sensitivity": sensitivity}

