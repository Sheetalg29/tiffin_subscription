from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class BillAllocation(Base):
    __tablename__ = "bill_allocations"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bills.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    served_days: Mapped[int] = mapped_column()
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    bill = relationship("Bill", back_populates="allocations")
    customer = relationship("Customer")
