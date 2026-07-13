"""add ldap servers config

Revision ID: 4a1b2c3d4e5f
Revises: d4e5f6a7b8c9
Create Date: 2026-07-10 00:00:00.000000

"""

import time
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4a1b2c3d4e5f'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Seed the ldap.servers config key with an empty list if it doesn't exist.
    # This is a no-op for existing deployments that already have the key,
    # and ensures the key exists for new installations.
    op.execute(
        sa.text(
            "INSERT OR IGNORE INTO config (key, value, updated_at) "
            "VALUES ('ldap.servers', '[]', :now)"
        ),
        now=int(time.time()),
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM config WHERE key = 'ldap.servers'"))
