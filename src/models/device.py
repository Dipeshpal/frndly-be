from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    device_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    os_type = Column(String(50), nullable=False)
    device_type = Column(String(50), nullable=False)
    last_seen = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="devices")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_device_id", "device_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "os_type": self.os_type,
            "device_type": self.device_type,
            "last_seen": self.last_seen.isoformat(),
            "online": (datetime.utcnow() - self.last_seen).total_seconds() < 300,
            "created_at": self.created_at.isoformat(),
        }
