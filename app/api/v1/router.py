from fastapi import APIRouter

from app.api.v1 import auth, clipboard, users, vault

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(clipboard.router)
api_router.include_router(vault.router)
api_router.include_router(users.router)
