"""add agentic platform models

Revision ID: a7b8c9d0e1f2
Revises: 5edc3e070215
Create Date: 2026-01-09 19:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = '5edc3e070215'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add has_api column to tools table
    op.add_column('tools', sa.Column('has_api', sa.Boolean(), nullable=True, server_default='false'))
    
    # Create skills table
    op.create_table(
        'skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tools.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_zh', sa.String(100), nullable=True),
        sa.Column('slug', sa.String(100), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('api_endpoint', sa.String(512), nullable=True),
        sa.Column('http_method', sa.String(10), nullable=True),
        sa.Column('input_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('headers_template', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('auth_type', sa.String(50), nullable=True, server_default='none'),
        sa.Column('auth_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_latency_ms', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create agent_workflows table
    op.create_table(
        'agent_workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_zh', sa.String(255), nullable=True),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('graph_json', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('trigger_type', sa.String(50), nullable=True, server_default='manual'),
        sa.Column('trigger_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('input_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_model', sa.String(100), nullable=True, server_default='deepseek-chat'),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True, server_default='0.7'),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_template', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('forked_from_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id', ondelete='SET NULL'), nullable=True),
        sa.Column('fork_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('run_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('star_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create agent_executions table
    op.create_table(
        'agent_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=True, server_default='pending'),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_log', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('token_usage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_api_calls', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('trigger_type', sa.String(50), nullable=True),
        sa.Column('trigger_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create agent_memories table (for Phase 3 RAG)
    op.create_table(
        'agent_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=True),
        sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for better query performance
    op.create_index('idx_skills_tool_id', 'skills', ['tool_id'])
    op.create_index('idx_agent_workflows_user_id', 'agent_workflows', ['user_id'])
    op.create_index('idx_agent_workflows_is_public', 'agent_workflows', ['is_public'])
    op.create_index('idx_agent_executions_workflow_id', 'agent_executions', ['workflow_id'])
    op.create_index('idx_agent_executions_user_id', 'agent_executions', ['user_id'])
    op.create_index('idx_agent_executions_status', 'agent_executions', ['status'])
    op.create_index('idx_agent_memories_workflow_id', 'agent_memories', ['workflow_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_agent_memories_workflow_id', table_name='agent_memories')
    op.drop_index('idx_agent_executions_status', table_name='agent_executions')
    op.drop_index('idx_agent_executions_user_id', table_name='agent_executions')
    op.drop_index('idx_agent_executions_workflow_id', table_name='agent_executions')
    op.drop_index('idx_agent_workflows_is_public', table_name='agent_workflows')
    op.drop_index('idx_agent_workflows_user_id', table_name='agent_workflows')
    op.drop_index('idx_skills_tool_id', table_name='skills')
    
    # Drop tables
    op.drop_table('agent_memories')
    op.drop_table('agent_executions')
    op.drop_table('agent_workflows')
    op.drop_table('skills')
    
    # Remove has_api column from tools
    op.drop_column('tools', 'has_api')
