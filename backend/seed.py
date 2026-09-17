from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models import User, Customer, Plan, Subscription, PausePeriod
from app.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    user = db.scalar(select(User).where(User.email == "demo@tiffinflow.app"))
    if not user:
        user = User(name="Demo Owner", email="demo@tiffinflow.app", password_hash=hash_password("Demo@1234"))
        db.add(user); db.commit(); db.refresh(user)
    plan = db.scalar(select(Plan).where(Plan.name == "Standard Lunch"))
    if not plan:
        plan = Plan(name="Standard Lunch", monthly_price=Decimal("3000.00"), description="Weekday home-style lunch")
        db.add(plan); db.commit(); db.refresh(plan)
    for name, phone, address, paused in [
        ("Rahul Sharma", "9876543210", "Malviya Nagar, Jaipur", True),
        ("Neha Singh", "9988776655", "Jagatpura, Jaipur", False),
        ("Amit Kumar", "9123456789", "Mansarovar, Jaipur", False),
    ]:
        c = db.scalar(select(Customer).where(Customer.owner_id == user.id, Customer.phone == phone))
        if not c:
            c = Customer(owner_id=user.id, name=name, phone=phone, address=address); db.add(c); db.commit(); db.refresh(c)
        s = db.scalar(select(Subscription).where(Subscription.customer_id == c.id))
        if not s:
            s = Subscription(customer_id=c.id, plan_id=plan.id, start_date=date(2026,9,1), end_date=date(2026,9,30)); db.add(s); db.commit(); db.refresh(s)
        if paused and not s.pauses:
            db.add(PausePeriod(subscription_id=s.id, pause_start=date(2026,9,15), pause_end=date(2026,9,18), reason="Travel")); db.commit()
    print("Demo data ready: demo@tiffinflow.app / Demo@1234")
finally:
    db.close()
