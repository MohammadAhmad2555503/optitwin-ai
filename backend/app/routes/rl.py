from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.rl import RLEvaluateRequest, RLRunRead, RLTrainRequest
from app.services import rl_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/rl", tags=["RL Lab"])


@router.post("/train", response_model=RLRunRead)
def train(payload: RLTrainRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rl_service.train(db, current_user, payload)


@router.get("/runs", response_model=list[RLRunRead])
def list_runs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rl_service.list_runs(db, current_user)


@router.get("/runs/{run_id}", response_model=RLRunRead)
def get_run(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rl_service.get_run(db, current_user, run_id)


@router.post("/evaluate")
def evaluate(payload: RLEvaluateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rl_service.evaluate(db, current_user, payload)


@router.post("/compare-with-strategies")
def compare_with_strategies(
    payload: RLEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rl_service.compare_with_strategies(db, current_user, payload.scenario_id, payload.seed)

