"""add rejection reason to withdrawals

Revision ID: efa350962d61
Revises: 9f1234567890
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "efa350962d61"
down_revision: Union[str, Sequence[str], None] = "9f1234567890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "withdrawals",
        sa.Column(
            "rejection_reason",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("withdrawals", "rejection_reason")