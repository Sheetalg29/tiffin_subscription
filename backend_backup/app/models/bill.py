from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = (UniqueConstraint("subscription_id", "billing_month", name="uq_subscription_month_bill"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), index=True)
    billing_month: Mapped[date] = mapped_column(Date)
    total_service_days: Mapped[int] = mapped_column()
    paused_service_days: Mapped[int] = mapped_column()
    served_days: Mapped[int] = mapped_column()
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="DUE")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subscription = relationship("Subscription", back_populates="bills")
