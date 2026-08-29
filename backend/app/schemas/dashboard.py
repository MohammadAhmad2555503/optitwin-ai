from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_scenarios: int
    total_simulation_runs: int
    best_strategy: Optional[str]
    average_delay_reduction: float
    average_throughput_improvement: float
    total_optimiser_experiments: int
    total_rl_runs: int
    total_reports: int


class ActivityRead(BaseModel):
    id: int
    activity_type: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RecentActivityResponse(BaseModel):
    activities: List[ActivityRead]

