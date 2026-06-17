import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401 — ensure all models are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only run startup for local development, not serverless
    if os.getenv("VERCEL") is None:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"'))
                await conn.execute(text(f'SET search_path TO "{settings.DB_SCHEMA}"'))
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
    yield


app = FastAPI(
    title="Frndly API",
    description="Cross-device clipboard and secret vault",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
