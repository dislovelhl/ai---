"""add skill documentation fields

Revision ID: d4e5f6g7h8i9
Revises: 027e859045ab
Create Date: 2026-01-11 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = '027e859045ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add documentation fields to skills table
    op.add_column('skills', sa.Column('rate_limit', JSON, nullable=True))
    op.add_column('skills', sa.Column('pricing_tier', sa.String(50), nullable=True))
    op.add_column('skills', sa.Column('pricing_details', JSON, nullable=True))
    op.add_column('skills', sa.Column('code_examples', JSON, nullable=True))
    op.add_column('skills', sa.Column('sample_request', JSON, nullable=True))
    op.add_column('skills', sa.Column('sample_response', JSON, nullable=True))


def downgrade() -> None:
    # Remove documentation fields from skills table
    op.drop_column('skills', 'sample_response')
    op.drop_column('skills', 'sample_request')
    op.drop_column('skills', 'code_examples')
    op.drop_column('skills', 'pricing_details')
    op.drop_column('skills', 'pricing_tier')
    op.drop_column('skills', 'rate_limit')
