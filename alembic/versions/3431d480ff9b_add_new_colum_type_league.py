"""add new colum type league

Revision ID: 3431d480ff9b
Revises: d9d1d35b9a9d
Create Date: 2025-05-14 22:35:03.895069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import ENUM

# revision identifiers, used by Alembic.
revision: str = '3431d480ff9b'
down_revision: Union[str, None] = 'd9d1d35b9a9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    typeleague_enum = ENUM(
        'BEST_LEAGUE', 'DEFAULT_LEAGUE', 'TOP_20_CLUB_LEAGUE', 'NEW_CLUB_LEAGUE',
        name='typeleague'
    )
    bind = op.get_bind()
    typeleague_enum.create(bind, checkfirst=True)

    # 1. Добавляем nullable колонку
    op.add_column('league_fight', sa.Column(
        'type_league',
        typeleague_enum,
        nullable=True
    ))

    # 2. Обновляем значения в зависимости от логики
    op.execute("""
        UPDATE league_fight
        SET type_league = CASE
            WHEN is_beast_league = 1 THEN 'BEST_LEAGUE'
            WHEN is_top_20_club = 1 THEN 'TOP_20_CLUB_LEAGUE'
            ELSE 'DEFAULT_LEAGUE'
        END
    """)

    # 3. Меняем колонку на NOT NULL — указав тип снова
    op.execute("""
        ALTER TABLE league_fight
        MODIFY COLUMN type_league ENUM(
            'BEST_LEAGUE', 'DEFAULT_LEAGUE', 'TOP_20_CLUB_LEAGUE', 'NEW_CLUB_LEAGUE'
        ) NOT NULL
    """)


def downgrade() -> None:
    op.drop_column('league_fight', 'type_league')
    ENUM(name='typeleague').drop(op.get_bind(), checkfirst=True)