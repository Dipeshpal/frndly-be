import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.auth import AuthResponse, GoogleLoginRequest, LoginRequest, SignupRequest, UserResponse


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
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_to_user_response(user))


async def google_login(db: AsyncSession, data: GoogleLoginRequest) -> AuthResponse:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": data.id_token},
            timeout=10.0,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    payload = resp.json()

    if settings.GOOGLE_CLIENT_ID and payload.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token audience mismatch")

    google_id = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name") or payload.get("email", "").split("@")[0]
    avatar_url = payload.get("picture")

    if not google_id or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incomplete Google profile")

    repo = UserRepository(db)

    user = await repo.get_by_google_id(google_id)
    if not user:
        user = await repo.get_by_email(email)
        if user:
            # Link existing local account to Google
            user = await repo.update(user, google_id=google_id, auth_provider="google", avatar_url=avatar_url)
        else:
            user = await repo.create_google_user(name=name, email=email, google_id=google_id, avatar_url=avatar_url)

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=_to_user_response(user))
