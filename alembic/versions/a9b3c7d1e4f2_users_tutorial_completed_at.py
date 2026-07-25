"""decouple "saw the tutorial slides" from bot registration status

In-app character creation has to set status_register = END_TRAINING immediately,
otherwise the player is left with every bot button prefixed 🔒 and a live nag
loop, with no way to finish now that the chat FSM is gone. But GET /api/tutorial
derived `completed` from that same flag, so setting it at creation would have
silently stopped the 5-slide tutorial from ever running.

They were one bit doing two jobs. This splits them.

Revision ID: a9b3c7d1e4f2
Revises: f6a7b8c1d2e3
Create Date: 2026-07-26
"""
import sqlalchemy as sa
from alembic import op

revision = "a9b3c7d1e4f2"
down_revision = "f6a7b8c1d2e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("tutorial_completed_at", sa.DateTime(), nullable=True))
    # Everyone already through bot registration has effectively seen the onboarding;
    # backfilling stops the slides being re-shown to the existing player base.
    op.execute(
        "UPDATE users SET tutorial_completed_at = COALESCE(user_time_register, NOW()) "
        "WHERE status_register = 'END_TRAINING'"
    )


def downgrade() -> None:
    op.drop_column("users", "tutorial_completed_at")
