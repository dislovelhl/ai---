"""add workflow versioning

Revision ID: b1c2d3e4f5g6
Revises: a7b8c9d0e1f2
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5g6'
down_revision = 'a7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('agent_workflows', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('agent_workflows', sa.Column('version_history', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade():
    op.drop_column('agent_workflows', 'version_history')
    op.drop_column('agent_workflows', 'version')
