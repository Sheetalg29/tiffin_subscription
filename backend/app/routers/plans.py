from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.plan import Plan
from ..models.user import User
from ..schemas.plan import PlanCreate, PlanOut

router = APIRouter(prefix="/api/plans", tags=["Plans"])

@router.post("", response_model=PlanOut, status_code=201)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Plans are global templates in this MVP; first creation with same name is reused.
    existing = db.scalar(select(Plan).where(Plan.name == payload.name))
    if existing: raise HTTPException(409, "Plan name already exists")
    plan = Plan(**payload.model_dump())
    db.add(plan); db.commit(); db.refresh(plan)
    return plan

@router.get("", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(Plan).where(Plan.active == True).order_by(Plan.monthly_price)).all()
