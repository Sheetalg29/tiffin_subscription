from datetime import datetime
from pydantic import BaseModel, Field

class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(default="", max_length=300)

class CustomerUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(default="", max_length=300)

class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    address: str
    created_at: datetime
    current_status: str = "INACTIVE"

    class Config:
        from_attributes = True
