from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from app.services.billing_service import calculate_bill


def make_subscription(pauses=None):
    plan = SimpleNamespace(monthly_price=Decimal("3000.00"))
    return SimpleNamespace(start_date=date(2026,9,1), end_date=date(2026,9,30), plan=plan, pauses=pauses or [])


def test_full_month_has_22_weekdays():
    result = calculate_bill(make_subscription(), date(2026,9,1))
    assert result["total_service_days"] == 22
    assert result["served_days"] == 22
    assert result["amount"] == Decimal("3000.00")


def test_weekday_pause_is_not_billed():
    pause = SimpleNamespace(pause_start=date(2026,9,10), pause_end=date(2026,9,14))
    result = calculate_bill(make_subscription([pause]), date(2026,9,1))
    assert result["paused_service_days"] == 3  # Sep 10, 11 and 14 are weekdays
    assert result["served_days"] == 19


def test_overlapping_pauses_are_not_double_counted():
    pauses = [
        SimpleNamespace(pause_start=date(2026,9,10), pause_end=date(2026,9,15)),
        SimpleNamespace(pause_start=date(2026,9,13), pause_end=date(2026,9,18)),
    ]
    result = calculate_bill(make_subscription(pauses), date(2026,9,1))
    assert result["paused_service_days"] == 7
