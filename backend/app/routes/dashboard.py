from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, RecentActivityResponse
from app.services import dashboard_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dashboard_service.summary(db, current_user)


@router.get("/recent-activity", response_model=RecentActivityResponse)
def recent_activity(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dashboard_service.recent_activity(db, current_user)

