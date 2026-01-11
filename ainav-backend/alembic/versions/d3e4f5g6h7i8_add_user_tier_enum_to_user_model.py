"""add user_tier enum to user model

Revision ID: d3e4f5g6h7i8
Revises: 027e859045ab
Create Date: 2026-01-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e4f5g6h7i8'
down_revision: Union[str, None] = '027e859045ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type
    user_tier_enum = sa.Enum('free', 'pro', 'enterprise', name='usertier', create_type=True)
    user_tier_enum.create(op.get_bind(), checkfirst=True)

    # Add user_tier column to users table with default 'free'
    op.add_column('users', sa.Column('user_tier', user_tier_enum, nullable=False, server_default='free'))


def downgrade() -> None:
    # Remove user_tier column
    op.drop_column('users', 'user_tier')

    # Drop enum type
    sa.Enum(name='usertier').drop(op.get_bind(), checkfirst=True)
