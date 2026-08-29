from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RLTrainRequest(BaseModel):
    scenario_id: int
    algorithm: str = "TabularQAgent"
    episodes: int = Field(default=80, ge=5, le=1000)
    seed: Optional[int] = 42


class RLRunRead(BaseModel):
    id: int
    user_id: int
    scenario_id: int
    algorithm: str
    episodes: int
    reward_function: Dict[str, Any]
    training_metrics: Dict[str, Any]
    reward_curve: List[float]
    comparison_metrics: Dict[str, Any]
    status: str
    created_at: datetime


class RLEvaluateRequest(BaseModel):
    scenario_id: int
    run_id: Optional[int] = None
    episodes: int = Field(default=20, ge=1, le=300)
    seed: Optional[int] = 43

