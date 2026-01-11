"""add execution steps tracking

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
    # Add execution_steps column to agent_executions table
    op.add_column('agent_executions', sa.Column('execution_steps', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade():
    # Remove execution_steps column
    op.drop_column('agent_executions', 'execution_steps')
