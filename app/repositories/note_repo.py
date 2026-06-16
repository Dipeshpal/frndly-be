from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


class NoteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_notes(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 50,
        search: str | None = None,
        tag: str | None = None,
        folder_id: str | None = None,
        unfiltered: bool = False,
    ) -> tuple[list[Note], int]:
        q = select(Note).where(Note.user_id == user_id)
        if not unfiltered:
            if folder_id:
                q = q.where(Note.folder_id == folder_id)
            else:
                q = q.where(Note.folder_id.is_(None))
        if search:
            q = q.where(or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%"),
            ))
        if tag:
            q = q.where(Note.tags.contains([tag]))
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar_one()
        q = q.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        result = await self.db.execute(q.offset((page - 1) * per_page).limit(per_page))
        return list(result.scalars().all()), total

    async def get(self, user_id: str, note_id: str) -> Note | None:
        result = await self.db.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: str,
        title: str,
        content: str,
        tags: list[str],
        is_pinned: bool,
        folder_id: str | None = None,
    ) -> Note:
        note = Note(
            user_id=user_id,
            title=title,
            content=content,
            tags=tags,
            is_pinned=is_pinned,
            folder_id=folder_id,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def update(self, note: Note, **kwargs) -> Note:
        for key, value in kwargs.items():
            setattr(note, key, value)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete(self, note: Note) -> None:
        await self.db.delete(note)
        await self.db.commit()
