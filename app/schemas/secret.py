from typing import Literal

from pydantic import BaseModel

SecretCategory = Literal["api_key", "database", "cloud", "personal", "other"]


class CreateSecretRequest(BaseModel):
    name: str
    value: str
    description: str | None = None
    category: SecretCategory = "other"
    folder: str = "General"


class UpdateSecretRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: SecretCategory | None = None
    folder: str | None = None


class SecretResponse(BaseModel):
    id: str
    name: str
    value: str
    description: str | None
    category: str
    folder: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class FolderInfo(BaseModel):
    name: str
    count: int


class SecretPreview(BaseModel):
    id: str
    name: str
    category: str
