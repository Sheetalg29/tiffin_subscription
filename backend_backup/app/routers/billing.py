from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..dependencies import get_current_user
from ..models.bill import Bill
from ..models.customer import Customer
from ..models.subscription import Subscription
from ..models.user import User
from ..schemas.bill import BillCalculation, BillOut
from ..services.billing_service import calculate_bill

router = APIRouter(prefix="/api/bills", tags=["Billing"])


def calculation(subscription: Subscription, month: date):
    values = calculate_bill(subscription, month)
    return BillCalculation(subscription_id=subscription.id, customer_name=subscription.customer.name, billing_month=date(month.year, month.month, 1), plan_price=subscription.plan.monthly_price, **values)

@router.get("/calculate/{subscription_id}", response_model=BillCalculation)
def calculate(subscription_id: int, month: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.scalar(select(Subscription).join(Customer).options(joinedload(Subscription.customer), joinedload(Subscription.plan), joinedload(Subscription.pauses)).where(Subscription.id == subscription_id, Customer.owner_id == user.id))
    if not s: raise HTTPException(404, "Subscription not found")
    try:
        month_date = date.fromisoformat(f"{month}-01") if month else date.today().replace(day=1)
    except ValueError as exc:
        raise HTTPException(400, "month must be YYYY-MM") from exc
    return calculation(s, month_date)

@router.post("/generate/{subscription_id}", response_model=BillOut, status_code=201)
def generate(subscription_id: int, month: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.scalar(select(Subscription).join(Customer).options(joinedload(Subscription.customer), joinedload(Subscription.plan), joinedload(Subscription.pauses)).where(Subscription.id == subscription_id, Customer.owner_id == user.id))
    if not s: raise HTTPException(404, "Subscription not found")
    month_date = date.fromisoformat(f"{month}-01") if month else date.today().replace(day=1)
    existing = db.scalar(select(Bill).where(Bill.subscription_id == s.id, Bill.billing_month == month_date))
    values = calculate_bill(s, month_date)
    if existing:
        for k, v in values.items(): setattr(existing, k, v)
        db.commit(); db.refresh(existing); bill = existing
    else:
        bill = Bill(subscription_id=s.id, billing_month=month_date, **values)
        db.add(bill); db.commit(); db.refresh(bill)
    return BillOut.model_validate({**{c: getattr(bill,c) for c in ["id","subscription_id","billing_month","total_service_days","paused_service_days","served_days","daily_rate","amount","status","generated_at"]}, "customer_name": s.customer.name})

@router.get("", response_model=dict)
def list_bills(page: int = 1, limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    page = max(page, 1); limit = min(max(limit, 1), 100)
    base = select(Bill).join(Subscription).join(Customer).where(Customer.owner_id == user.id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(base.options(joinedload(Bill.subscription).joinedload(Subscription.customer)).order_by(desc(Bill.billing_month)).offset((page-1)*limit).limit(limit)).unique().all()
    items = [BillOut.model_validate({**{c: getattr(b,c) for c in ["id","subscription_id","billing_month","total_service_days","paused_service_days","served_days","daily_rate","amount","status","generated_at"]}, "customer_name": b.subscription.customer.name}) for b in rows]
    return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": (total+limit-1)//limit}
