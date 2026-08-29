from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScenarioBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    workers: int = Field(default=12, ge=1, le=500)
    robots: int = Field(default=6, ge=0, le=500)
    orders_per_hour: float = Field(default=140.0, ge=1, le=10000)
    storage_zones: int = Field(default=5, ge=1, le=100)
    average_picking_time: float = Field(default=4.0, ge=0.2, le=120)
    priority_order_percentage: float = Field(default=18.0, ge=0, le=100)
    robot_failure_probability: float = Field(default=0.04, ge=0, le=1)
    worker_efficiency: float = Field(default=0.88, ge=0.1, le=1.5)
    shift_duration: float = Field(default=8.0, ge=1, le=24)
    cost_per_worker: float = Field(default=24.0, ge=0)
    cost_per_robot: float = Field(default=9.0, ge=0)
    delay_penalty: float = Field(default=3.5, ge=0)
    demand_variability: float = Field(default=0.2, ge=0, le=2)
    inventory_restock_frequency: float = Field(default=2.0, ge=0.25, le=24)


class ScenarioCreate(ScenarioBase):
    """Create scenario payload."""


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    workers: Optional[int] = Field(default=None, ge=1, le=500)
    robots: Optional[int] = Field(default=None, ge=0, le=500)
    orders_per_hour: Optional[float] = Field(default=None, ge=1, le=10000)
    storage_zones: Optional[int] = Field(default=None, ge=1, le=100)
    average_picking_time: Optional[float] = Field(default=None, ge=0.2, le=120)
    priority_order_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    robot_failure_probability: Optional[float] = Field(default=None, ge=0, le=1)
    worker_efficiency: Optional[float] = Field(default=None, ge=0.1, le=1.5)
    shift_duration: Optional[float] = Field(default=None, ge=1, le=24)
    cost_per_worker: Optional[float] = Field(default=None, ge=0)
    cost_per_robot: Optional[float] = Field(default=None, ge=0)
    delay_penalty: Optional[float] = Field(default=None, ge=0)
    demand_variability: Optional[float] = Field(default=None, ge=0, le=2)
    inventory_restock_frequency: Optional[float] = Field(default=None, ge=0.25, le=24)


class ScenarioRead(ScenarioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

