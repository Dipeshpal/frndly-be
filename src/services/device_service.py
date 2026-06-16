from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from src.models.device import Device


class DeviceService:
    @staticmethod
    def register_device(
        db: Session,
        user_id: str,
        device_id: str,
        name: str,
        os_type: str,
        device_type: str,
    ) -> Device:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if device:
            device.last_seen = datetime.utcnow()
            device.name = name
            device.os_type = os_type
            device.device_type = device_type
        else:
            device = Device(
                id=str(uuid4()),
                user_id=user_id,
                device_id=device_id,
                name=name,
                os_type=os_type,
                device_type=device_type,
                last_seen=datetime.utcnow(),
            )
            db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def heartbeat(db: Session, device_id: str) -> Device | None:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if device:
            device.last_seen = datetime.utcnow()
            db.commit()
            db.refresh(device)
        return device

    @staticmethod
    def get_devices_for_user(db: Session, user_id: str) -> list[Device]:
        return db.query(Device).filter_by(user_id=user_id).order_by(Device.last_seen.desc()).all()

    @staticmethod
    def delete_device(db: Session, device_id: str) -> bool:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if device:
            db.delete(device)
            db.commit()
            return True
        return False
