from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time import utc_now


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"), nullable=False, index=True)
    strategy_name: Mapped[str] = mapped_column(String(120), nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0)
    delayed_orders: Mapped[int] = mapped_column(Integer, default=0)
    average_completion_time: Mapped[float] = mapped_column(Float, default=0.0)
    average_queue_length: Mapped[float] = mapped_column(Float, default=0.0)
    worker_utilisation: Mapped[float] = mapped_column(Float, default=0.0)
    robot_utilisation: Mapped[float] = mapped_column(Float, default=0.0)
    throughput_per_hour: Mapped[float] = mapped_column(Float, default=0.0)
    cost_per_order: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    efficiency_score: Mapped[float] = mapped_column(Float, default=0.0)
    bottleneck_zone: Mapped[str] = mapped_column(String(80), default="Zone A")
    metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    time_series_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    scenario = relationship("Scenario", back_populates="simulation_runs")


class WhatIfResult(Base):
    __tablename__ = "whatif_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    base_scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"), nullable=False, index=True)
    modified_parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    baseline_metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    new_metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    recommendation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

