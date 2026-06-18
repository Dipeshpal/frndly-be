from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    sync_activity_bytes: int
    encrypted_vaults_count: int
    linked_nodes_count: int
    request_speed_ms: int
    active_clips_count: int
    security_level: str
    daily_notifications_count: int
    daily_clipboard_items_count: int
    daily_vault_items_count: int
