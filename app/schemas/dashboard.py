from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    sync_activity_bytes: int
    encrypted_vaults_count: int
    linked_nodes_count: int
    request_speed_ms: int
