from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.secret import Secret


class SecretRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self, user_id: str, search: str | None = None, category: str | None = None
    ) -> list[Secret]:
        q = select(Secret).where(Secret.user_id == user_id)
        if search:
            q = q.where(Secret.name.ilike(f"%{search}%"))
        if category:
            q = q.where(Secret.category == category)
        result = await self.db.execute(q.order_by(Secret.created_at.desc()))
        return list(result.scalars().all())

    async def get(self, user_id: str, secret_id: str) -> Secret | None:
        result = await self.db.execute(
            select(Secret).where(Secret.id == secret_id, Secret.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, name: str, value: str, description: str | None, category: str) -> Secret:
        secret = Secret(user_id=user_id, name=name, value=value, description=description, category=category)
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
