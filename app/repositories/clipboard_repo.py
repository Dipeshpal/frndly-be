from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clipboard import ClipboardItem


class ClipboardRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self, user_id: str, page: int = 1, per_page: int = 50, search: str | None = None
    ) -> tuple[list[ClipboardItem], int]:
        q = select(ClipboardItem).where(ClipboardItem.user_id == user_id)
        if search:
            q = q.where(ClipboardItem.content.ilike(f"%{search}%"))
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar_one()
        items = (
            await self.db.execute(
                q.order_by(ClipboardItem.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        ).scalars().all()
        return list(items), total

    async def create(self, user_id: str, content: str, device_name: str) -> ClipboardItem:
        item = ClipboardItem(user_id=user_id, content=content, device_name=device_name)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, user_id: str, item_id: str) -> bool:
        result = await self.db.execute(
            select(ClipboardItem).where(ClipboardItem.id == item_id, ClipboardItem.user_id == user_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return False
        await self.db.delete(item)
        await self.db.commit()
        return True
