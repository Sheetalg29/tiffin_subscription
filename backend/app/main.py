from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from . import models
from .routers import auth, billing, customers, dashboard, plans, subscriptions

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0", description="Subscription and pro-rated billing API for tiffin businesses")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(plans.router)
app.include_router(subscriptions.router)
app.include_router(billing.router)
app.include_router(dashboard.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "tiffinflow-api"}
