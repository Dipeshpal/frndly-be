import random
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.clipboard import ClipboardItem
from app.models.secret import Secret
from app.models.user import User
from app.schemas.dashboard import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Sync activity bytes
    clipboard_len_q = select(func.coalesce(func.sum(func.length(ClipboardItem.content)), 0)).where(ClipboardItem.user_id == current_user.id)
    secret_len_q = select(func.coalesce(func.sum(func.length(Secret.value)), 0)).where(Secret.user_id == current_user.id)
    
    clipboard_len_res = await db.execute(clipboard_len_q)
    secret_len_res = await db.execute(secret_len_q)
    
    sync_activity_bytes = clipboard_len_res.scalar() + secret_len_res.scalar()
    
    # 2. Encrypted vaults count
    secret_count_q = select(func.count(Secret.id)).where(Secret.user_id == current_user.id)
    secret_count_res = await db.execute(secret_count_q)
    encrypted_vaults_count = secret_count_res.scalar()
    
    # 3. Linked nodes count
    device_count_q = select(func.count(func.distinct(ClipboardItem.device_name))).where(ClipboardItem.user_id == current_user.id)
    device_count_res = await db.execute(device_count_q)
    linked_nodes_count = device_count_res.scalar()
    
    # 4. Request speed ms (Mocked)
    request_speed_ms = random.randint(25, 45)
    
    return DashboardStatsResponse(
        sync_activity_bytes=sync_activity_bytes,
        encrypted_vaults_count=encrypted_vaults_count,
        linked_nodes_count=linked_nodes_count,
        request_speed_ms=request_speed_ms,
    )
