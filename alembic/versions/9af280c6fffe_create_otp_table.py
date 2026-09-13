"""create otp table

Revision ID: 9af280c6fffe
Revises: 7bac02b2b1e2
Create Date: 2026-08-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9af280c6fffe"
down_revision: Union[str, Sequence[str], None] = "7bac02b2b1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "otps",

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "code",
            sa.String(length=6),
            nullable=False,
        ),

        sa.Column(
            "purpose",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "is_used",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "uuid",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_otps_uuid"),
        "otps",
        ["uuid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_otps_uuid"),
        table_name="otps",
    )

    op.drop_table("otps")