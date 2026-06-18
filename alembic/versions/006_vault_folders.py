"""Add folder column to secrets

Revision ID: 006_vault_folders
Revises: 005_device_tracking
Create Date: 2026-06-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "006_vault_folders"
down_revision: str | None = "005_device_tracking"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Check if secrets table exists before adding column
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'secrets' in inspector.get_table_names():
        # Check if folder column already exists
        columns = [col['name'] for col in inspector.get_columns('secrets')]
        if 'folder' not in columns:
            op.add_column("secrets", sa.Column("folder", sa.String(100), nullable=False, server_default="General"))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'secrets' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('secrets')]
        if 'folder' in columns:
            op.drop_column("secrets", "folder")
