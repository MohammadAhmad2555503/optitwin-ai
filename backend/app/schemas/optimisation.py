from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OptimisationRunRequest(BaseModel):
    function_name: str = "sphere"
    optimisers: List[str] = Field(default_factory=lambda: ["Gradient Descent", "SGD", "Adam", "Fractional GD"])
    learning_rate: float = Field(default=0.02, gt=0, le=1)
    iterations: int = Field(default=250, ge=10, le=5000)
    alpha: float = Field(default=0.7, ge=0.1, le=1.0)
    seed: Optional[int] = 42


class OptimisationExperimentRead(BaseModel):
    id: int
    user_id: int
    function_name: str
    optimisers: List[str]
    learning_rate: float
    iterations: int
    alpha: float
    results: Dict[str, Any]
    convergence_curves: Dict[str, List[float]]
    stability_metrics: Dict[str, Any]
    created_at: datetime


class OptimisationCompareRequest(OptimisationRunRequest):
    """Compare optimisers without requiring a persisted experiment."""


class AlphaSensitivityRequest(BaseModel):
    function_name: str = "rosenbrock"
    learning_rate: float = Field(default=0.01, gt=0, le=1)
    iterations: int = Field(default=200, ge=10, le=3000)
    alphas: List[float] = Field(default_factory=lambda: [0.3, 0.5, 0.7, 0.9])
    seed: Optional[int] = 42


class ConvergenceAnalysisRequest(BaseModel):
    curves: Dict[str, List[float]]
    threshold: float = 1e-3


class StabilityAnalysisRequest(BaseModel):
    curves: Dict[str, List[float]]
    learning_rates: Optional[List[float]] = None
    alphas: Optional[List[float]] = None

