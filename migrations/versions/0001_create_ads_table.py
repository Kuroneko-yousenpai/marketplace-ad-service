"""create ads table

Revision ID: 0001
Revises:
Create Date: 2026-04-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="active",
        ),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_ads_user_id", "ads", ["user_id"])
    op.create_index("ix_ads_category", "ads", ["category"])
    op.create_index("ix_ads_city", "ads", ["city"])
    op.create_index("ix_ads_status", "ads", ["status"])


def downgrade() -> None:
    op.drop_index("ix_ads_status", table_name="ads")
    op.drop_index("ix_ads_city", table_name="ads")
    op.drop_index("ix_ads_category", table_name="ads")
    op.drop_index("ix_ads_user_id", table_name="ads")
    op.drop_table("ads")
