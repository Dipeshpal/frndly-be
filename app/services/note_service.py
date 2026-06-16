from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.repositories.note_repo import NoteRepository
from app.schemas.note import CreateNoteRequest, NoteListResponse, NoteResponse, UpdateNoteRequest


def _fmt(note: Note) -> NoteResponse:
    return NoteResponse(
        id=str(note.id),
        title=note.title,
        content=note.content,
        tags=list(note.tags or []),
        is_pinned=note.is_pinned,
        folder_id=note.folder_id,
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat(),
    )


async def list_notes(
    db: AsyncSession,
    user_id: str,
    page: int,
    per_page: int,
    search: str | None,
    tag: str | None,
    folder_id: str | None = None,
    unfiltered: bool = False,
) -> NoteListResponse:
    repo = NoteRepository(db)
    items, total = await repo.list_notes(user_id, page, per_page, search, tag, folder_id, unfiltered)
    return NoteListResponse(items=[_fmt(n) for n in items], total=total, page=page, per_page=per_page)


async def get_note(db: AsyncSession, user_id: str, note_id: str) -> NoteResponse:
    repo = NoteRepository(db)
    note = await repo.get(user_id, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return _fmt(note)


async def create_note(db: AsyncSession, user_id: str, data: CreateNoteRequest) -> NoteResponse:
    repo = NoteRepository(db)
    note = await repo.create(user_id, data.title, data.content, data.tags, data.is_pinned, data.folder_id)
    return _fmt(note)


async def update_note(
    db: AsyncSession, user_id: str, note_id: str, data: UpdateNoteRequest
) -> NoteResponse:
    repo = NoteRepository(db)
    note = await repo.get(user_id, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    updates = data.model_dump(exclude_none=True)
    note = await repo.update(note, **updates)
    return _fmt(note)


async def delete_note(db: AsyncSession, user_id: str, note_id: str) -> None:
    repo = NoteRepository(db)
    note = await repo.get(user_id, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await repo.delete(note)
