from fastapi import APIRouter

from app.api.v1 import auth, clipboard, users, vault, dashboard, alerts, notes, folders

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(clipboard.router)
api_router.include_router(vault.router)
api_router.include_router(users.router)
api_router.include_router(dashboard.router)
api_router.include_router(alerts.router)
api_router.include_router(notes.router)
api_router.include_router(folders.router)
