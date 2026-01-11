"""add replay tracking fields

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade():
    # Add replay tracking fields to agent_executions table
    op.add_column('agent_executions', sa.Column('parent_execution_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('agent_executions', sa.Column('replayed_from_step', sa.String(length=100), nullable=True))

    # Add foreign key constraint and index for parent_execution_id
    op.create_foreign_key(
        'fk_agent_executions_parent_execution_id',
        'agent_executions', 'agent_executions',
        ['parent_execution_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index(
        'ix_agent_executions_parent_execution_id',
        'agent_executions',
        ['parent_execution_id']
    )


def downgrade():
    # Remove index and foreign key constraint
    op.drop_index('ix_agent_executions_parent_execution_id', table_name='agent_executions')
    op.drop_constraint('fk_agent_executions_parent_execution_id', 'agent_executions', type_='foreignkey')

    # Remove columns
    op.drop_column('agent_executions', 'replayed_from_step')
    op.drop_column('agent_executions', 'parent_execution_id')
