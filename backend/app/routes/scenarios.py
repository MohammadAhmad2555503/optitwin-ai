from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.scenario import ScenarioCreate, ScenarioRead, ScenarioUpdate
from app.services import scenario_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.post("", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
def create_scenario(
    payload: ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return scenario_service.create_scenario(db, current_user, payload)


@router.get("", response_model=list[ScenarioRead])
def list_scenarios(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return scenario_service.list_scenarios(db, current_user)


@router.get("/{scenario_id}", response_model=ScenarioRead)
def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return scenario_service.get_scenario(db, current_user, scenario_id)


@router.patch("/{scenario_id}", response_model=ScenarioRead)
def update_scenario(
    scenario_id: int,
    payload: ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return scenario_service.update_scenario(db, current_user, scenario_id, payload)


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scenario_service.delete_scenario(db, current_user, scenario_id)
    return None

