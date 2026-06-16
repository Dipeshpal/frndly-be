"""folders feature

Revision ID: 004_folders_feature
Revises: 003_notes_feature
Create Date: 2026-06-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_folders_feature"
down_revision: str | None = "003_notes_feature"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "folders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("parent_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["folders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_folders_user_id", "folders", ["user_id"])
    op.create_index("ix_folders_parent_id", "folders", ["parent_id"])

    op.add_column("notes", sa.Column("folder_id", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_notes_folder_id", "notes", "folders", ["folder_id"], ["id"], ondelete="SET NULL"
    )
    op.create_index("ix_notes_folder_id", "notes", ["folder_id"])


def downgrade() -> None:
    op.drop_index("ix_notes_folder_id", table_name="notes")
    op.drop_constraint("fk_notes_folder_id", "notes", type_="foreignkey")
    op.drop_column("notes", "folder_id")

    op.drop_index("ix_folders_parent_id", table_name="folders")
    op.drop_index("ix_folders_user_id", table_name="folders")
    op.drop_table("folders")
