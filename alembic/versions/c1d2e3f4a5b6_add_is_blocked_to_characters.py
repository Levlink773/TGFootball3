"""add is_blocked to characters

Revision ID: c1d2e3f4a5b6
Revises: a9b3c7d1e4f2
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'c1d2e3f4a5b6'
down_revision = 'a9b3c7d1e4f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'characters',
        sa.Column(
            'is_blocked',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('0'),
        ),
    )


def downgrade() -> None:
    op.drop_column('characters', 'is_blocked')
