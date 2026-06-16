from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import Folder
from app.repositories.folder_repo import FolderRepository
from app.schemas.folder import CreateFolderRequest, FolderResponse, UpdateFolderRequest


def _fmt(folder: Folder) -> FolderResponse:
    return FolderResponse(
        id=str(folder.id),
        name=folder.name,
        parent_id=folder.parent_id,
        created_at=folder.created_at.isoformat(),
        updated_at=folder.updated_at.isoformat(),
    )


async def list_folders(db: AsyncSession, user_id: str) -> list[FolderResponse]:
    repo = FolderRepository(db)
    folders = await repo.list_folders(user_id)
    return [_fmt(f) for f in folders]


async def create_folder(db: AsyncSession, user_id: str, data: CreateFolderRequest) -> FolderResponse:
    repo = FolderRepository(db)
    folder = await repo.create(user_id, data.name, data.parent_id)
    return _fmt(folder)


async def update_folder(
    db: AsyncSession, user_id: str, folder_id: str, data: UpdateFolderRequest
) -> FolderResponse:
    repo = FolderRepository(db)
    folder = await repo.get(user_id, folder_id)
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    updates = data.model_dump(exclude_none=True)
    folder = await repo.update(folder, **updates)
    return _fmt(folder)


async def delete_folder(db: AsyncSession, user_id: str, folder_id: str) -> None:
    repo = FolderRepository(db)
    folder = await repo.get(user_id, folder_id)
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    await repo.delete(folder)
