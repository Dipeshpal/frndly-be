from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.note import CreateNoteRequest, NoteListResponse, NoteResponse, UpdateNoteRequest
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=NoteListResponse)
async def list_notes(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    tag: str | None = Query(None),
    folder_id: str | None = Query(None),
    all_notes: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await note_service.list_notes(
        db, current_user.id, page, per_page, search, tag,
        folder_id=folder_id if not all_notes else None,
        unfiltered=all_notes,
    )


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(
    data: CreateNoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await note_service.create_note(db, current_user.id, data)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await note_service.get_note(db, current_user.id, note_id)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    data: UpdateNoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await note_service.update_note(db, current_user.id, note_id, data)


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await note_service.delete_note(db, current_user.id, note_id)
