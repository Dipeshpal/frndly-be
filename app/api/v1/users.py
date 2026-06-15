from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import UpdateProfileRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = UserRepository(db)
    updates = data.model_dump(exclude_none=True)
    if updates:
        current_user = await repo.update(current_user, **updates)
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat(),
    )
