"""add search_history table

Revision ID: d4e5f6g7h8i9
Revises: 027e859045ab
Create Date: 2026-01-11 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = '027e859045ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create search_history table
    op.create_table(
        'search_history',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('query', sa.String(500), nullable=False, index=True),
        sa.Column('query_pinyin', sa.String(500), nullable=True, index=True),
        sa.Column('result_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('clicked_result_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create indexes for better query performance
    op.create_index('idx_search_history_user_id', 'search_history', ['user_id'])
    op.create_index('idx_search_history_created_at', 'search_history', ['created_at'])
    # Composite index for fetching user's recent searches
    op.create_index('idx_search_history_user_created', 'search_history', ['user_id', 'created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_search_history_user_created', table_name='search_history')
    op.drop_index('idx_search_history_created_at', table_name='search_history')
    op.drop_index('idx_search_history_user_id', table_name='search_history')

    # Drop table
    op.drop_table('search_history')
