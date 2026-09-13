"""add otp base status columns

Revision ID: a5da3b641cdf
Revises: 9af280c6fffe
Create Date: 2026-08-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a5da3b641cdf"
down_revision: Union[str, Sequence[str], None] = "9af280c6fffe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    op.add_column(
        "otps",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "otps",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("otps", "is_deleted")
    op.drop_column("otps", "is_active")