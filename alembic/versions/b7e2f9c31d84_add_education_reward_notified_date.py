"""add education_reward_notified_date to reminder_characters

Revision ID: b7e2f9c31d84
Revises: a1b2c3d4e5f6
Create Date: 2026-07-22
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'b7e2f9c31d84'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'reminder_characters',
        sa.Column(
            'education_reward_notified_date',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("'1970-01-01 00:00:00'"),
        ),
    )
    # Users whose reward is already claimable were spammed by the crash-loop
    # broadcast; mark them notified so the deploy restart sends nothing.
    op.execute(
        "UPDATE reminder_characters "
        "SET education_reward_notified_date = NOW() "
        "WHERE education_reward_date <= NOW()"
    )


def downgrade() -> None:
    op.drop_column('reminder_characters', 'education_reward_notified_date')
