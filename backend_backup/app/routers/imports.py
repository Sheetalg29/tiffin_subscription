import csv
import io
import re
from datetime import date, datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.customer import Customer
from ..models.plan import Plan
from ..models.subscription import Subscription
from ..models.user import User
from ..schemas.imports import CustomerImportReport, ImportRejectedRow

router = APIRouter(prefix="/api/import", tags=["Import"])

DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d",
    "%d-%m-%Y", "%d/%m/%Y",
    "%d-%m-%y", "%d/%m/%y",
)


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", (value or "").strip())


def parse_date(value: str) -> date:
    raw = (value or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError("Invalid date")


@router.post("/customers", response_model=CustomerImportReport)
async def import_customers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a CSV file")

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(400, "CSV must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(text))
    required = {"name", "phone"}
    if not reader.fieldnames or not required.issubset({h.strip().lower() for h in reader.fieldnames}):
        raise HTTPException(400, "CSV must contain at least name and phone columns")

    # Normalize header names once.
    reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
    existing_phones = set(
        db.scalars(select(Customer.phone).where(Customer.owner_id == user.id)).all()
    )
    seen = set(existing_phones)

    total = imported = duplicates = rejected = 0
    rejected_rows = []

    for row_number, row in enumerate(reader, start=2):
        total += 1
        name = (row.get("name") or "").strip()
        phone = normalize_phone(row.get("phone") or "")
        address = (row.get("address") or "").strip()
        start_raw = (row.get("start_date") or "").strip()
        plan_name = (row.get("plan") or row.get("plan_name") or "").strip()

        if not name:
            rejected += 1
            rejected_rows.append(ImportRejectedRow(row=row_number, reason="Missing name"))
            continue
        if not phone:
            rejected += 1
            rejected_rows.append(ImportRejectedRow(row=row_number, reason="Missing phone"))
            continue
        if phone in seen:
            duplicates += 1
            continue

        start_date = None
        if start_raw:
            try:
                start_date = parse_date(start_raw)
            except ValueError:
                rejected += 1
                rejected_rows.append(ImportRejectedRow(row=row_number, reason="Invalid date"))
                continue

        if plan_name:
            plan = db.scalar(select(Plan).where(Plan.name.ilike(plan_name)))
            if not plan:
                rejected += 1
                rejected_rows.append(ImportRejectedRow(row=row_number, reason="Unknown plan"))
                continue

        customer = Customer(owner_id=user.id, name=name, phone=phone, address=address)
        db.add(customer)
        db.flush()
        seen.add(phone)
        imported += 1

        # If both start_date and plan are supplied, create a subscription through
        # the end of that calendar month. This makes the import useful while
        # keeping customer-only rows valid.
        if start_date and plan_name:
            from calendar import monthrange
            end_date = date(
                start_date.year, start_date.month,
                monthrange(start_date.year, start_date.month)[1]
            )
            db.add(Subscription(
                customer_id=customer.id,
                plan_id=plan.id,
                start_date=start_date,
                end_date=end_date,
                status="ACTIVE",
            ))

    db.commit()
    return CustomerImportReport(
        total=total,
        imported=imported,
        duplicates=duplicates,
        rejected=rejected,
        rejected_rows=rejected_rows,
    )
