from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SimulationRunRequest(BaseModel):
    scenario_id: int
    strategy_name: str = "Hybrid Heuristic Strategy"
    seed: Optional[int] = 42


class StrategyCompareRequest(BaseModel):
    scenario_id: int
    seed: Optional[int] = 42


class SimulationMetrics(BaseModel):
    total_orders: int
    completed_orders: int
    delayed_orders: int
    average_completion_time: float
    average_queue_length: float
    worker_utilisation: float
    robot_utilisation: float
    throughput_per_hour: float
    cost_per_order: float
    total_cost: float
    efficiency_score: float
    bottleneck_zone: str
    delay_reduction_vs_baseline: float = 0.0


class SimulationRunRead(SimulationMetrics):
    id: int
    user_id: int
    scenario_id: int
    strategy_name: str
    metrics: Dict[str, Any]
    time_series: List[Dict[str, Any]]
    created_at: datetime


class StrategyComparisonResponse(BaseModel):
    scenario_id: int
    best_strategy: str
    results: List[SimulationRunRead]


class WhatIfRequest(BaseModel):
    base_scenario_id: int
    strategy_name: str = "Hybrid Heuristic Strategy"
    modified_parameters: Dict[str, Any] = Field(default_factory=dict)
    seed: Optional[int] = 42


class WhatIfRead(BaseModel):
    id: int
    user_id: int
    base_scenario_id: int
    modified_parameters: Dict[str, Any]
    baseline_metrics: Dict[str, Any]
    new_metrics: Dict[str, Any]
    percentage_changes: Dict[str, float]
    recommendation: str
    created_at: datetime

