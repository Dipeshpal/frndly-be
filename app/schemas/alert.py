from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    title: str
    message: str
    source_app: str | None = None
    device_name: str | None = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: str
    user_id: str
    received_at: datetime
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
