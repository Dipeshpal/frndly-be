"""Add folder column to secrets

Revision ID: 006_vault_folders
Revises: 005_device_tracking
Create Date: 2026-06-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006_vault_folders"
down_revision: str | None = "005_device_tracking"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("secrets", sa.Column("folder", sa.String(100), nullable=False, server_default="General"))


def downgrade() -> None:
    op.drop_column("secrets", "folder")
