"""merge heads

Revision ID: 5f6a7b8c9d0e
Revises: 4a1b2c3d4e5f, f0bd01a18a3d
Create Date: 2026-07-29 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = '5f6a7b8c9d0e'
down_revision: str | Sequence[str] | None = ('4a1b2c3d4e5f', 'f0bd01a18a3d')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
