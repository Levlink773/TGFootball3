"""per-task quest claim flags

Revision ID: f6a7b8c1d2e3
Revises: e5f6a7b8c1d2
Create Date: 2026-07-23
"""
import sqlalchemy as sa
from alembic import op

revision = "f6a7b8c1d2e3"
down_revision = "e5f6a7b8c1d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for col in ("trainings_claimed", "matches_claimed", "wins_claimed"):
        op.add_column("daily_quests", sa.Column(col, sa.Boolean(), nullable=False, server_default="0"))


def downgrade() -> None:
    for col in ("trainings_claimed", "matches_claimed", "wins_claimed"):
        op.drop_column("daily_quests", col)
