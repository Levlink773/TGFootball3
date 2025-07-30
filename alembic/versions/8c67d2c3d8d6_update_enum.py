"""update enum

Revision ID: 8c67d2c3d8d6
Revises: 1ca92a4446c8
Create Date: 2025-06-27 20:43:51.470235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8c67d2c3d8d6'
down_revision: Union[str, None] = '1ca92a4446c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users 
        MODIFY COLUMN status_register 
        ENUM(
            'PRE_RIGSTER_STATUS',
            'START_REGISTER',
            'CREATE_CHARACTER',
            'SEND_NAME_CHARACTER',
            'SELECT_GENDER',
            'SELECT_POSITION',
            'TERRITORY_ACADEMY',
            'JOIN_TO_CLUB',
            'FIRST_TRAINING',
            'TRAINING_CENTER',
            'BUY_EQUIPMENT',
            'JOIN_FIRST_MATCH',
            'FORGOT_TRAINING',
            'END_TRAINING'
        ) NOT NULL DEFAULT 'END_TRAINING';
    """)

def downgrade() -> None:
    op.execute("""
        ALTER TABLE users 
        MODIFY COLUMN status_register 
        ENUM(
            'PRE_RIGSTER_STATUS',
            'START_REGISTER',
            'CREATE_CHARACTER',
            'SEND_NAME_CHARACTER',
            'SELECT_GENDER',
            'SELECT_POSITION',
            'TERRITORY_ACADEMY',
            'JOIN_TO_CLUB',
            'FIRST_TRAINING',
            'FORGOT_TRAINING',
            'END_TRAINING'
        ) NOT NULL DEFAULT 'END_TRAINING';
    """)