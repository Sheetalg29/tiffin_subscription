from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class SubscriptionTransfer(Base):
    __tablename__ = "subscription_transfers"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), index=True)
    from_customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    to_customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    transfer_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subscription = relationship("Subscription", back_populates="transfers")
    from_customer = relationship("Customer", foreign_keys=[from_customer_id])
    to_customer = relationship("Customer", foreign_keys=[to_customer_id])
