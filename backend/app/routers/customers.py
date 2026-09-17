from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.customer import Customer
from ..models.user import User
from ..schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from ..services.billing_service import current_status

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    duplicate = db.scalar(select(Customer).where(Customer.owner_id == user.id, Customer.phone == payload.phone))
    if duplicate:
        raise HTTPException(409, "A customer with this phone already exists")
    customer = Customer(owner_id=user.id, **payload.model_dump())
    db.add(customer); db.commit(); db.refresh(customer)
    customer.current_status = "INACTIVE"
    return customer

@router.get("", response_model=dict)
def list_customers(page: int = 1, limit: int = 10, search: str = "", sort_by: str = "created_at", order: str = "desc", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    page = max(page, 1); limit = min(max(limit, 1), 100)
    stmt = select(Customer).where(Customer.owner_id == user.id)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(or_(Customer.name.ilike(term), Customer.phone.ilike(term)))
    sort_map = {"name": Customer.name, "phone": Customer.phone, "created_at": Customer.created_at}
    column = sort_map.get(sort_by, Customer.created_at)
    stmt = stmt.order_by(desc(column) if order == "desc" else asc(column))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.offset((page-1)*limit).limit(limit)).all()
    result = []
    for c in rows:
        statuses = [current_status(s) for s in c.subscriptions]
        status = "ACTIVE" if "ACTIVE" in statuses else ("PAUSED" if "PAUSED" in statuses else "INACTIVE")
        result.append(CustomerOut.model_validate({**{k: getattr(c, k) for k in ["id","name","phone","address","created_at"]}, "current_status": status}))
    return {"items": result, "page": page, "limit": limit, "total": total, "total_pages": (total + limit - 1)//limit}

@router.get("/search", response_model=list[CustomerOut])
def search_customers(phone: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Customer).where(Customer.owner_id == user.id, Customer.phone.ilike(f"%{phone}%")).limit(20)).all()
    result = []
    for c in rows:
        statuses = [current_status(s) for s in c.subscriptions]
        status = "ACTIVE" if "ACTIVE" in statuses else ("PAUSED" if "PAUSED" in statuses else "INACTIVE")
        result.append(CustomerOut.model_validate({**{k: getattr(c, k) for k in ["id","name","phone","address","created_at"]}, "current_status": status}))
    return result

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.scalar(select(Customer).where(Customer.id == customer_id, Customer.owner_id == user.id))
    if not c: raise HTTPException(404, "Customer not found")
    statuses = [current_status(s) for s in c.subscriptions]
    status = "ACTIVE" if "ACTIVE" in statuses else ("PAUSED" if "PAUSED" in statuses else "INACTIVE")
    return CustomerOut.model_validate({**{k: getattr(c, k) for k in ["id","name","phone","address","created_at"]}, "current_status": status})

@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.scalar(select(Customer).where(Customer.id == customer_id, Customer.owner_id == user.id))
    if not c: raise HTTPException(404, "Customer not found")
    duplicate = db.scalar(select(Customer).where(Customer.owner_id == user.id, Customer.phone == payload.phone, Customer.id != customer_id))
    if duplicate: raise HTTPException(409, "A customer with this phone already exists")
    for key, value in payload.model_dump().items(): setattr(c, key, value)
    db.commit(); db.refresh(c)
    return get_customer(customer_id, db, user)

@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.scalar(select(Customer).where(Customer.id == customer_id, Customer.owner_id == user.id))
    if not c: raise HTTPException(404, "Customer not found")
    db.delete(c); db.commit()
