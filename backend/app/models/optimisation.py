from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.time import utc_now


class OptimisationExperiment(Base):
    __tablename__ = "optimisation_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    function_name: Mapped[str] = mapped_column(String(80), nullable=False)
    optimisers_json: Mapped[str] = mapped_column(Text, default="[]")
    learning_rate: Mapped[float] = mapped_column(Float, default=0.01)
    iterations: Mapped[int] = mapped_column(Integer, default=250)
    alpha: Mapped[float] = mapped_column(Float, default=0.7)
    results_json: Mapped[str] = mapped_column(Text, default="{}")
    convergence_curves_json: Mapped[str] = mapped_column(Text, default="{}")
    stability_metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

