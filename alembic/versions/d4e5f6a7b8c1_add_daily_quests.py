"""add daily_quests table

Revision ID: d4e5f6a7b8c1
Revises: c3d4e5f6a7b8
Create Date: 2026-07-23
"""
import sqlalchemy as sa
from alembic import op

revision = "d4e5f6a7b8c1"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_quests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("character_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("quest_date", sa.Date(), nullable=False),
        sa.Column("trainings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("matches", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("claimed", sa.Boolean(), nullable=False, server_default="0"),
        sa.UniqueConstraint("character_id", "quest_date", name="uq_daily_quest_char_date"),
    )


def downgrade() -> None:
    op.drop_table("daily_quests")
