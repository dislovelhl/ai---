"""merge oauth and versioning heads

Revision ID: 027e859045ab
Revises: b1c2d3e4f5g6, c2d3e4f5g6h7
Create Date: 2026-01-09 21:17:41.859886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '027e859045ab'
down_revision: Union[str, None] = ('b1c2d3e4f5g6', 'c2d3e4f5g6h7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
