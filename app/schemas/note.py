from pydantic import BaseModel, Field


class CreateNoteRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    tags: list[str] = []
    is_pinned: bool = False
    folder_id: str | None = None


class UpdateNoteRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    tags: list[str] | None = None
    is_pinned: bool | None = None
    folder_id: str | None = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]
    is_pinned: bool
    folder_id: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
    page: int
    per_page: int
