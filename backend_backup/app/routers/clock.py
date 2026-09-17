from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..services.notification_service import create_delivery_notifications

router = APIRouter(prefix="/api/clock", tags=["Clock"])


@router.post("")
def run_clock(today: date | None = None,
              db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    run_date = today or date.today()
    created = create_delivery_notifications(db, user, run_date)
    return {
        "date": run_date,
        "due_notifications_created": created,
        "message": "Daily delivery clock processed successfully.",
    }
