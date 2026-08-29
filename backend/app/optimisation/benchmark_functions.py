from collections.abc import Callable
from typing import Dict, Tuple

import numpy as np

Objective = Callable[[np.ndarray], float]
Gradient = Callable[[np.ndarray], np.ndarray]


def sphere(x: np.ndarray) -> float:
    return float(np.sum(x**2))


def sphere_grad(x: np.ndarray) -> np.ndarray:
    return 2 * x


def rosenbrock(x: np.ndarray) -> float:
    return float(np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))


def rosenbrock_grad(x: np.ndarray) -> np.ndarray:
    grad = np.zeros_like(x)
    grad[:-1] += -400 * x[:-1] * (x[1:] - x[:-1] ** 2) - 2 * (1 - x[:-1])
    grad[1:] += 200 * (x[1:] - x[:-1] ** 2)
    return grad


def rastrigin(x: np.ndarray) -> float:
    return float(10 * len(x) + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))


def rastrigin_grad(x: np.ndarray) -> np.ndarray:
    return 2 * x + 20 * np.pi * np.sin(2 * np.pi * x)


FUNCTIONS: Dict[str, Tuple[Objective, Gradient]] = {
    "sphere": (sphere, sphere_grad),
    "rosenbrock": (rosenbrock, rosenbrock_grad),
    "rastrigin": (rastrigin, rastrigin_grad),
}


def get_benchmark(name: str) -> Tuple[Objective, Gradient]:
    key = name.lower().strip()
    if key not in FUNCTIONS:
        raise ValueError(f"Unknown benchmark function: {name}")
    return FUNCTIONS[key]

