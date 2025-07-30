"""add new colum

Revision ID: ff1330232e3e
Revises: 205648c63b51
Create Date: 2025-04-15 17:50:09.309914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff1330232e3e'
down_revision: Union[str, None] = '205648c63b51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
