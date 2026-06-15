from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.clipboard_repo import ClipboardRepository
from app.schemas.clipboard import (
    ClipboardItemResponse,
    ClipboardListResponse,
    CreateClipboardRequest,
)


def _fmt(item: object) -> ClipboardItemResponse:
    return ClipboardItemResponse(
        id=str(item.id),  # type: ignore[attr-defined]
        content=item.content,  # type: ignore[attr-defined]
        device_name=item.device_name,  # type: ignore[attr-defined]
        created_at=item.created_at.isoformat(),  # type: ignore[attr-defined]
    )


async def list_clipboard(
    db: AsyncSession, user_id: str, page: int, per_page: int, search: str | None
) -> ClipboardListResponse:
    repo = ClipboardRepository(db)
    items, total = await repo.list(user_id, page, per_page, search)
    return ClipboardListResponse(items=[_fmt(i) for i in items], total=total, page=page, per_page=per_page)


async def create_clipboard(db: AsyncSession, user_id: str, data: CreateClipboardRequest) -> ClipboardItemResponse:
    repo = ClipboardRepository(db)
    item = await repo.create(user_id, data.content, data.device_name)
    return _fmt(item)


async def delete_clipboard(db: AsyncSession, user_id: str, item_id: str) -> None:
    from fastapi import HTTPException, status
    repo = ClipboardRepository(db)
    deleted = await repo.delete(user_id, item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
