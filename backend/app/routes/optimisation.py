from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.optimisation import AlphaSensitivityRequest, OptimisationExperimentRead, OptimisationRunRequest
from app.services import optimisation_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/optimisation", tags=["Optimisation"])


@router.post("/run", response_model=OptimisationExperimentRead)
def run_experiment(
    payload: OptimisationRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return optimisation_service.run_experiment(db, current_user, payload)


@router.get("/experiments", response_model=list[OptimisationExperimentRead])
def list_experiments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return optimisation_service.list_experiments(db, current_user)


@router.get("/experiments/{experiment_id}", response_model=OptimisationExperimentRead)
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return optimisation_service.get_experiment(db, current_user, experiment_id)


@router.post("/compare")
def compare(payload: OptimisationRunRequest, current_user: User = Depends(get_current_user)):
    return optimisation_service.run_core(payload)


@router.post("/alpha-sensitivity")
def alpha_sensitivity(payload: AlphaSensitivityRequest, current_user: User = Depends(get_current_user)):
    return optimisation_service.alpha_sensitivity(payload)

