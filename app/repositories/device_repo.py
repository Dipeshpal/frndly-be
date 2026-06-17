from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DeviceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert(self, user_id: str, device_id: str, name: str, os_type: str, device_type: str) -> Device:
        now = _utcnow()
        stmt = (
            insert(Device)
            .values(
                user_id=user_id,
                device_id=device_id,
                name=name,
                os_type=os_type,
                device_type=device_type,
                last_seen=now,
                created_at=now,
            )
            .on_conflict_do_update(
                constraint="uq_user_device",
                set_={"name": name, "os_type": os_type, "device_type": device_type, "last_seen": now},
            )
            .returning(Device)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        row = result.scalar_one()
        return row

    async def heartbeat(self, user_id: str, device_id: str) -> Device | None:
        now = _utcnow()
        stmt = (
            update(Device)
            .where(Device.user_id == user_id, Device.device_id == device_id)
            .values(last_seen=now)
            .returning(Device)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def list(self, user_id: str) -> list[Device]:
        result = await self.db.execute(
            select(Device).where(Device.user_id == user_id).order_by(Device.last_seen.desc())
        )
        return list(result.scalars().all())

    async def delete(self, user_id: str, device_id: str) -> bool:
        result = await self.db.execute(
            select(Device).where(Device.user_id == user_id, Device.device_id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            return False
        await self.db.delete(device)
        await self.db.commit()
        return True
