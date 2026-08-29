import json
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.optimisation import OptimisationExperiment
from app.models.user import User
from app.optimisation.optimizers import run_optimizer
from app.schemas.optimisation import AlphaSensitivityRequest, OptimisationRunRequest
from app.services.activity_service import log_activity


def _loads(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback


def _experiment_to_read(experiment: OptimisationExperiment) -> Dict[str, Any]:
    return {
        "id": experiment.id,
        "user_id": experiment.user_id,
        "function_name": experiment.function_name,
        "optimisers": _loads(experiment.optimisers_json, []),
        "learning_rate": experiment.learning_rate,
        "iterations": experiment.iterations,
        "alpha": experiment.alpha,
        "results": _loads(experiment.results_json, {}),
        "convergence_curves": _loads(experiment.convergence_curves_json, {}),
        "stability_metrics": _loads(experiment.stability_metrics_json, {}),
        "created_at": experiment.created_at,
    }


def run_core(payload: OptimisationRunRequest) -> Dict[str, Any]:
    runs = [
        run_optimizer(
            payload.function_name,
            optimiser,
            payload.learning_rate,
            payload.iterations,
            payload.alpha,
            payload.seed,
        )
        for optimiser in payload.optimisers
    ]
    results = {run["optimiser"]: {**run["metrics"], "final_position": run["final_position"]} for run in runs}
    curves = {run["optimiser"]: run["curve"] for run in runs}
    stability = {name: result["stability_score"] for name, result in results.items()}
    return {"results": results, "convergence_curves": curves, "stability_metrics": stability}


def run_experiment(db: Session, user: User, payload: OptimisationRunRequest) -> Dict[str, Any]:
    output = run_core(payload)
    experiment = OptimisationExperiment(
        user_id=user.id,
        function_name=payload.function_name.lower(),
        optimisers_json=json.dumps(payload.optimisers),
        learning_rate=payload.learning_rate,
        iterations=payload.iterations,
        alpha=payload.alpha,
        results_json=json.dumps(output["results"]),
        convergence_curves_json=json.dumps(output["convergence_curves"]),
        stability_metrics_json=json.dumps(output["stability_metrics"]),
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    log_activity(db, user.id, "optimisation.run", f"Ran optimisation lab on {payload.function_name}")
    return _experiment_to_read(experiment)


def list_experiments(db: Session, user: User) -> List[Dict[str, Any]]:
    rows = db.scalars(
        select(OptimisationExperiment)
        .where(OptimisationExperiment.user_id == user.id)
        .order_by(OptimisationExperiment.created_at.desc())
    )
    return [_experiment_to_read(row) for row in rows]


def get_experiment(db: Session, user: User, experiment_id: int) -> Dict[str, Any]:
    experiment = db.get(OptimisationExperiment, experiment_id)
    if experiment is None or experiment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Optimisation experiment not found")
    return _experiment_to_read(experiment)


def alpha_sensitivity(payload: AlphaSensitivityRequest) -> Dict[str, Any]:
    results = []
    for alpha in payload.alphas:
        request = OptimisationRunRequest(
            function_name=payload.function_name,
            optimisers=["Fractional GD"],
            learning_rate=payload.learning_rate,
            iterations=payload.iterations,
            alpha=alpha,
            seed=payload.seed,
        )
        output = run_core(request)
        metrics = output["results"]["Fractional GD"]
        results.append({"alpha": alpha, **metrics})
    best = min(results, key=lambda row: row["best_loss"]) if results else None
    return {"function_name": payload.function_name, "results": results, "best_alpha": best["alpha"] if best else None}

