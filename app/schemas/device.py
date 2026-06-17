from pydantic import BaseModel


class RegisterDeviceRequest(BaseModel):
    device_id: str
    name: str
    os_type: str = "unknown"
    device_type: str = "unknown"


class DeviceOut(BaseModel):
    id: str
    device_id: str
    name: str
    os_type: str
    device_type: str
    last_seen: str
    online: bool
    created_at: str

    model_config = {"from_attributes": True}
