from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models.bill import Bill
from ..models.bill_allocation import BillAllocation
from ..models.customer import Customer
from ..models.subscription import Subscription
from ..models.subscription_transfer import SubscriptionTransfer
from .billing_service import service_dates, calculate_bill, effective_paused_dates


CENT = Decimal("0.01")


def get_initial_customer_id(subscription: Subscription) -> int:
    transfers = sorted(subscription.transfers, key=lambda t: (t.transfer_date, t.id))
    return transfers[0].from_customer_id if transfers else subscription.customer_id


def calculate_customer_allocations(subscription: Subscription, billing_month: date):
    """
    Split served service days between customers across transfer dates.
    The plan and billing cycle stay unchanged.
    """
    month_start = date(billing_month.year, billing_month.month, 1)
    from calendar import monthrange
    month_end = date(
        billing_month.year, billing_month.month,
        monthrange(billing_month.year, billing_month.month)[1]
    )
    period_start = max(subscription.start_date, month_start)
    period_end = min(subscription.end_date, month_end)
    if period_start > period_end:
        return []

    service = service_dates(period_start, period_end)
    paused = effective_paused_dates(subscription) & service
    served = service - paused

    transfers = sorted(
        [t for t in subscription.transfers
         if subscription.start_date <= t.transfer_date <= subscription.end_date],
        key=lambda t: (t.transfer_date, t.id),
    )

    segments = []
    current_customer = get_initial_customer_id(subscription)
    segment_start = subscription.start_date

    for transfer in transfers:
        segment_end = transfer.transfer_date - __import__("datetime").timedelta(days=1)
        if segment_start <= segment_end:
            segments.append((current_customer, segment_start, segment_end))
        current_customer = transfer.to_customer_id
        segment_start = transfer.transfer_date

    if segment_start <= subscription.end_date:
        segments.append((current_customer, segment_start, subscription.end_date))

    counts = []
    for customer_id, start, end in segments:
        days = served & service_dates(max(start, period_start), min(end, period_end))
        if days:
            counts.append((customer_id, len(days)))

    total = len(service)
    if not counts or not total:
        return []

    total_amount = (Decimal(subscription.plan.monthly_price) *
                    Decimal(len(served)) / Decimal(total)).quantize(CENT, rounding=ROUND_HALF_UP)

    allocations = []
    running = Decimal("0.00")
    for index, (customer_id, days) in enumerate(counts):
        if index == len(counts) - 1:
            amount = total_amount - running
        else:
            amount = (Decimal(subscription.plan.monthly_price) *
                      Decimal(days) / Decimal(total)).quantize(CENT, rounding=ROUND_HALF_UP)
            running += amount
        allocations.append({
            "customer_id": customer_id,
            "served_days": days,
            "amount": amount,
        })
    return allocations


def persist_bill_allocations(db: Session, bill: Bill, allocations: list[dict]):
    for allocation in list(bill.allocations):
        db.delete(allocation)
    db.flush()
    for item in allocations:
        db.add(BillAllocation(
            bill_id=bill.id,
            customer_id=item["customer_id"],
            served_days=item["served_days"],
            amount=item["amount"],
        ))
