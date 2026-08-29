from __future__ import annotations

from typing import List

import numpy as np


def memory_weighted_gradient(history: List[np.ndarray], alpha: float) -> np.ndarray:
    """Experimental fractional-inspired memory kernel over past gradients.

    This is intentionally labelled "fractional-inspired": lower alpha gives older
    gradients more influence, while alpha close to 1 behaves closer to standard GD.
    """
    if not history:
        raise ValueError("Gradient history cannot be empty")
    alpha = float(np.clip(alpha, 0.1, 1.0))
    age = np.arange(len(history), 0, -1, dtype=float)
    weights = age ** (-alpha)
    weights = weights / np.sum(weights)
    stacked = np.vstack(history)
    return np.sum(stacked * weights[:, None], axis=0)

