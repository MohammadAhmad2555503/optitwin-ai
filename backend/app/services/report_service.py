import json
from typing import Any, Iterable

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.optimisation import OptimisationExperiment
from app.models.report import Report
from app.models.rl import RLTrainingRun
from app.models.scenario import Scenario
from app.models.simulation import SimulationRun, WhatIfResult
from app.models.user import User
from app.schemas.report import ReportGenerateRequest
from app.services.activity_service import log_activity


def _loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback


def _latest(db: Session, model: Any, user_id: int):
    return db.scalar(select(model).where(model.user_id == user_id).order_by(model.created_at.desc()))


def _selected_or_latest(db: Session, model: Any, user_id: int, selected_id: int | None, label: str):
    if selected_id is None:
        return _latest(db, model, user_id)
    item = db.get(model, selected_id)
    if item is None or item.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found")
    return item


def _metric_table(metrics: dict[str, Any]) -> str:
    rows = [
        ("Total orders", metrics.get("total_orders")),
        ("Completed orders", metrics.get("completed_orders")),
        ("Delayed orders", metrics.get("delayed_orders")),
        ("Throughput per hour", metrics.get("throughput_per_hour")),
        ("Cost per order", metrics.get("cost_per_order")),
        ("Efficiency score", metrics.get("efficiency_score")),
    ]
    return "\n".join([f"| {name} | {value} |" for name, value in rows])


def _optimiser_table(results: dict[str, Any]) -> str:
    lines = ["| Optimiser | Best loss | Final loss | Stability | Diverged |", "| --- | ---: | ---: | ---: | --- |"]
    for name, metrics in results.items():
        lines.append(
            f"| {name} | {metrics.get('best_loss')} | {metrics.get('final_loss')} | {metrics.get('stability_score')} | {metrics.get('divergence_flag')} |"
        )
    return "\n".join(lines)


def generate_report(db: Session, user: User, payload: ReportGenerateRequest) -> Report:
    scenario = _selected_or_latest(db, Scenario, user.id, payload.scenario_id, "Scenario")
    simulation = _selected_or_latest(db, SimulationRun, user.id, payload.simulation_run_id, "Simulation run")
    optimisation = _selected_or_latest(
        db,
        OptimisationExperiment,
        user.id,
        payload.optimisation_experiment_id,
        "Optimisation experiment",
    )
    rl_run = _selected_or_latest(db, RLTrainingRun, user.id, payload.rl_run_id, "RL run")
    whatif = _latest(db, WhatIfResult, user.id)

    markdown = build_markdown_report(payload.title, scenario, simulation, optimisation, rl_run, whatif)
    report = Report(user_id=user.id, title=payload.title, report_markdown=markdown)
    db.add(report)
    db.commit()
    db.refresh(report)
    log_activity(db, user.id, "report.generated", f"Generated report '{payload.title}'")
    return report


def build_markdown_report(
    title: str,
    scenario: Scenario | None,
    simulation: SimulationRun | None,
    optimisation: OptimisationExperiment | None,
    rl_run: RLTrainingRun | None,
    whatif: WhatIfResult | None,
) -> str:
    scenario_name = scenario.name if scenario else "No scenario selected"
    simulation_metrics = _loads(simulation.metrics_json, {}) if simulation else {}
    optimisation_results = _loads(optimisation.results_json, {}) if optimisation else {}
    rl_metrics = _loads(rl_run.training_metrics_json, {}) if rl_run else {}
    whatif_new = _loads(whatif.new_metrics_json, {}) if whatif else {}
    whatif_base = _loads(whatif.baseline_metrics_json, {}) if whatif else {}

    sections = [
        f"# {title}",
        "## Executive Summary",
        f"This report analyses the digital twin scenario **{scenario_name}** using stored OptiTwinAI simulations, optimisation experiments, and reinforcement-learning policy outputs.",
        "## Scenario Overview",
        _scenario_overview(scenario),
        "## Simulation Parameters",
        _simulation_parameters(scenario),
        "## Strategy Comparison",
        "| Metric | Value |\n| --- | ---: |\n" + (_metric_table(simulation_metrics) if simulation_metrics else "| No simulation stored | - |"),
        "## What-if Analysis",
        _whatif_summary(whatif_base, whatif_new, whatif.recommendation if whatif else ""),
        "## Optimisation Lab Results",
        _optimiser_table(optimisation_results) if optimisation_results else "No optimisation experiment has been stored yet.",
        "## Gradient Descent, SGD, Adam Comparison",
        "The optimisation lab stores comparable loss curves and final-loss metrics for Gradient Descent, noisy SGD-style updates, and Adam.",
        "## Fractional-Order Optimisation Analysis",
        "The Fractional GD entry uses an experimental fractional-inspired memory kernel. Lower alpha values increase gradient-history influence; alpha near 1 behaves closer to standard gradient descent.",
        "## Convergence Analysis",
        "Convergence is measured with final loss, best loss, threshold iterations, average improvement, and curve ranking.",
        "## Stability Analysis",
        "Stability combines final-window variance, oscillation score, smoothness score, and divergence flags.",
        "## Reinforcement Learning Results",
        _rl_summary(rl_metrics),
        "## Operational Recommendations",
        _recommendations(simulation_metrics, whatif_new, optimisation_results, rl_metrics),
        "## Limitations",
        "- The built-in RL trainer is a tabular Q-learning engine for local policy experiments; high-volume production deployment should validate policies against calibrated operational data.\n- The fractional optimiser is fractional-inspired and does not claim full fractional calculus formalism.\n- Simulation outputs are decision-support estimates until calibrated against a specific warehouse telemetry feed.",
        "## Future Work",
        "- Add Alembic migration files for managed schema evolution.\n- Connect real WMS/ERP event streams.\n- Add optional Gymnasium and Stable-Baselines3 policy backends for larger training jobs.\n- Add experiment versioning and batch calibration tools.",
        "## Appendix",
            "Report source: OptiTwinAI local SQLite data.",
    ]
    return "\n\n".join(sections)


