"""add user verification status

Revision ID: 7bac02b2b1e2
Revises: 5521e8c945e8
Create Date: 2026-08-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7bac02b2b1e2"
down_revision: Union[str, Sequence[str], None] = "5521e8c945e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # Remove the database-level default after existing rows
    # have been populated with False.
    op.alter_column(
        "users",
        "is_verified",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "users",
        "is_verified",
    )
    
