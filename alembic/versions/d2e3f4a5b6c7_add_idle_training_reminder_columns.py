"""add last_training_at + idle_notified_at to reminder_characters

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'reminder_characters',
        sa.Column('last_training_at', sa.DateTime(), nullable=True),
    )
    op.add_column(
        'reminder_characters',
        sa.Column(
            'idle_notified_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("'1970-01-01 00:00:00'"),
        ),
    )
    # Без бэкфилла КАЖДЫЙ существующий игрок в первый же проход попадает
    # в рубеж «>24ч» и получает сообщение — это выглядело бы как спам-инцидент.
    op.execute(
        "UPDATE reminder_characters r "
        "JOIN characters c ON c.id = r.character_id "
        "SET r.last_training_at = COALESCE(r.time_start_training, c.created_at)"
    )
    # Помечаем всех уже уведомлёнными: самый поздний пересечённый рубеж получает
    # due < NOW(), claim не проходит, и ничего не летит до СЛЕДУЮЩЕГО рубежа.
    op.execute("UPDATE reminder_characters SET idle_notified_at = NOW()")


def downgrade() -> None:
    op.drop_column('reminder_characters', 'idle_notified_at')
    op.drop_column('reminder_characters', 'last_training_at')
