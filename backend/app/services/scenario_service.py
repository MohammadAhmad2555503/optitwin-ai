from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.user import User
from app.schemas.scenario import ScenarioCreate, ScenarioUpdate
from app.services.activity_service import log_activity


def create_scenario(db: Session, user: User, payload: ScenarioCreate) -> Scenario:
    scenario = Scenario(user_id=user.id, **payload.model_dump())
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    log_activity(db, user.id, "scenario.created", f"Created scenario '{scenario.name}'")
    return scenario


def list_scenarios(db: Session, user: User) -> list[Scenario]:
    return list(db.scalars(select(Scenario).where(Scenario.user_id == user.id).order_by(Scenario.updated_at.desc())))


def get_scenario(db: Session, user: User, scenario_id: int) -> Scenario:
    scenario = db.get(Scenario, scenario_id)
    if scenario is None or scenario.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return scenario


def update_scenario(db: Session, user: User, scenario_id: int, payload: ScenarioUpdate) -> Scenario:
    scenario = get_scenario(db, user, scenario_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(scenario, key, value)
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    log_activity(db, user.id, "scenario.updated", f"Updated scenario '{scenario.name}'")
    return scenario


def delete_scenario(db: Session, user: User, scenario_id: int) -> None:
    scenario = get_scenario(db, user, scenario_id)
    name = scenario.name
    db.delete(scenario)
    db.commit()
    log_activity(db, user.id, "scenario.deleted", f"Deleted scenario '{name}'")

