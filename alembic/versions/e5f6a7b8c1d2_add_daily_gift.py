"""add gift_claimed to daily_quests

Revision ID: e5f6a7b8c1d2
Revises: d4e5f6a7b8c1
Create Date: 2026-07-23
"""
import sqlalchemy as sa
from alembic import op

revision = "e5f6a7b8c1d2"
down_revision = "d4e5f6a7b8c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("daily_quests", sa.Column("gift_claimed", sa.Boolean(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("daily_quests", "gift_claimed")
