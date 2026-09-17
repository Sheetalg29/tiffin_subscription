# REASONING

## 1. Problem understanding

The product needs to manage a tiffin subscription lifecycle: subscribe → pause/resume → calculate the monthly bill → search the customer and view active/paused status.

## 2. Architecture choice

A React frontend communicates with a FastAPI REST API. PostgreSQL is the intended persistent production database. SQLAlchemy keeps database operations separated from HTTP routes. A SQLite default is included only to make the repository runnable immediately in environments where PostgreSQL is not installed; Docker Compose provides PostgreSQL for the intended setup.

## 3. Data model

Customers, plans, subscriptions, pause periods and bills are separate entities because each has a different lifecycle. A subscription points to a customer and a plan. Pause periods belong to a subscription. Generated bills snapshot the calculated values for a month.

## 4. Billing design

Billing is calculated from weekday service dates, not calendar days. The subscription is intersected with the requested billing month. Pause periods are clipped to the subscription period and converted into a set of dates. Using a set prevents overlapping pauses from double-counting a service day.

Formula:

`served_days = total_service_days - paused_service_days`

`amount = monthly_price * served_days / total_service_days`

## 5. Authentication

Owner passwords are never stored in plaintext. Each password is salted and hashed with Python's scrypt implementation. JWT access tokens identify the owner for protected REST endpoints.

## 6. Search, pagination and sorting

The customer list supports a search term against name/phone, page/limit parameters and a restricted sort-column map. This avoids accepting arbitrary SQL column names from the client.

## 7. Edge cases tested

- No pause: full monthly amount.
- Pause on weekdays: those service days are excluded.
- Pause spanning a weekend: weekend dates are ignored because they are not service days.
- Multiple pauses.
- Overlapping pauses: dates are stored in a set, so duplicates are removed.
- Pause outside the subscription: no effect on the billing period.
- Mid-month subscriptions: the billing period is clipped to the subscription dates.

## 8. Known product decisions

The MVP assumes a Monday–Friday lunch service. A future holiday/calendar table can make service days configurable. Resume removes a currently active pause; a future version can model explicit pause state transitions and audit events.

## 9. Validation

FastAPI/Pydantic validates request shapes. Database constraints protect unique customer phones per owner and one generated bill per subscription/month. Billing logic is isolated in `services/billing_service.py` so it can be tested independently of the UI.

## 10. Debug/fix log

Initial implementation risk: treating every calendar date as billable. The final implementation first generates weekday service dates and then intersects those dates with pause periods.

Another risk: overlapping pauses causing duplicate deductions. The final implementation uses a Python set of paused dates, so overlapping ranges cannot double-count.

## 11. Submission preparation

Before final submission, run the backend tests, build the frontend, verify registration/login, customer search, pagination/sorting, subscription creation, pause/resume and bill generation through the deployed UI, and fill `AI_LOGS.md` with the exact unmodified AI transcript requested by the evaluator.
