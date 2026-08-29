from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.time import utc_now


class RLTrainingRun(Base):
    __tablename__ = "rl_training_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"), nullable=False, index=True)
    algorithm: Mapped[str] = mapped_column(String(80), default="TabularQAgent")
    episodes: Mapped[int] = mapped_column(Integer, default=80)
    reward_function_json: Mapped[str] = mapped_column(Text, default="{}")
    training_metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    reward_curve_json: Mapped[str] = mapped_column(Text, default="[]")
    comparison_metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(40), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

