from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


def log_activity(db: Session, user_id: int, activity_type: str, description: str) -> ActivityLog:
    activity = ActivityLog(user_id=user_id, activity_type=activity_type, description=description[:255])
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

