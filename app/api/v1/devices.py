from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.device import DeviceOut, RegisterDeviceRequest
from app.services import device_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceOut, status_code=200)
async def register_device(
    data: RegisterDeviceRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await device_service.register_device(db, current_user.id, data)


@router.post("/{device_id}/heartbeat", response_model=DeviceOut)
async def heartbeat(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    device = await device_service.heartbeat(db, current_user.id, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.get("", response_model=list[DeviceOut])
async def list_devices(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await device_service.list_devices(db, current_user.id)


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = await device_service.delete_device(db, current_user.id, device_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
