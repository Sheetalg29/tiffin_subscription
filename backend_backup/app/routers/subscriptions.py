from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..dependencies import get_current_user
from ..models.customer import Customer
from ..models.pause_period import PausePeriod
from ..models.plan import Plan
from ..models.subscription import Subscription
from ..models.user import User
from ..schemas.subscription import PauseCreate, PauseOut, SubscriptionCreate, SubscriptionOut
from ..services.billing_service import current_status

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])


def serialize(s: Subscription):
    return SubscriptionOut.model_validate({
        "id": s.id, "customer_id": s.customer_id, "plan_id": s.plan_id,
        "start_date": s.start_date, "end_date": s.end_date, "status": current_status(s),
        "customer_name": s.customer.name, "plan_name": s.plan.name,
        "monthly_price": s.plan.monthly_price,
        "pauses": s.pauses,
    })

@router.post("", response_model=SubscriptionOut, status_code=201)
def create_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.end_date < payload.start_date: raise HTTPException(400, "End date must be after start date")
    customer = db.scalar(select(Customer).where(Customer.id == payload.customer_id, Customer.owner_id == user.id))
    plan = db.get(Plan, payload.plan_id)
    if not customer or not plan: raise HTTPException(404, "Customer or plan not found")
    subscription = Subscription(customer_id=customer.id, plan_id=plan.id, start_date=payload.start_date, end_date=payload.end_date, status="ACTIVE")
    db.add(subscription); db.commit(); db.refresh(subscription)
    subscription = db.scalar(select(Subscription).options(joinedload(Subscription.customer), joinedload(Subscription.plan)).where(Subscription.id == subscription.id))
    return serialize(subscription)

@router.get("", response_model=dict)
def list_subscriptions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Subscription).join(Customer).options(joinedload(Subscription.customer), joinedload(Subscription.plan), joinedload(Subscription.pauses)).where(Customer.owner_id == user.id).order_by(Subscription.created_at.desc())).unique().all()
    items = [serialize(s) for s in rows]
    return {"items": items, "total": len(items)}

@router.get("/{subscription_id}", response_model=SubscriptionOut)
def get_subscription(subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.scalar(select(Subscription).join(Customer).options(joinedload(Subscription.customer), joinedload(Subscription.plan), joinedload(Subscription.pauses)).where(Subscription.id == subscription_id, Customer.owner_id == user.id))
    if not s: raise HTTPException(404, "Subscription not found")
    return serialize(s)

@router.post("/{subscription_id}/pause", response_model=PauseOut, status_code=201)
def pause_subscription(subscription_id: int, payload: PauseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.scalar(select(Subscription).join(Customer).where(Subscription.id == subscription_id, Customer.owner_id == user.id))
    if not s: raise HTTPException(404, "Subscription not found")
    if payload.pause_end < payload.pause_start: raise HTTPException(400, "Pause end must be after pause start")
    if payload.pause_end < s.start_date or payload.pause_start > s.end_date: raise HTTPException(400, "Pause must overlap the subscription")
    pause = PausePeriod(subscription_id=s.id, **payload.model_dump())
    db.add(pause); db.commit(); db.refresh(pause)
    return pause

@router.post("/{subscription_id}/resume", response_model=SubscriptionOut)
def resume_subscription(subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.scalar(select(Subscription).join(Customer).options(joinedload(Subscription.customer), joinedload(Subscription.plan), joinedload(Subscription.pauses)).where(Subscription.id == subscription_id, Customer.owner_id == user.id))
    if not s: raise HTTPException(404, "Subscription not found")
    today = date.today()
    # Resume means remove the pause that currently covers today, if one exists.
    covering = [p for p in s.pauses if p.pause_start <= today <= p.pause_end]
    if not covering: raise HTTPException(400, "No current pause to resume")
    for p in covering: db.delete(p)
    db.commit(); db.refresh(s)
    return serialize(s)
