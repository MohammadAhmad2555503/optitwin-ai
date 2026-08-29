from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.report import ReportGenerateRequest, ReportRead
from app.services import report_service
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportRead)
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service.generate_report(db, current_user, payload)


@router.get("", response_model=list[ReportRead])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return report_service.list_reports(db, current_user)


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return report_service.get_report(db, current_user, report_id)

