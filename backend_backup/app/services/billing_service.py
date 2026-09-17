from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from ..models.subscription import Subscription


def iter_dates(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def service_dates(start: date, end: date) -> set[date]:
    return {d for d in iter_dates(start, end) if d.weekday() < 5}


def effective_paused_dates(subscription: Subscription) -> set[date]:
    paused: set[date] = set()
    for pause in subscription.pauses:
        start = max(pause.pause_start, subscription.start_date)
        end = min(pause.pause_end, subscription.end_date)
        if start <= end:
            paused |= service_dates(start, end)
    return paused


def calculate_bill(subscription: Subscription, billing_month: date):
    month_start = date(billing_month.year, billing_month.month, 1)
    month_end = date(billing_month.year, billing_month.month, monthrange(billing_month.year, billing_month.month)[1])
    period_start = max(subscription.start_date, month_start)
    period_end = min(subscription.end_date, month_end)
    if period_start > period_end:
        return {
            "total_service_days": 0,
            "paused_service_days": 0,
            "served_days": 0,
            "daily_rate": Decimal("0.00"),
            "amount": Decimal("0.00"),
        }
    service = service_dates(period_start, period_end)
    paused = effective_paused_dates(subscription) & service
    served = service - paused
    total = len(service)
    paused_count = len(paused)
    served_count = len(served)
    daily_rate = (Decimal(subscription.plan.monthly_price) / Decimal(total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total else Decimal("0.00")
    amount = (Decimal(subscription.plan.monthly_price) * Decimal(served_count) / Decimal(total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total else Decimal("0.00")
    return {
        "total_service_days": total,
        "paused_service_days": paused_count,
        "served_days": served_count,
        "daily_rate": daily_rate,
        "amount": amount,
    }


def current_status(subscription: Subscription, today: date | None = None) -> str:
    today = today or date.today()
    if not (subscription.start_date <= today <= subscription.end_date):
        return "INACTIVE"
    for pause in subscription.pauses:
        if pause.pause_start <= today <= pause.pause_end:
            return "PAUSED"
    return "ACTIVE"
