from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import Folder
from app.models.note import Note


class FolderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_folders(self, user_id: str) -> list[Folder]:
        result = await self.db.execute(
            select(Folder)
            .where(Folder.user_id == user_id)
            .order_by(Folder.parent_id.is_(None).desc(), Folder.name)
        )
        return list(result.scalars().all())

    async def get(self, user_id: str, folder_id: str) -> Folder | None:
        result = await self.db.execute(
            select(Folder).where(Folder.id == folder_id, Folder.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, name: str, parent_id: str | None) -> Folder:
        folder = Folder(user_id=user_id, name=name, parent_id=parent_id)
        self.db.add(folder)
        await self.db.commit()
        await self.db.refresh(folder)
        return folder

    async def update(self, folder: Folder, **kwargs) -> Folder:
        for key, value in kwargs.items():
            setattr(folder, key, value)
        await self.db.commit()
        await self.db.refresh(folder)
        return folder

    async def delete(self, folder: Folder) -> None:
        # Unfile all notes in this folder before deleting
        await self.db.execute(
            update(Note).where(Note.folder_id == folder.id).values(folder_id=None)
        )
        await self.db.delete(folder)
        await self.db.commit()
