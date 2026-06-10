"""add description column to entities

Revision ID: 0002_entity_description
Revises: 0001_initial
Create Date: 2026-06-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_entity_description"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("entities", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("entities", "description")
