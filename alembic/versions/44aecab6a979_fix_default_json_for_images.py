"""Fix default JSON for images

Revision ID: 44aecab6a979
Revises: 84c25e0c8f7d
Create Date: 2025-09-17 18:34:05.262682

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "44aecab6a979"
down_revision: Union[str, Sequence[str], None] = "84c25e0c8f7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix default value for posts.images column."""
    op.alter_column(
        "posts",
        "images",
        server_default=text("'[]'::json"),
        existing_type=sa.JSON(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Revert default value for posts.images column."""
    op.alter_column(
        "posts",
        "images",
        server_default=None,
        existing_type=sa.JSON(),
        existing_nullable=False,
    )
