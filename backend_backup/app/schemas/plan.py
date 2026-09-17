from decimal import Decimal
from pydantic import BaseModel, Field

class PlanCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    monthly_price: Decimal = Field(gt=0)
    description: str = Field(default="", max_length=300)

class PlanOut(BaseModel):
    id: int
    name: str
    monthly_price: Decimal
    description: str
    active: bool
    class Config:
        from_attributes = True
