"""unaccent

Revision ID: c13b0be62f53
Revises:
Create Date: 2026-10-29 17:09:31.477492

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c13b0be62f53"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  """Upgrade schema."""
  op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def downgrade() -> None:
  """Downgrade schema."""
  op.execute("DROP EXTENSION IF EXISTS unaccent;")
