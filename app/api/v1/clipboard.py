from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.clipboard import ClipboardItemResponse, ClipboardListResponse, CreateClipboardRequest, DeviceResponse
from app.services import clipboard_service

router = APIRouter(prefix="/clipboard", tags=["clipboard"])


@router.get("", response_model=ClipboardListResponse)
async def list_clipboard(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await clipboard_service.list_clipboard(db, current_user.id, page, per_page, search, date)


@router.post("", response_model=ClipboardItemResponse, status_code=201)
async def create_clipboard(
    data: CreateClipboardRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await clipboard_service.create_clipboard(db, current_user.id, data)


@router.delete("/{item_id}", status_code=204)
async def delete_clipboard(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await clipboard_service.delete_clipboard(db, current_user.id, item_id)


@router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await clipboard_service.list_devices(db, current_user.id)
