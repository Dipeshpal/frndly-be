from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.repositories.device_repo import DeviceRepository
from app.schemas.device import DeviceOut, RegisterDeviceRequest

_ONLINE_THRESHOLD = timedelta(seconds=60)


def _fmt(device: Device) -> DeviceOut:
    now = datetime.now(timezone.utc)
    last_seen_dt = device.last_seen if device.last_seen.tzinfo else device.last_seen.replace(tzinfo=timezone.utc)
    online = (now - last_seen_dt) < _ONLINE_THRESHOLD
    return DeviceOut(
        id=str(device.id),
        device_id=device.device_id,
        name=device.name,
        os_type=device.os_type,
        device_type=device.device_type,
        last_seen=last_seen_dt.isoformat(),
        online=online,
        created_at=device.created_at.isoformat() if device.created_at.tzinfo else device.created_at.replace(tzinfo=timezone.utc).isoformat(),
    )


async def register_device(db: AsyncSession, user_id: str, data: RegisterDeviceRequest) -> DeviceOut:
    repo = DeviceRepository(db)
    device = await repo.upsert(user_id, data.device_id, data.name, data.os_type, data.device_type)
    return _fmt(device)


async def heartbeat(db: AsyncSession, user_id: str, device_id: str) -> DeviceOut | None:
    repo = DeviceRepository(db)
    device = await repo.heartbeat(user_id, device_id)
    return _fmt(device) if device else None


async def list_devices(db: AsyncSession, user_id: str) -> list[DeviceOut]:
    repo = DeviceRepository(db)
    devices = await repo.list(user_id)
    return [_fmt(d) for d in devices]


async def delete_device(db: AsyncSession, user_id: str, device_id: str) -> bool:
    repo = DeviceRepository(db)
    return await repo.delete(user_id, device_id)
