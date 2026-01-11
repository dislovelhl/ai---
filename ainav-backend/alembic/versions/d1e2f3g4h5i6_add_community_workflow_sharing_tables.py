"""add community workflow sharing tables

Revision ID: d1e2f3g4h5i6
Revises: 027e859045ab
Create Date: 2026-01-11 04:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, None] = '027e859045ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workflow_categories table
    op.create_table(
        'workflow_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_zh', sa.String(100), nullable=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(255), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create workflow_tags table
    op.create_table(
        'workflow_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('name_zh', sa.String(50), nullable=True),
        sa.Column('slug', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create workflow_workflow_tags junction table (many-to-many)
    op.create_table(
        'workflow_workflow_tags',
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_tags.id'), primary_key=True),
    )

    # Create workflow_stars junction table (many-to-many with timestamp)
    op.create_table(
        'workflow_stars',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Add category_id column to agent_workflows table
    op.add_column('agent_workflows', sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_categories.id'), nullable=True))

    # Create indexes for better query performance
    op.create_index('idx_workflow_categories_slug', 'workflow_categories', ['slug'])
    op.create_index('idx_workflow_tags_slug', 'workflow_tags', ['slug'])
    op.create_index('idx_workflow_tags_name', 'workflow_tags', ['name'])
    op.create_index('idx_workflow_workflow_tags_workflow_id', 'workflow_workflow_tags', ['workflow_id'])
    op.create_index('idx_workflow_workflow_tags_tag_id', 'workflow_workflow_tags', ['tag_id'])
    op.create_index('idx_workflow_stars_user_id', 'workflow_stars', ['user_id'])
    op.create_index('idx_workflow_stars_workflow_id', 'workflow_stars', ['workflow_id'])
    op.create_index('idx_agent_workflows_category_id', 'agent_workflows', ['category_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_agent_workflows_category_id', table_name='agent_workflows')
    op.drop_index('idx_workflow_stars_workflow_id', table_name='workflow_stars')
    op.drop_index('idx_workflow_stars_user_id', table_name='workflow_stars')
    op.drop_index('idx_workflow_workflow_tags_tag_id', table_name='workflow_workflow_tags')
    op.drop_index('idx_workflow_workflow_tags_workflow_id', table_name='workflow_workflow_tags')
    op.drop_index('idx_workflow_tags_name', table_name='workflow_tags')
    op.drop_index('idx_workflow_tags_slug', table_name='workflow_tags')
    op.drop_index('idx_workflow_categories_slug', table_name='workflow_categories')

    # Remove category_id column from agent_workflows
    op.drop_column('agent_workflows', 'category_id')

    # Drop tables
    op.drop_table('workflow_stars')
    op.drop_table('workflow_workflow_tags')
    op.drop_table('workflow_tags')
    op.drop_table('workflow_categories')
