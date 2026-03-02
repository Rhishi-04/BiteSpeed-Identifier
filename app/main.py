"""
FastAPI app: mount routers and create tables on startup.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.models import Contact  # noqa: F401 - so Contact table is registered
from app.routers import identify

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (like Base.metadata.create_all)
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown if needed


app = FastAPI(title="Bitespeed Identify", lifespan=lifespan, redirect_slashes=False)

app.include_router(identify.router, prefix="/identify", tags=["identify"])


@app.get("/")
def root():
    return {"ok": True, "message": "Bitespeed identify API"}
