"""Repair users stranded mid chat-tutorial: mark them END_TRAINING.

The chat education gauntlet is retired (education now lives in the Mini App
tutorial). Users stuck at any gauntlet stage — including the orphaned dead-end
states TERRITORY_ACADEMY / JOIN_FIRST_MATCH — get unlocked. Users still in the
character-creation dialog stages are left untouched.

Revision ID: b2c3d4e5f6a7
Revises: b7e2f9c31d84 (VPS-side education_reward_notified_date fix, 2026-07-22 morning)
Create Date: 2026-07-22
"""
from typing import Sequence, Union

from alembic import op

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'b7e2f9c31d84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STRANDED = (
    "'FIRST_TRAINING'", "'TRAINING_CENTER'", "'BUY_EQUIPMENT'",
    "'TERRITORY_ACADEMY'", "'JOIN_FIRST_MATCH'", "'FORGOT_TRAINING'",
)


def upgrade() -> None:
    op.execute(
        "UPDATE users SET status_register = 'END_TRAINING' "
        f"WHERE status_register IN ({', '.join(STRANDED)})"
    )


def downgrade() -> None:
    pass  # data repair, not reversible
