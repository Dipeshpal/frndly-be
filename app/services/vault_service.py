import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.secret_repo import SecretRepository
from app.schemas.secret import CreateSecretRequest, FolderInfo, SecretPreview, SecretResponse, UpdateSecretRequest


def _get_fernet() -> Fernet:
    if settings.VAULT_ENCRYPTION_KEY:
        return Fernet(settings.VAULT_ENCRYPTION_KEY.encode())
    raw = settings.JWT_SECRET_KEY.encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
    return Fernet(key)


def encrypt_value(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_value(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()


def _fmt(secret: object) -> SecretResponse:
    try:
        value = decrypt_value(secret.value)  # type: ignore[attr-defined]
    except (InvalidToken, Exception):
        value = "[encrypted — unreadable: key mismatch]"

    return SecretResponse(
        id=str(secret.id),  # type: ignore[attr-defined]
        name=secret.name,  # type: ignore[attr-defined]
        value=value,
        description=secret.description,  # type: ignore[attr-defined]
        category=secret.category,  # type: ignore[attr-defined]
        folder=secret.folder,  # type: ignore[attr-defined]
        created_at=secret.created_at.isoformat(),  # type: ignore[attr-defined]
        updated_at=secret.updated_at.isoformat(),  # type: ignore[attr-defined]
    )


async def list_secrets(
    db: AsyncSession, user_id: str, search: str | None, category: str | None, folder: str | None = None
) -> list[SecretResponse]:
    repo = SecretRepository(db)
    secrets = await repo.list(user_id, search, category, folder)
    return [_fmt(s) for s in secrets]


async def list_folders(db: AsyncSession, user_id: str) -> list[FolderInfo]:
    repo = SecretRepository(db)
    rows = await repo.list_folders(user_id)
    return [FolderInfo(name=name, count=count) for name, count in rows]


async def preview_folder(db: AsyncSession, user_id: str, folder_name: str) -> list[SecretPreview]:
    repo = SecretRepository(db)
    secrets = await repo.preview_folder(user_id, folder_name)
    return [SecretPreview(id=str(s.id), name=s.name, category=s.category) for s in secrets]


async def delete_folder(db: AsyncSession, user_id: str, folder_name: str) -> int:
    repo = SecretRepository(db)
    return await repo.delete_by_folder(user_id, folder_name)


async def create_secret(db: AsyncSession, user_id: str, data: CreateSecretRequest) -> SecretResponse:
    repo = SecretRepository(db)
    encrypted = encrypt_value(data.value)
    secret = await repo.create(user_id, data.name, encrypted, data.description, data.category, data.folder)
    return _fmt(secret)


async def update_secret(
    db: AsyncSession, user_id: str, secret_id: str, data: UpdateSecretRequest
) -> SecretResponse:
    repo = SecretRepository(db)
    secret = await repo.get(user_id, secret_id)
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    updates = data.model_dump(exclude_none=True)
    if "value" in updates:
        updates["value"] = encrypt_value(updates["value"])
    await repo.update(secret, **updates)
    return _fmt(secret)


async def delete_secret(db: AsyncSession, user_id: str, secret_id: str) -> None:
    repo = SecretRepository(db)
    secret = await repo.get(user_id, secret_id)
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    await repo.delete(secret)
