import base64
import os

from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.secret_repo import SecretRepository
from app.schemas.secret import CreateSecretRequest, SecretResponse, UpdateSecretRequest


def _get_fernet() -> Fernet:
    # Derive a 32-byte Fernet key from JWT_SECRET_KEY
    raw = settings.JWT_SECRET_KEY.encode()
    padded = (raw * ((32 // len(raw)) + 1))[:32]
    key = base64.urlsafe_b64encode(padded)
    return Fernet(key)


def encrypt_value(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_value(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()


def _fmt(secret: object) -> SecretResponse:
    return SecretResponse(
        id=str(secret.id),  # type: ignore[attr-defined]
        name=secret.name,  # type: ignore[attr-defined]
        value=decrypt_value(secret.value),  # type: ignore[attr-defined]
        description=secret.description,  # type: ignore[attr-defined]
        category=secret.category,  # type: ignore[attr-defined]
        created_at=secret.created_at.isoformat(),  # type: ignore[attr-defined]
        updated_at=secret.updated_at.isoformat(),  # type: ignore[attr-defined]
    )


async def list_secrets(
    db: AsyncSession, user_id: str, search: str | None, category: str | None
) -> list[SecretResponse]:
    repo = SecretRepository(db)
    secrets = await repo.list(user_id, search, category)
    return [_fmt(s) for s in secrets]


async def create_secret(db: AsyncSession, user_id: str, data: CreateSecretRequest) -> SecretResponse:
    repo = SecretRepository(db)
    encrypted = encrypt_value(data.value)
    secret = await repo.create(user_id, data.name, encrypted, data.description, data.category)
    return _fmt(secret)


async def update_secret(
    db: AsyncSession, user_id: str, secret_id: str, data: UpdateSecretRequest
) -> SecretResponse:
    repo = SecretRepository(db)
    secret = await repo.get(user_id, secret_id)
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    updates = data.model_dump(exclude_none=True)
    await repo.update(secret, **updates)
    return _fmt(secret)


async def delete_secret(db: AsyncSession, user_id: str, secret_id: str) -> None:
    repo = SecretRepository(db)
    secret = await repo.get(user_id, secret_id)
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    await repo.delete(secret)
