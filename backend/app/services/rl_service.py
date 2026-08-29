import json
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rl import RLTrainingRun
from app.models.user import User
from app.rl.rl_demo import evaluate_policy_artifact, generate_training_run
from app.rl.warehouse_rl_env import get_rl_spec
from app.schemas.rl import RLEvaluateRequest, RLTrainRequest
from app.services.activity_service import log_activity
from app.services.scenario_service import get_scenario
from app.simulation.strategies import STRATEGIES
from app.simulation.warehouse_env import run_warehouse_simulation


def _loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback


def _run_to_read(run: RLTrainingRun) -> Dict[str, Any]:
    return {
        "id": run.id,
        "user_id": run.user_id,
        "scenario_id": run.scenario_id,
        "algorithm": run.algorithm,
        "episodes": run.episodes,
        "reward_function": _loads(run.reward_function_json, {}),
        "training_metrics": _loads(run.training_metrics_json, {}),
        "reward_curve": _loads(run.reward_curve_json, []),
        "comparison_metrics": _loads(run.comparison_metrics_json, {}),
        "status": run.status,
        "created_at": run.created_at,
    }


def train(db: Session, user: User, payload: RLTrainRequest) -> Dict[str, Any]:
    scenario = get_scenario(db, user, payload.scenario_id)
    demo = generate_training_run(scenario, payload.episodes, payload.seed, payload.algorithm)
    run = RLTrainingRun(
        user_id=user.id,
        scenario_id=scenario.id,
        algorithm=payload.algorithm,
        episodes=payload.episodes,
        reward_function_json=json.dumps(demo["reward_function"]),
        training_metrics_json=json.dumps(demo["training_metrics"]),
        reward_curve_json=json.dumps(demo["reward_curve"]),
        comparison_metrics_json=json.dumps(demo["comparison_metrics"]),
        status="completed",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    log_activity(db, user.id, "rl.train", f"Trained RL policy for '{scenario.name}'")
    return _run_to_read(run)


def list_runs(db: Session, user: User) -> List[Dict[str, Any]]:
    rows = db.scalars(select(RLTrainingRun).where(RLTrainingRun.user_id == user.id).order_by(RLTrainingRun.created_at.desc()))
    return [_run_to_read(row) for row in rows]


def get_run(db: Session, user: User, run_id: int) -> Dict[str, Any]:
    run = db.get(RLTrainingRun, run_id)
    if run is None or run.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RL training run not found")
    return _run_to_read(run)


def evaluate(db: Session, user: User, payload: RLEvaluateRequest) -> Dict[str, Any]:
    scenario = get_scenario(db, user, payload.scenario_id)
    if payload.run_id is not None:
        run = db.get(RLTrainingRun, payload.run_id)
        if run is None or run.user_id != user.id or run.scenario_id != scenario.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RL training run not found")
        training_metrics = _loads(run.training_metrics_json, {})
        policy_artifact = training_metrics.get("policy_artifact", {})
        evaluation = evaluate_policy_artifact(scenario, policy_artifact, payload.episodes, payload.seed)
    else:
        trained = generate_training_run(scenario, max(payload.episodes * 2, 20), payload.seed, "EvaluationQAgent")
        evaluation = evaluate_policy_artifact(
            scenario,
            trained["training_metrics"]["policy_artifact"],
            payload.episodes,
            payload.seed,
        )
    return {
        "scenario_id": scenario.id,
        "episodes": payload.episodes,
        "evaluation_metrics": evaluation["evaluation_metrics"],
        "reward_curve": evaluation["reward_curve"],
    }


def compare_with_strategies(db: Session, user: User, scenario_id: int, seed: int | None = 42) -> Dict[str, Any]:
    scenario = get_scenario(db, user, scenario_id)
    rule_based = {}
    for strategy in STRATEGIES[:-1]:
        metrics = run_warehouse_simulation(scenario, strategy, seed)["metrics"]
        rule_based[strategy] = {
            "delay_rate": metrics["delay_rate"],
            "throughput_per_hour": metrics["throughput_per_hour"],
            "cost_per_order": metrics["cost_per_order"],
            "efficiency_score": metrics["efficiency_score"],
        }
    latest_run = db.scalar(
        select(RLTrainingRun)
        .where(RLTrainingRun.user_id == user.id, RLTrainingRun.scenario_id == scenario.id)
        .order_by(RLTrainingRun.created_at.desc())
    )
    if latest_run:
        training_metrics = _loads(latest_run.training_metrics_json, {})
        policy_artifact = training_metrics.get("policy_artifact", {})
        rl_evaluation = evaluate_policy_artifact(scenario, policy_artifact, 20, seed)
        rl_metrics = {"RL Agent Strategy": rl_evaluation["evaluation_metrics"]}
    else:
        rl_metrics = generate_training_run(scenario, 80, seed, "TabularQAgent")["comparison_metrics"]
    return {"rl_spec": get_rl_spec().__dict__, "comparison": {**rule_based, **rl_metrics}}

