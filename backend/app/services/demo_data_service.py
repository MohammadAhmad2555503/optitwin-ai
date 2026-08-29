from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import ActivityLog
from app.models.scenario import Scenario
from app.models.user import User
from app.utils.security import hash_password


def seed_demo_data(db: Session) -> None:
    user = db.scalar(select(User).where(User.email == "demo@optitwin.ai"))
    if user is None:
        user = User(
            name="Demo Operator",
            email="demo@optitwin.ai",
            password_hash=hash_password("demo-password"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    has_scenario = db.scalar(select(Scenario).where(Scenario.user_id == user.id))
    if has_scenario is None:
        scenario = Scenario(
            user_id=user.id,
            name="Metro Fulfilment Twin",
            workers=18,
            robots=8,
            orders_per_hour=180,
            storage_zones=6,
            average_picking_time=4.2,
            priority_order_percentage=22,
            robot_failure_probability=0.04,
            worker_efficiency=0.9,
            shift_duration=8,
            cost_per_worker=24,
            cost_per_robot=9,
            delay_penalty=3.5,
            demand_variability=0.24,
            inventory_restock_frequency=2,
        )
        db.add(scenario)
        db.add(
            ActivityLog(
                user_id=user.id,
                activity_type="demo.seeded",
                description="Seeded demo scenario 'Metro Fulfilment Twin'",
            )
        )
        db.commit()

