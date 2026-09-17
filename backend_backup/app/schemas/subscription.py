from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int
    start_date: date
    end_date: date

class PauseCreate(BaseModel):
    pause_start: date
    pause_end: date
    reason: str = ""

class PauseOut(BaseModel):
    id: int
    pause_start: date
    pause_end: date
    reason: str
    class Config:
        from_attributes = True

class SubscriptionOut(BaseModel):
    id: int
    customer_id: int
    plan_id: int
    start_date: date
    end_date: date
    status: str
    customer_name: str
    plan_name: str
    monthly_price: Decimal
    pauses: list[PauseOut] = []
    class Config:
        from_attributes = True
