"""add new colum

Revision ID: ec258bb7f6eb
Revises: ff1330232e3e
Create Date: 2025-04-15 17:52:01.601352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec258bb7f6eb'
down_revision: Union[str, None] = 'ff1330232e3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
