"""unique constraint on characters.characters_user_id

Enforces one character per user at the DB level. This is the root-cause guard for
the duplicate-character pileup that made CharacterService.get_character raise
MultipleResultsFound and crashed every club view.

NOTE: the characters table must already be de-duplicated before this runs, or
create_unique_constraint will fail. The one-time dedupe (keep club-holder / most
progress / lowest id per user) is a deliberate data step run before this upgrade.
UNIQUE permits multiple NULLs, so bot/orphan rows without a user_id are unaffected.

Revision ID: af10341a0261
Revises: 6e6e42c4c047
Create Date: 2026-07-05 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'af10341a0261'
down_revision: Union[str, None] = '6e6e42c4c047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_characters_user_id', 'characters', ['characters_user_id']
    )


def downgrade() -> None:
    # The plain KEY `characters_user_id` (backing FK characters_ibfk_1) is left in
    # place, so dropping the unique index does not break the foreign key.
    op.drop_constraint('uq_characters_user_id', 'characters', type_='unique')
