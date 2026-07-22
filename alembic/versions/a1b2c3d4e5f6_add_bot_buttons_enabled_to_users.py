"""add bot_buttons_enabled to users

Revision ID: a1b2c3d4e5f6
Revises: c4d8e1f70a2b
Create Date: 2026-07-21
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision = 'c4d8e1f70a2b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('bot_buttons_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
    )


def downgrade() -> None:
    op.drop_column('users', 'bot_buttons_enabled')
