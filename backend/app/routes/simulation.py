from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.simulation import (
    SimulationRunRead,
    SimulationRunRequest,
    StrategyCompareRequest,
    StrategyComparisonResponse,
)
from app.services import simulation_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/run", response_model=SimulationRunRead)
def run_simulation(
    payload: SimulationRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return simulation_service.run_simulation(db, current_user, payload)


@router.get("/runs", response_model=list[SimulationRunRead])
def list_runs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return simulation_service.list_runs(db, current_user)


@router.get("/runs/{run_id}", response_model=SimulationRunRead)
def get_run(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return simulation_service.get_run(db, current_user, run_id)


@router.post("/compare-strategies", response_model=StrategyComparisonResponse)
def compare_strategies(
    payload: StrategyCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return simulation_service.compare_strategies(db, current_user, payload)

