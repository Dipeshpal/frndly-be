from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.secret import CreateSecretRequest, FolderInfo, SecretPreview, SecretResponse, UpdateSecretRequest
from app.services import vault_service

router = APIRouter(prefix="/secrets", tags=["vault"])


@router.get("/folders", response_model=list[FolderInfo])
async def list_folders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await vault_service.list_folders(db, current_user.id)


@router.get("/folders/{folder_name}/preview", response_model=list[SecretPreview])
async def preview_folder(
    folder_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await vault_service.preview_folder(db, current_user.id, folder_name)


@router.delete("/folders/{folder_name}", status_code=204)
async def delete_folder(
    folder_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await vault_service.delete_folder(db, current_user.id, folder_name)


@router.get("", response_model=list[SecretResponse])
async def list_secrets(
    search: str | None = Query(None),
    category: str | None = Query(None),
    folder: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await vault_service.list_secrets(db, current_user.id, search, category, folder)


@router.post("", response_model=SecretResponse, status_code=201)
async def create_secret(
    data: CreateSecretRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await vault_service.create_secret(db, current_user.id, data)


@router.put("/{secret_id}", response_model=SecretResponse)
async def update_secret(
    secret_id: str,
    data: UpdateSecretRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await vault_service.update_secret(db, current_user.id, secret_id, data)


@router.delete("/{secret_id}", status_code=204)
async def delete_secret(
    secret_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await vault_service.delete_secret(db, current_user.id, secret_id)
