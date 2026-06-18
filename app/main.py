import os
from contextlib import asynccontextmanager
from urllib.parse import urlparse, urlunparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, _get_async_database_url
import app.models  # noqa: F401 — ensure all models are registered


async def _ensure_database_exists():
    db_url = _get_async_database_url(settings.DATABASE_URL)
    parsed = urlparse(db_url)
    db_name = parsed.path.lstrip("/")

    maintenance_url = urlunparse(
        (parsed.scheme, parsed.netloc, "/postgres", "", "", "")
    )

    try:
        maint_engine = create_async_engine(maintenance_url, echo=False)
        async with maint_engine.begin() as conn:
            await conn.execute(text(f'CREATE DATABASE IF NOT EXISTS "{db_name}"'))
        await maint_engine.dispose()
    except Exception as e:
        print(f"Warning: Could not create database: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only run startup for local development, not serverless
    if os.getenv("VERCEL") is None:
        try:
            await _ensure_database_exists()
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
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
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
