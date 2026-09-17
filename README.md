# TiffinFlow — Tiffin Subscription & Billing Management

TiffinFlow is a full-stack web product for home-style tiffin/lunch businesses. Owners can register, manage customers, create monthly subscriptions, pause/resume customers, search by phone, and calculate pro-rated bills only for weekday service days that were actually served.

## Product

**Target audience:** small tiffin businesses and local meal-subscription operators.

**Core rule:**

`served days = service weekdays - paused service weekdays`

`bill = monthly plan price × served days / total service weekdays`

Overlapping pause periods are merged through a set of dates, so a day is never double-counted.

## Stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: PostgreSQL (Docker Compose) / SQLite fallback for quick local demo
- ORM: SQLAlchemy
- Authentication: JWT + salted scrypt password hashing
- Tests: PyTest

## Architecture

```text
React/Vite UI → FastAPI REST API → SQLAlchemy → PostgreSQL
                         ↓
                 Billing service
```

## Features

- Owner registration and login
- JWT-protected dashboard
- Customer CRUD and phone/name search
- Pagination and sorting
- Monthly plans
- Subscriptions
- Pause/resume
- Weekday-aware pro-rated billing
- Bill history
- Dashboard metrics
- Public landing page

## API Endpoints

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register owner |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current owner |

### Customers

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/customers` | Create customer |
| GET | `/api/customers` | List, search, paginate, sort |
| GET | `/api/customers/search?phone=` | Phone lookup |
| GET | `/api/customers/{id}` | Customer details |
| PUT | `/api/customers/{id}` | Update customer |
| DELETE | `/api/customers/{id}` | Delete customer |

### Plans

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/plans` | Create plan |
| GET | `/api/plans` | List active plans |

### Subscriptions

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/subscriptions` | Create subscription |
| GET | `/api/subscriptions` | List subscriptions |
| GET | `/api/subscriptions/{id}` | Subscription details |
| POST | `/api/subscriptions/{id}/pause` | Add pause period |
| POST | `/api/subscriptions/{id}/resume` | Remove current pause |

### Billing

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/bills/calculate/{subscription_id}?month=YYYY-MM` | Preview bill |
| POST | `/api/bills/generate/{subscription_id}?month=YYYY-MM` | Generate/store bill |
| GET | `/api/bills` | Bill history with pagination |

### Dashboard

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/dashboard/summary` | Customer/status/revenue summary |

## Database Schema

```text
users
  └── customers
        └── subscriptions ── plans
                ├── pause_periods
                └── bills
```

Main tables: `users`, `customers`, `plans`, `subscriptions`, `pause_periods`, `bills`.

## Local setup — Codespaces / Linux / macOS

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

For a real PostgreSQL database, set `DATABASE_URL` in `.env` to:

```text
postgresql+psycopg://tiffinflow:tiffinflow@localhost:5432/tiffinflow
```

For a quick no-Postgres demo, leave `DATABASE_URL` unset; the default is a local SQLite file.

Run:

```bash
uvicorn app.main:app --reload --port 8000
python seed.py
```

API docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

### Demo account

```text
Email: demo@tiffinflow.app
Password: Demo@1234
```

Run `python seed.py` before using the demo account.

## PostgreSQL with Docker

```bash
docker compose up -d db
```

Then set `DATABASE_URL` as above and start the backend.

## Tests

From `backend/`:

```bash
pytest -q
```

The billing tests cover full-month billing, weekday pauses, and overlapping pause periods.

## Environment variables

Backend:

```text
DATABASE_URL=postgresql+psycopg://...
SECRET_KEY=long-random-secret
CORS_ORIGINS=http://localhost:5173
```

Frontend:

```text
VITE_API_URL=http://localhost:8000/api
```

## Deployment

A simple deployment can use a managed PostgreSQL database, Render/Fly.io/etc. for FastAPI, and Vercel/Netlify/etc. for the React frontend. Configure environment variables on the hosting platforms rather than committing secrets.

## Three next features

1. Online payments.
2. WhatsApp bill/pause notifications.
3. Daily delivery tracking.

## Evaluation notes

`README.md`, `REASONING.md`, and `AI_LOGS.md` are intentionally kept in the repository root as requested by the assignment. Before submission, `AI_LOGS.md` must be replaced/filled with the exact unmodified AI transcript required by the evaluator.
