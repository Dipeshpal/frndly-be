from datetime import datetime, time, timezone
import random
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.clipboard import ClipboardItem
from app.models.secret import Secret
from app.models.alert import Alert
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
    
    # 5. Active clips count
    active_clips_q = select(func.count(ClipboardItem.id)).where(ClipboardItem.user_id == current_user.id)
    active_clips_res = await db.execute(active_clips_q)
    active_clips_count = active_clips_res.scalar()
    
    # 6. Security level
    if encrypted_vaults_count >= 5 and linked_nodes_count >= 1:
        security_level = "A+"
    elif encrypted_vaults_count >= 1:
        security_level = "A"
    else:
        security_level = "B"
        
    # 7. Daily counts
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    
    daily_alerts_q = select(func.count(Alert.id)).where(Alert.user_id == current_user.id, Alert.received_at >= today_start)
    daily_alerts_res = await db.execute(daily_alerts_q)
    daily_notifications_count = daily_alerts_res.scalar()
    
    daily_clips_q = select(func.count(ClipboardItem.id)).where(ClipboardItem.user_id == current_user.id, ClipboardItem.created_at >= today_start)
    daily_clips_res = await db.execute(daily_clips_q)
    daily_clipboard_items_count = daily_clips_res.scalar()
    
    daily_vault_q = select(func.count(Secret.id)).where(Secret.user_id == current_user.id, Secret.created_at >= today_start)
    daily_vault_res = await db.execute(daily_vault_q)
    daily_vault_items_count = daily_vault_res.scalar()

    return DashboardStatsResponse(
        sync_activity_bytes=sync_activity_bytes,
        encrypted_vaults_count=encrypted_vaults_count,
        linked_nodes_count=linked_nodes_count,
        request_speed_ms=request_speed_ms,
        active_clips_count=active_clips_count,
        security_level=security_level,
        daily_notifications_count=daily_notifications_count,
        daily_clipboard_items_count=daily_clipboard_items_count,
        daily_vault_items_count=daily_vault_items_count,
    )
