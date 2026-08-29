from __future__ import annotations

import time
from typing import Dict, List

import numpy as np

from app.optimisation.benchmark_functions import get_benchmark
from app.optimisation.fractional_optimizer import memory_weighted_gradient
from app.optimisation.stability import calculate_curve_metrics


ALIASES = {
    "gd": "Gradient Descent",
    "gradient descent": "Gradient Descent",
    "sgd": "SGD",
    "adam": "Adam",
    "fractional gd": "Fractional GD",
    "fractional gradient descent": "Fractional GD",
    "fractional-order optimiser": "Fractional GD",
}


def normalise_optimiser(name: str) -> str:
    return ALIASES.get(name.lower().strip(), name)


def run_optimizer(
    function_name: str,
    optimiser_name: str,
    learning_rate: float,
    iterations: int,
    alpha: float = 0.7,
    seed: int | None = 42,
    dimension: int = 2,
) -> Dict[str, object]:
    objective, gradient = get_benchmark(function_name)
    optimiser = normalise_optimiser(optimiser_name)
    rng = np.random.default_rng((seed or 0) + sum(ord(c) for c in optimiser))
    x = rng.normal(loc=2.5, scale=1.0, size=dimension)
    m = np.zeros_like(x)
    v = np.zeros_like(x)
    beta1, beta2 = 0.9, 0.999
    eps = 1e-8
    history: List[np.ndarray] = []
    curve: List[float] = []
    started = time.perf_counter()

    for step in range(1, iterations + 1):
        loss = objective(x)
        curve.append(float(loss))
        if not np.isfinite(loss) or loss > 1e12:
            curve.extend([float("inf")] * (iterations - step))
            break

        grad = gradient(x)
        grad = np.clip(grad, -1e4, 1e4)
        if optimiser == "Gradient Descent":
            update = grad
        elif optimiser == "SGD":
            update = grad + rng.normal(0, 0.08 * (np.linalg.norm(grad) + 1), size=grad.shape)
        elif optimiser == "Adam":
            m = beta1 * m + (1 - beta1) * grad
            v = beta2 * v + (1 - beta2) * (grad**2)
            m_hat = m / (1 - beta1**step)
            v_hat = v / (1 - beta2**step)
            update = m_hat / (np.sqrt(v_hat) + eps)
        elif optimiser == "Fractional GD":
            history.append(grad.copy())
            history = history[-80:]
            update = memory_weighted_gradient(history, alpha)
        else:
            raise ValueError(f"Unknown optimiser: {optimiser_name}")
        x = x - learning_rate * update
        x = np.clip(x, -1e6, 1e6)

    runtime = time.perf_counter() - started
    metrics = calculate_curve_metrics(curve)
    metrics["runtime"] = round(runtime, 5)
    return {
        "optimiser": optimiser,
        "curve": [float(v) if np.isfinite(v) else 1e12 for v in curve],
        "final_position": [round(float(v), 6) for v in x],
        "metrics": metrics,
    }

