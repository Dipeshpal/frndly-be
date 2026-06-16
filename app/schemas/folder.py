from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: str | None = None


class UpdateFolderRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    parent_id: str | None = None


class FolderResponse(BaseModel):
    id: str
    name: str
    parent_id: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
