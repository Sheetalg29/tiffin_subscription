from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class TransferCreate(BaseModel):
    new_customer_id: int
    transfer_date: date


class TransferOut(BaseModel):
    id: int
    subscription_id: int
    from_customer_id: int
    to_customer_id: int
    transfer_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class BillAllocationOut(BaseModel):
    customer_id: int
    customer_name: str
    served_days: int
    amount: Decimal
