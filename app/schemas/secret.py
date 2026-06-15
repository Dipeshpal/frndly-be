from typing import Literal

from pydantic import BaseModel

SecretCategory = Literal["api_key", "database", "cloud", "personal", "other"]


class CreateSecretRequest(BaseModel):
    name: str
    value: str
    description: str | None = None
    category: SecretCategory = "other"


class UpdateSecretRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: SecretCategory | None = None


class SecretResponse(BaseModel):
    id: str
    name: str
    value: str
    description: str | None
    category: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
