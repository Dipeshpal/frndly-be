from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.folder import CreateFolderRequest, FolderResponse, UpdateFolderRequest
from app.services import folder_service

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("", response_model=list[FolderResponse])
async def list_folders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await folder_service.list_folders(db, current_user.id)


@router.post("", response_model=FolderResponse, status_code=201)
async def create_folder(
    data: CreateFolderRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await folder_service.create_folder(db, current_user.id, data)


@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: str,
    data: UpdateFolderRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await folder_service.update_folder(db, current_user.id, folder_id, data)


@router.delete("/{folder_id}", status_code=204)
async def delete_folder(
    folder_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await folder_service.delete_folder(db, current_user.id, folder_id)
