from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    title: str = "OptiTwinAI Decision Support Report"
    scenario_id: Optional[int] = None
    simulation_run_id: Optional[int] = None
    optimisation_experiment_id: Optional[int] = None
    rl_run_id: Optional[int] = None


class ReportRead(BaseModel):
    id: int
    user_id: int
    title: str
    report_markdown: str
    created_at: datetime

    model_config = {"from_attributes": True}

