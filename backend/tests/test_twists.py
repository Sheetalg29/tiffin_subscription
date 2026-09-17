import io
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.notification_service import create_delivery_notifications
from app.services.transfer_service import calculate_customer_allocations


def make_sub(pauses=None, transfers=None):
    plan = SimpleNamespace(monthly_price=Decimal("3000.00"))
    return SimpleNamespace(
        id=1,
        customer_id=1,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
        plan=plan,
        pauses=pauses or [],
        transfers=transfers or [],
    )


def test_transfer_splits_served_days_and_total_amount():
    transfers = [
        SimpleNamespace(
            id=1, from_customer_id=1, to_customer_id=2,
            transfer_date=date(2026, 9, 16),
        )
    ]
    sub = make_sub(transfers=transfers)
    allocations = calculate_customer_allocations(sub, date(2026, 9, 1))

    assert [x["customer_id"] for x in allocations] == [1, 2]
    assert sum(x["served_days"] for x in allocations) == 22
    assert sum(x["amount"] for x in allocations) == Decimal("3000.00")


def test_transfer_respects_paused_days():
    transfers = [
        SimpleNamespace(
            id=1, from_customer_id=1, to_customer_id=2,
            transfer_date=date(2026, 9, 16),
        )
    ]
    pauses = [
        SimpleNamespace(
            pause_start=date(2026, 9, 10),
            pause_end=date(2026, 9, 14),
        )
    ]
    sub = make_sub(pauses=pauses, transfers=transfers)
    allocations = calculate_customer_allocations(sub, date(2026, 9, 1))

    assert sum(x["served_days"] for x in allocations) == 19
    assert sum(x["amount"] for x in allocations) == Decimal("2590.91")


def test_notification_service_skips_weekend_and_paused():
    class FakeDB:
        def __init__(self):
            self.added = []
        def scalars(self, *args, **kwargs):
            class Result:
                def unique(self): return self
                def all(self): return []
            return Result()
        def scalar(self, *args, **kwargs): return None
        def add(self, item): self.added.append(item)
        def commit(self): pass

    owner = SimpleNamespace(id=10)
    db = FakeDB()

    assert create_delivery_notifications(db, owner, date(2026, 9, 19)) == 0
    assert db.added == []
