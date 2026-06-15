from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.alert_repo import AlertRepository
from app.schemas.alert import AlertCreate, AlertResponse

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[AlertResponse]:
    repo = AlertRepository(db)
    return await repo.list_alerts(current_user.id)


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_in: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    repo = AlertRepository(db)
    return await repo.create_alert(current_user.id, alert_in)
