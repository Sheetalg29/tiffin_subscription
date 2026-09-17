from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..models.customer import Customer
from ..models.notification_outbox import NotificationOutbox
from ..models.subscription import Subscription
from ..models.user import User
from .billing_service import current_status


def create_delivery_notifications(db: Session, owner: User, today: date) -> int:
    """Create one idempotent outbox event for each customer due for tiffin today."""
    if today.weekday() >= 5:
        return 0

    subscriptions = db.scalars(
        select(Subscription)
        .join(Customer)
        .options(joinedload(Subscription.customer), joinedload(Subscription.pauses))
        .where(
            Customer.owner_id == owner.id,
            Subscription.start_date <= today,
            Subscription.end_date >= today,
        )
    ).unique().all()

    created = 0
    for subscription in subscriptions:
        if current_status(subscription, today) != "ACTIVE":
            continue

        exists = db.scalar(
            select(NotificationOutbox).where(
                NotificationOutbox.subscription_id == subscription.id,
                NotificationOutbox.notification_date == today,
                NotificationOutbox.notification_type == "DELIVERY_DUE",
            )
        )
        if exists:
            continue

        event = NotificationOutbox(
            owner_id=owner.id,
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            notification_date=today,
            notification_type="DELIVERY_DUE",
            message=f"Tiffin delivery is due today for {subscription.customer.name}.",
            status="PENDING",
        )
        db.add(event)
        created += 1

    db.commit()
    return created
