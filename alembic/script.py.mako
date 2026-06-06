"""alembic/script.py.mako - Migration script template."""

from alembic import op
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "${revision}"
down_revision = "${down_revision}"
branch_labels = "${branch_labels}"
depends_on = "${depends_on}"


def upgrade() -> None:
    ${upgrades_if}(op.get_bind())


def downgrade() -> None:
    ${downgrades_if}(op.get_bind())