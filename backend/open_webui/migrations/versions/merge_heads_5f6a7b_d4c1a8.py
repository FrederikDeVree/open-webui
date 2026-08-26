"""merge heads (chat timer_at / indexes with local merge heads)

Revision ID: a3e9f7c1b2d4
Revises: 5f6a7b8c9d0e, d4c1a8e37b62
Create Date: 2026-08-26 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = 'a3e9f7c1b2d4'
down_revision: str | Sequence[str] | None = ('5f6a7b8c9d0e', 'd4c1a8e37b62')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
