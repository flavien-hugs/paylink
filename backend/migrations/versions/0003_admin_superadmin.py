"""add is_superadmin to admin_users and promote the first account

Revision ID: 0003_admin_superadmin
Revises: 0002_entity_description
Create Date: 2026-06-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_admin_superadmin"
down_revision: Union[str, None] = "0002_entity_description"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "admin_users",
        sa.Column("is_superadmin", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    # Promote the earliest-created admin account to super administrator.
    op.execute(
        """
        UPDATE admin_users SET is_superadmin = true
        WHERE id = (SELECT id FROM admin_users ORDER BY created_at ASC LIMIT 1)
        """
    )


def downgrade() -> None:
    op.drop_column("admin_users", "is_superadmin")
