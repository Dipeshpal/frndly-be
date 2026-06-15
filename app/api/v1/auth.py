from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest, UpdateProfileRequest, UserResponse
from app.services import auth_service
from app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.signup(db, data)


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, data)


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat(),
    )
