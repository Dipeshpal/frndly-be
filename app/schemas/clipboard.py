from pydantic import BaseModel


class CreateClipboardRequest(BaseModel):
    content: str
    device_name: str = "Unknown"


class ClipboardItemResponse(BaseModel):
    id: str
    content: str
    device_name: str
    created_at: str

    model_config = {"from_attributes": True}


class ClipboardListResponse(BaseModel):
    items: list[ClipboardItemResponse]
    total: int
    page: int
    per_page: int

class DeviceResponse(BaseModel):
    device_name: str
    last_active: str
    is_current_session: bool = False