def _scenario_overview(scenario: Scenario | None) -> str:
    if not scenario:
        return "No scenario was available."
    return (
        f"- Workers: {scenario.workers}\n- Robots: {scenario.robots}\n- Orders per hour: {scenario.orders_per_hour}\n"
        f"- Storage zones: {scenario.storage_zones}\n- Shift duration: {scenario.shift_duration} hours"
    )


def _simulation_parameters(scenario: Scenario | None) -> str:
    if not scenario:
        return "No parameters available."
    return (
        f"- Average picking time: {scenario.average_picking_time} min\n- Priority orders: {scenario.priority_order_percentage}%\n"
        f"- Robot failure probability: {scenario.robot_failure_probability}\n- Demand variability: {scenario.demand_variability}\n"
        f"- Restock frequency: every {scenario.inventory_restock_frequency} hours"
    )


def _whatif_summary(base: dict[str, Any], new: dict[str, Any], recommendation: str) -> str:
    if not base or not new:
        return "No what-if analysis has been stored yet."
    return (
        f"Baseline throughput was {base.get('throughput_per_hour')} orders/hour; modified throughput is {new.get('throughput_per_hour')} orders/hour.\n\n"
        f"Recommendation: {recommendation}"
    )


def _rl_summary(metrics: dict[str, Any]) -> str:
    if not metrics:
        return "No RL training run has been stored yet."
    return (
        f"- Average reward: {metrics.get('average_reward')}\n- Final reward: {metrics.get('final_reward')}\n"
        f"- Delay rate: {metrics.get('delay_rate')}\n- Throughput per hour: {metrics.get('throughput_per_hour')}"
    )


def _recommendations(
    simulation_metrics: dict[str, Any],
    whatif_new: dict[str, Any],
    optimisation_results: dict[str, Any],
    rl_metrics: dict[str, Any],
) -> str:
    recommendations = []
    if simulation_metrics:
        recommendations.append(
            f"Prioritise the strategy with efficiency score {simulation_metrics.get('efficiency_score')} and bottleneck {simulation_metrics.get('bottleneck_zone')}."
        )
    if whatif_new:
        recommendations.append("Use what-if deltas to stage changes before deploying new staffing or robotics levels.")
    if optimisation_results:
        best = min(optimisation_results.items(), key=lambda item: item[1].get("best_loss", float("inf")))[0]
        recommendations.append(f"Use {best} as the optimisation baseline for this benchmark family.")
    if rl_metrics:
        recommendations.append("Validate the learned RL policy against historical warehouse telemetry before operational rollout.")
    return "\n".join(f"- {item}" for item in recommendations) if recommendations else "No stored results are available yet."


def list_reports(db: Session, user: User) -> list[Report]:
    return list(db.scalars(select(Report).where(Report.user_id == user.id).order_by(Report.created_at.desc())))


def get_report(db: Session, user: User, report_id: int) -> Report:
    report = db.get(Report, report_id)
    if report is None or report.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report

