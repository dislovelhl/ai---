"""add template metadata to workflows

Revision ID: d4e5f6g7h8i9
Revises: 027e859045ab
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = '027e859045ab'
branch_labels = None
depends_on = None


def upgrade():
    # Add template-specific metadata columns to agent_workflows table
    op.add_column('agent_workflows', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('agent_workflows', sa.Column('use_case', sa.String(length=255), nullable=True))
    op.add_column('agent_workflows', sa.Column('usage_instructions_zh', sa.Text(), nullable=True))
    op.add_column('agent_workflows', sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True))


def downgrade():
    # Remove template-specific metadata columns from agent_workflows table
    op.drop_column('agent_workflows', 'tags')
    op.drop_column('agent_workflows', 'usage_instructions_zh')
    op.drop_column('agent_workflows', 'use_case')
    op.drop_column('agent_workflows', 'category')
