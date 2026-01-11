"""add oauth fields to user

Revision ID: c2d3e4f5g6h7
Revises: b8c9d0e1f2g3
Create Date: 2025-01-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c2d3e4f5g6h7'
down_revision: Union[str, None] = 'b8c9d0e1f2g3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add OAuth provider ID columns to users table
    op.add_column('users', sa.Column('github_id', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('wechat_id', sa.String(50), nullable=True))

    # Create unique indexes for OAuth IDs
    op.create_index('ix_users_github_id', 'users', ['github_id'], unique=True)
    op.create_index('ix_users_wechat_id', 'users', ['wechat_id'], unique=True)

    # Make phone column nullable (for OAuth users without phone)
    op.alter_column('users', 'phone',
                    existing_type=sa.String(20),
                    nullable=True)


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_users_wechat_id', table_name='users')
    op.drop_index('ix_users_github_id', table_name='users')

    # Remove columns
    op.drop_column('users', 'wechat_id')
    op.drop_column('users', 'github_id')

    # Note: Not reverting phone nullable change as it could cause data loss
