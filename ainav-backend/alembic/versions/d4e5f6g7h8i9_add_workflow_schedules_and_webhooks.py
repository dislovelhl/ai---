"""add workflow schedules and webhooks

Revision ID: d4e5f6g7h8i9
Revises: 027e859045ab
Create Date: 2026-01-11 04:20:43.000000

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
    # Create workflow_schedules table
    op.create_table(
        'workflow_schedules',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', sa.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=False),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create workflow_webhooks table
    op.create_table(
        'workflow_webhooks',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', sa.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('webhook_secret', sa.String(255), nullable=False),
        sa.Column('webhook_url_path', sa.String(255), nullable=False, unique=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('allowed_ips', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('max_requests_per_hour', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create indexes for better query performance
    op.create_index('idx_workflow_schedules_workflow_id', 'workflow_schedules', ['workflow_id'])
    op.create_index('idx_workflow_schedules_next_run_at', 'workflow_schedules', ['next_run_at'])
    op.create_index('idx_workflow_schedules_enabled', 'workflow_schedules', ['enabled'])
    op.create_index('idx_workflow_webhooks_workflow_id', 'workflow_webhooks', ['workflow_id'])
    op.create_index('idx_workflow_webhooks_url_path', 'workflow_webhooks', ['webhook_url_path'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_workflow_webhooks_url_path', table_name='workflow_webhooks')
    op.drop_index('idx_workflow_webhooks_workflow_id', table_name='workflow_webhooks')
    op.drop_index('idx_workflow_schedules_enabled', table_name='workflow_schedules')
    op.drop_index('idx_workflow_schedules_next_run_at', table_name='workflow_schedules')
    op.drop_index('idx_workflow_schedules_workflow_id', table_name='workflow_schedules')

    # Drop tables
    op.drop_table('workflow_webhooks')
    op.drop_table('workflow_schedules')
