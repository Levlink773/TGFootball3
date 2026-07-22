"""Remove chat menu for everyone: bot_buttons_enabled -> 0 (app-first ГРАТИ).

Users can re-enable the chat keyboard from the Mini App Settings toggle.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET bot_buttons_enabled = 0")
    op.alter_column(
        'users', 'bot_buttons_enabled',
        existing_type=sa.Boolean(), nullable=False, server_default=sa.text('0'),
    )


def downgrade() -> None:
    op.alter_column(
        'users', 'bot_buttons_enabled',
        existing_type=sa.Boolean(), nullable=False, server_default=sa.text('1'),
    )
