from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.secret import Secret


class SecretRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self,
        user_id: str,
        search: str | None = None,
        category: str | None = None,
        folder: str | None = None,
    ) -> list[Secret]:
        q = select(Secret).where(Secret.user_id == user_id)
        if search:
            q = q.where(Secret.name.ilike(f"%{search}%"))
        if category:
            q = q.where(Secret.category == category)
        if folder:
            q = q.where(Secret.folder == folder)
        result = await self.db.execute(q.order_by(Secret.created_at.desc()))
        return list(result.scalars().all())

    async def list_folders(self, user_id: str) -> list[tuple[str, int]]:
        q = (
            select(Secret.folder, func.count(Secret.id).label("count"))
            .where(Secret.user_id == user_id)
            .group_by(Secret.folder)
            .order_by(Secret.folder)
        )
        result = await self.db.execute(q)
        return [(row.folder, row.count) for row in result.all()]

    async def preview_folder(self, user_id: str, folder: str, limit: int = 5) -> list[Secret]:
        q = (
            select(Secret)
            .where(Secret.user_id == user_id, Secret.folder == folder)
            .order_by(Secret.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def delete_by_folder(self, user_id: str, folder: str) -> int:
        from sqlalchemy import delete as sa_delete
        result = await self.db.execute(
            sa_delete(Secret).where(Secret.user_id == user_id, Secret.folder == folder)
        )
        await self.db.commit()
        return result.rowcount

    async def get(self, user_id: str, secret_id: str) -> Secret | None:
        result = await self.db.execute(
            select(Secret).where(Secret.id == secret_id, Secret.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, user_id: str, name: str, value: str, description: str | None, category: str, folder: str = "General"
    ) -> Secret:
        secret = Secret(user_id=user_id, name=name, value=value, description=description, category=category, folder=folder)
        self.db.add(secret)
        await self.db.commit()
        await self.db.refresh(secret)
        return secret

    async def update(self, secret: Secret, **kwargs: object) -> Secret:
        for key, value in kwargs.items():
            setattr(secret, key, value)
        await self.db.commit()
        await self.db.refresh(secret)
        return secret

    async def delete(self, secret: Secret) -> None:
        await self.db.delete(secret)
        await self.db.commit()
