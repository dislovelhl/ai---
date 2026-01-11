"""add description fields to scenario

Revision ID: d1e2f3g4h5i6
Revises: 027e859045ab
Create Date: 2026-01-11 04:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, None] = '027e859045ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description and description_zh columns to scenarios table
    op.add_column('scenarios', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('scenarios', sa.Column('description_zh', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove description and description_zh columns from scenarios table
    op.drop_column('scenarios', 'description_zh')
    op.drop_column('scenarios', 'description')
