from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

class BillOut(BaseModel):
    id: int
    subscription_id: int
    billing_month: date
    total_service_days: int
    paused_service_days: int
    served_days: int
    daily_rate: Decimal
    amount: Decimal
    status: str
    generated_at: datetime
    customer_name: str
    class Config:
        from_attributes = True

class BillCalculation(BaseModel):
    subscription_id: int
    customer_name: str
    billing_month: date
    plan_price: Decimal
    total_service_days: int
    paused_service_days: int
    served_days: int
    daily_rate: Decimal
    amount: Decimal
