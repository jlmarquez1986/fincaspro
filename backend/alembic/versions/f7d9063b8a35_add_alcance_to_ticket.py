"""add_alcance_to_ticket

Revision ID: f7d9063b8a35
Revises: 9aec2efa12cd
Create Date: 2026-07-24 16:57:34.495686

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "f7d9063b8a35"
down_revision: str | Sequence[str] | None = "9aec2efa12cd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("tickets", sa.Column("alcance", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tickets", "alcance")
