import json
from statistics import mean
from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity import ActivityLog
from app.models.optimisation import OptimisationExperiment
from app.models.report import Report
from app.models.rl import RLTrainingRun
from app.models.scenario import Scenario
from app.models.simulation import SimulationRun
from app.models.user import User


def _loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback


def summary(db: Session, user: User) -> Dict[str, Any]:
    total_scenarios = db.scalar(select(func.count()).select_from(Scenario).where(Scenario.user_id == user.id)) or 0
    total_runs = db.scalar(select(func.count()).select_from(SimulationRun).where(SimulationRun.user_id == user.id)) or 0
    total_experiments = db.scalar(select(func.count()).select_from(OptimisationExperiment).where(OptimisationExperiment.user_id == user.id)) or 0
    total_rl = db.scalar(select(func.count()).select_from(RLTrainingRun).where(RLTrainingRun.user_id == user.id)) or 0
    total_reports = db.scalar(select(func.count()).select_from(Report).where(Report.user_id == user.id)) or 0
    runs = list(db.scalars(select(SimulationRun).where(SimulationRun.user_id == user.id)))
    best_strategy = max(runs, key=lambda run: run.efficiency_score).strategy_name if runs else None
    delay_reductions = [_loads(run.metrics_json, {}).get("delay_reduction_vs_baseline", 0.0) for run in runs]
    throughput_gains = []
    for run in runs:
        if run.scenario and run.scenario.orders_per_hour:
            throughput_gains.append((run.throughput_per_hour - run.scenario.orders_per_hour) / run.scenario.orders_per_hour * 100)
    return {
        "total_scenarios": total_scenarios,
        "total_simulation_runs": total_runs,
        "best_strategy": best_strategy,
        "average_delay_reduction": round(mean(delay_reductions), 2) if delay_reductions else 0.0,
        "average_throughput_improvement": round(mean(throughput_gains), 2) if throughput_gains else 0.0,
        "total_optimiser_experiments": total_experiments,
        "total_rl_runs": total_rl,
        "total_reports": total_reports,
    }


def recent_activity(db: Session, user: User) -> Dict[str, Any]:
    activities = list(
        db.scalars(
            select(ActivityLog)
            .where(ActivityLog.user_id == user.id)
            .order_by(ActivityLog.created_at.desc())
            .limit(15)
        )
    )
    return {"activities": activities}

