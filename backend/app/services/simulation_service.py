import json
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.simulation import SimulationRun, WhatIfResult
from app.models.user import User
from app.schemas.simulation import SimulationRunRequest, StrategyCompareRequest, WhatIfRequest
from app.services.activity_service import log_activity
from app.services.scenario_service import get_scenario
from app.simulation.strategies import STRATEGIES
from app.simulation.warehouse_env import run_warehouse_simulation, scenario_to_dict


def _loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback


def _run_to_read(run: SimulationRun) -> Dict[str, Any]:
    metrics = _loads(run.metrics_json, {})
    return {
        "id": run.id,
        "user_id": run.user_id,
        "scenario_id": run.scenario_id,
        "strategy_name": run.strategy_name,
        "total_orders": run.total_orders,
        "completed_orders": run.completed_orders,
        "delayed_orders": run.delayed_orders,
        "average_completion_time": run.average_completion_time,
        "average_queue_length": run.average_queue_length,
        "worker_utilisation": run.worker_utilisation,
        "robot_utilisation": run.robot_utilisation,
        "throughput_per_hour": run.throughput_per_hour,
        "cost_per_order": run.cost_per_order,
        "total_cost": run.total_cost,
        "efficiency_score": run.efficiency_score,
        "bottleneck_zone": run.bottleneck_zone,
        "delay_reduction_vs_baseline": metrics.get("delay_reduction_vs_baseline", 0.0),
        "metrics": metrics,
        "time_series": _loads(run.time_series_json, []),
        "created_at": run.created_at,
    }


