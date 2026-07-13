"""add ldap servers config

Revision ID: 4a1b2c3d4e5f
Revises: 42e2978c7933
Create Date: 2026-07-10 00:00:00.000000

"""

import time
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4a1b2c3d4e5f'
down_revision: Union[str, None] = '42e2978c7933'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Seed the ldap.servers config key with an empty list if it doesn't exist.
    # This is a no-op for existing deployments that already have the key,
    # and ensures the key exists for new installations.
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == 'sqlite':
        query = (
            "INSERT OR IGNORE INTO config (key, value, updated_at) "
            "VALUES ('ldap.servers', '[]', :now)"
        )
    else:
        query = (
            "INSERT INTO config (key, value, updated_at) "
            "VALUES ('ldap.servers', '[]', :now) "
            "ON CONFLICT (key) DO NOTHING"
        )

    conn.execute(sa.text(query), {'now': int(time.time())})


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM config WHERE key = 'ldap.servers'"))
