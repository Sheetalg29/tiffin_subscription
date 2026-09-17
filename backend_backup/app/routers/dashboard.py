from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.customer import Customer
from ..models.subscription import Subscription
from ..models.bill import Bill
from ..models.user import User
from ..services.billing_service import current_status

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    customers = db.scalars(select(Customer).where(Customer.owner_id == user.id)).all()
    statuses = [current_status(s) for c in customers for s in c.subscriptions]
    active = statuses.count("ACTIVE")
    paused = statuses.count("PAUSED")
    revenue = db.scalar(select(func.coalesce(func.sum(Bill.amount), 0)).join(Subscription).join(Customer).where(Customer.owner_id == user.id)) or Decimal("0")
    return {"total_customers": len(customers), "active": active, "paused": paused, "revenue": Decimal(revenue)}
