"""Add device tracking table

Revision ID: 005_device_tracking
Revises: 004_folders_feature
Create Date: 2026-06-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_device_tracking"
down_revision: str | None = "004_folders_feature"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("device_id", sa.String(36), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("os_type", sa.String(50), nullable=False),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("last_seen", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Index("idx_user_id", "user_id"),
        sa.Index("idx_device_id", "device_id"),
    )


def downgrade() -> None:
    op.drop_table("devices")
