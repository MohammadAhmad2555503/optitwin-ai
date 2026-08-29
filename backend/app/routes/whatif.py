from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.simulation import WhatIfRead, WhatIfRequest
from app.services import simulation_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/whatif", tags=["What-if Analysis"])


@router.post("/run", response_model=WhatIfRead)
def run_what_if(
    payload: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return simulation_service.run_what_if(db, current_user, payload)


@router.get("/results", response_model=list[WhatIfRead])
def list_results(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return simulation_service.list_what_if_results(db, current_user)


@router.get("/results/{result_id}", response_model=WhatIfRead)
def get_result(result_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return simulation_service.get_what_if_result(db, current_user, result_id)

