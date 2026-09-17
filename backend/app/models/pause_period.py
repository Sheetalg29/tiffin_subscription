from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class PausePeriod(Base):
    __tablename__ = "pause_periods"
    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), index=True)
    pause_start: Mapped[date] = mapped_column(Date)
    pause_end: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subscription = relationship("Subscription", back_populates="pauses")
