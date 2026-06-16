from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.dependencies import get_db, get_current_user
from src.models.user import User
from src.services.device_service import DeviceService
from pydantic import BaseModel

router = APIRouter(prefix="/devices", tags=["devices"])


class RegisterDeviceRequest(BaseModel):
    device_id: str
    name: str
    os_type: str
    device_type: str


class DeviceResponse(BaseModel):
    id: str
    name: str
    os_type: str
    device_type: str
    last_seen: str
    online: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=DeviceResponse)
def register_device(
    req: RegisterDeviceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    device = DeviceService.register_device(
        db=db,
        user_id=current_user.id,
        device_id=req.device_id,
        name=req.name,
        os_type=req.os_type,
        device_type=req.device_type,
    )
    return device.to_dict()


@router.get("", response_model=list[DeviceResponse])
def list_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    devices = DeviceService.get_devices_for_user(db=db, user_id=current_user.id)
    return [device.to_dict() for device in devices]


@router.post("/{device_id}/heartbeat", response_model=DeviceResponse)
def heartbeat(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    device = DeviceService.heartbeat(db=db, device_id=device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")
    return device.to_dict()


@router.delete("/{device_id}")
def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    device = db.query(db.query(Device).filter_by(device_id=device_id).first().__class__).filter_by(device_id=device_id).first()
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")

    DeviceService.delete_device(db=db, device_id=device_id)
    return {"message": "Device deleted"}
