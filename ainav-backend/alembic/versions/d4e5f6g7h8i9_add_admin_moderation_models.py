"""add admin moderation models

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
    # Create UserRole enum
    user_role_enum = postgresql.ENUM('admin', 'moderator', 'user', name='userrole', create_type=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Create ModerationStatus enum
    moderation_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'flagged', name='moderationstatus', create_type=True)
    moderation_status_enum.create(op.get_bind(), checkfirst=True)

    # Add admin-related columns to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('role', user_role_enum, nullable=False, server_default='user'))
    op.add_column('users', sa.Column('permissions', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}'))

    # Create moderation_queue table
    op.create_table(
        'moderation_queue',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('content_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', moderation_status_enum, nullable=False, server_default='pending'),
        sa.Column('submitter_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewer_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create admin_activity_log table
    op.create_table(
        'admin_activity_log',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('admin_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('old_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create indexes for better query performance
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_admin', 'users', ['is_admin'])
    op.create_index('idx_moderation_queue_status', 'moderation_queue', ['status'])
    op.create_index('idx_moderation_queue_submitter_id', 'moderation_queue', ['submitter_id'])
    op.create_index('idx_moderation_queue_reviewer_id', 'moderation_queue', ['reviewer_id'])
    op.create_index('idx_moderation_queue_content_type', 'moderation_queue', ['content_type'])
    op.create_index('idx_admin_activity_log_admin_id', 'admin_activity_log', ['admin_id'])
    op.create_index('idx_admin_activity_log_action_type', 'admin_activity_log', ['action_type'])
    op.create_index('idx_admin_activity_log_resource_type', 'admin_activity_log', ['resource_type'])
    op.create_index('idx_admin_activity_log_created_at', 'admin_activity_log', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_admin_activity_log_created_at', table_name='admin_activity_log')
    op.drop_index('idx_admin_activity_log_resource_type', table_name='admin_activity_log')
    op.drop_index('idx_admin_activity_log_action_type', table_name='admin_activity_log')
    op.drop_index('idx_admin_activity_log_admin_id', table_name='admin_activity_log')
    op.drop_index('idx_moderation_queue_content_type', table_name='moderation_queue')
    op.drop_index('idx_moderation_queue_reviewer_id', table_name='moderation_queue')
    op.drop_index('idx_moderation_queue_submitter_id', table_name='moderation_queue')
    op.drop_index('idx_moderation_queue_status', table_name='moderation_queue')
    op.drop_index('idx_users_is_admin', table_name='users')
    op.drop_index('idx_users_role', table_name='users')

    # Drop tables
    op.drop_table('admin_activity_log')
    op.drop_table('moderation_queue')

    # Remove columns from users table
    op.drop_column('users', 'permissions')
    op.drop_column('users', 'role')
    op.drop_column('users', 'is_admin')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS moderationstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
