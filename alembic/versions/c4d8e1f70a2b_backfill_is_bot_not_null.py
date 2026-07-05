"""backfill characters.is_bot and make it NOT NULL DEFAULT 0

Real players had is_bot = NULL (the column was added with only a Python-side
default, existing rows never backfilled). Every ranking / training query filters
`is_bot == False` -> SQL `is_bot = 0`, and `NULL = 0` is false in SQL, so real
players were silently excluded from the hall-of-fame rankings ("Игроков нету").
Backfill NULL -> 0 and pin the column NOT NULL DEFAULT 0 so it can't recur.

Revision ID: c4d8e1f70a2b
Revises: af10341a0261
Create Date: 2026-07-05 16:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c4d8e1f70a2b'
down_revision: Union[str, None] = 'af10341a0261'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE characters SET is_bot = 0 WHERE is_bot IS NULL")
    op.alter_column(
        'characters', 'is_bot',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text('0'),
    )


def downgrade() -> None:
    op.alter_column(
        'characters', 'is_bot',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
