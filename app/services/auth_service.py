from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest, UserResponse


def _to_user_response(user: object) -> UserResponse:
    return UserResponse(
        id=str(user.id),  # type: ignore[attr-defined]
        name=user.name,  # type: ignore[attr-defined]
        email=user.email,  # type: ignore[attr-defined]
        created_at=user.created_at.isoformat(),  # type: ignore[attr-defined]
        updated_at=user.updated_at.isoformat(),  # type: ignore[attr-defined]
    )


async def signup(db: AsyncSession, data: SignupRequest) -> AuthResponse:
    repo = UserRepository(db)
    if await repo.get_by_email(data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await repo.create(data.name, data.email, hash_password(data.password))
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_to_user_response(user))


async def login(db: AsyncSession, data: LoginRequest) -> AuthResponse:
    repo = UserRepository(db)
    user = await repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_to_user_response(user))