def _persist_simulation(
    db: Session,
    user: User,
    scenario: Scenario,
    strategy_name: str,
    output: Dict[str, Any],
) -> SimulationRun:
    metrics = output["metrics"]
    run = SimulationRun(
        user_id=user.id,
        scenario_id=scenario.id,
        strategy_name=output["strategy_name"],
        total_orders=metrics["total_orders"],
        completed_orders=metrics["completed_orders"],
        delayed_orders=metrics["delayed_orders"],
        average_completion_time=metrics["average_completion_time"],
        average_queue_length=metrics["average_queue_length"],
        worker_utilisation=metrics["worker_utilisation"],
        robot_utilisation=metrics["robot_utilisation"],
        throughput_per_hour=metrics["throughput_per_hour"],
        cost_per_order=metrics["cost_per_order"],
        total_cost=metrics["total_cost"],
        efficiency_score=metrics["efficiency_score"],
        bottleneck_zone=metrics["bottleneck_zone"],
        metrics_json=json.dumps(metrics),
        time_series_json=json.dumps(output["time_series"]),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    log_activity(db, user.id, "simulation.run", f"Ran {strategy_name} on '{scenario.name}'")
    return run


def run_simulation(db: Session, user: User, payload: SimulationRunRequest) -> Dict[str, Any]:
    scenario = get_scenario(db, user, payload.scenario_id)
    output = run_warehouse_simulation(scenario, payload.strategy_name, payload.seed)
    if output["strategy_name"] != "First-Come-First-Served":
        baseline = run_warehouse_simulation(scenario, "First-Come-First-Served", payload.seed)
        baseline_delayed = max(baseline["metrics"]["delayed_orders"], 1)
        reduction = (baseline_delayed - output["metrics"]["delayed_orders"]) / baseline_delayed * 100
        output["metrics"]["delay_reduction_vs_baseline"] = round(reduction, 2)
    run = _persist_simulation(db, user, scenario, payload.strategy_name, output)
    return _run_to_read(run)


def list_runs(db: Session, user: User) -> List[Dict[str, Any]]:
    runs = db.scalars(
        select(SimulationRun).where(SimulationRun.user_id == user.id).order_by(SimulationRun.created_at.desc())
    )
    return [_run_to_read(run) for run in runs]


def get_run(db: Session, user: User, run_id: int) -> Dict[str, Any]:
    run = db.get(SimulationRun, run_id)
    if run is None or run.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation run not found")
    return _run_to_read(run)


def compare_strategies(db: Session, user: User, payload: StrategyCompareRequest) -> Dict[str, Any]:
    scenario = get_scenario(db, user, payload.scenario_id)
    raw_outputs = [run_warehouse_simulation(scenario, strategy, payload.seed) for strategy in STRATEGIES]
    baseline_delayed = max(raw_outputs[0]["metrics"]["delayed_orders"], 1)
    persisted = []
    for output in raw_outputs:
        reduction = (baseline_delayed - output["metrics"]["delayed_orders"]) / baseline_delayed * 100
        output["metrics"]["delay_reduction_vs_baseline"] = round(reduction, 2)
        persisted.append(_run_to_read(_persist_simulation(db, user, scenario, output["strategy_name"], output)))
    best = max(persisted, key=lambda row: row["efficiency_score"])
    log_activity(db, user.id, "simulation.compare", f"Compared strategies for '{scenario.name}'")
    return {"scenario_id": scenario.id, "best_strategy": best["strategy_name"], "results": persisted}


def run_what_if(db: Session, user: User, payload: WhatIfRequest) -> Dict[str, Any]:
    scenario = get_scenario(db, user, payload.base_scenario_id)
    base_data = scenario_to_dict(scenario)
    allowed = set(base_data.keys()) - {"name"}
    modified = dict(base_data)
    for key, value in payload.modified_parameters.items():
        if key in allowed:
            modified[key] = value

    baseline = run_warehouse_simulation(base_data, payload.strategy_name, payload.seed)["metrics"]
    new = run_warehouse_simulation(modified, payload.strategy_name, payload.seed)["metrics"]
    tracked = ["delayed_orders", "throughput_per_hour", "cost_per_order", "efficiency_score", "average_queue_length"]
    changes = {}
    for key in tracked:
        old = float(baseline.get(key, 0) or 0)
        changes[key] = round(((float(new.get(key, 0)) - old) / old * 100) if old else 0.0, 2)

    recommendation = _what_if_recommendation(changes, modified)
    result = WhatIfResult(
        user_id=user.id,
        base_scenario_id=scenario.id,
        modified_parameters_json=json.dumps(payload.modified_parameters),
        baseline_metrics_json=json.dumps(baseline),
        new_metrics_json=json.dumps(new),
        recommendation=recommendation,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    log_activity(db, user.id, "whatif.run", f"Ran what-if analysis for '{scenario.name}'")
    return _what_if_to_read(result, changes)


def _what_if_recommendation(changes: Dict[str, float], modified: Dict[str, Any]) -> str:
    throughput_gain = changes.get("throughput_per_hour", 0)
    delay_change = changes.get("delayed_orders", 0)
    cost_change = changes.get("cost_per_order", 0)
    if throughput_gain > 5 and delay_change < -5 and cost_change < 8:
        return "Adopt this configuration for a controlled pilot; it improves flow without excessive unit cost."
    if delay_change < -10:
        return "Operationally promising for service-level recovery, but validate labour and robot capacity assumptions."
    if cost_change > 12 and throughput_gain < 3:
        return "Do not adopt as-is; the cost increase is not matched by enough throughput gain."
    if modified.get("robot_failure_probability", 0) > 0.15:
        return "Prioritise maintenance resilience before scaling automation in this scenario."
    return "Run a second comparison with hybrid and RL strategies before making a deployment decision."


def _what_if_to_read(result: WhatIfResult, changes: Dict[str, float] | None = None) -> Dict[str, Any]:
    baseline = _loads(result.baseline_metrics_json, {})
    new = _loads(result.new_metrics_json, {})
    if changes is None:
        changes = {}
        for key in ["delayed_orders", "throughput_per_hour", "cost_per_order", "efficiency_score", "average_queue_length"]:
            old = float(baseline.get(key, 0) or 0)
            changes[key] = round(((float(new.get(key, 0)) - old) / old * 100) if old else 0.0, 2)
    return {
        "id": result.id,
        "user_id": result.user_id,
        "base_scenario_id": result.base_scenario_id,
        "modified_parameters": _loads(result.modified_parameters_json, {}),
        "baseline_metrics": baseline,
        "new_metrics": new,
        "percentage_changes": changes,
        "recommendation": result.recommendation,
        "created_at": result.created_at,
    }


def list_what_if_results(db: Session, user: User) -> List[Dict[str, Any]]:
    rows = db.scalars(
        select(WhatIfResult).where(WhatIfResult.user_id == user.id).order_by(WhatIfResult.created_at.desc())
    )
    return [_what_if_to_read(row) for row in rows]


def get_what_if_result(db: Session, user: User, result_id: int) -> Dict[str, Any]:
    result = db.get(WhatIfResult, result_id)
    if result is None or result.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="What-if result not found")
    return _what_if_to_read(result)

