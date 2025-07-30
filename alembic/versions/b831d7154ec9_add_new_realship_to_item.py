"""add new realship to Item

Revision ID: b831d7154ec9
Revises: db669194d470
Create Date: 2024-09-24 09:35:38.002151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b831d7154ec9'
down_revision: Union[str, None] = 'db669194d470'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('items', sa.Column('owner_character_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('items', 'owner_character_id')
