from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time import utc_now


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    workers: Mapped[int] = mapped_column(Integer, default=12)
    robots: Mapped[int] = mapped_column(Integer, default=6)
    orders_per_hour: Mapped[float] = mapped_column(Float, default=140.0)
    storage_zones: Mapped[int] = mapped_column(Integer, default=5)
    average_picking_time: Mapped[float] = mapped_column(Float, default=4.0)
    priority_order_percentage: Mapped[float] = mapped_column(Float, default=18.0)
    robot_failure_probability: Mapped[float] = mapped_column(Float, default=0.04)
    worker_efficiency: Mapped[float] = mapped_column(Float, default=0.88)
    shift_duration: Mapped[float] = mapped_column(Float, default=8.0)
    cost_per_worker: Mapped[float] = mapped_column(Float, default=24.0)
    cost_per_robot: Mapped[float] = mapped_column(Float, default=9.0)
    delay_penalty: Mapped[float] = mapped_column(Float, default=3.5)
    demand_variability: Mapped[float] = mapped_column(Float, default=0.2)
    inventory_restock_frequency: Mapped[float] = mapped_column(Float, default=2.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    user = relationship("User", back_populates="scenarios")
    simulation_runs = relationship("SimulationRun", back_populates="scenario", cascade="all, delete-orphan")

