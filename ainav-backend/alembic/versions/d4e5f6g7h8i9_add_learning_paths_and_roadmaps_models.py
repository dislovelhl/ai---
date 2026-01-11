"""add learning paths and roadmaps models

Revision ID: d4e5f6g7h8i9
Revises: 027e859045ab
Create Date: 2026-01-11 08:00:00.000000

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
    # Create learning_paths table
    op.create_table(
        'learning_paths',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_zh', sa.String(255), nullable=True),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(255), nullable=True),
        sa.Column('difficulty_level', sa.String(20), nullable=False),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('prerequisites', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_outcomes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create learning_path_modules table
    op.create_table(
        'learning_path_modules',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('learning_path_id', sa.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('title_zh', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('content_type', sa.String(20), nullable=False),
        sa.Column('content_url', sa.String(512), nullable=True),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('quiz_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create user_learning_progress table
    op.create_table(
        'user_learning_progress',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('learning_path_id', sa.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='not_started'),
        sa.Column('progress_percentage', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('completed_modules', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create learning_certificates table
    op.create_table(
        'learning_certificates',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('learning_path_id', sa.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id', ondelete='CASCADE'), nullable=False),
        sa.Column('certificate_number', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('certificate_url', sa.String(512), nullable=False),
        sa.Column('share_token', sa.UUID(as_uuid=True), nullable=False, unique=True, index=True),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create learning_path_tools junction table (many-to-many)
    op.create_table(
        'learning_path_tools',
        sa.Column('learning_path_id', sa.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tool_id', sa.UUID(as_uuid=True), sa.ForeignKey('tools.id', ondelete='CASCADE'), primary_key=True),
    )

    # Create indexes for better query performance
    op.create_index('idx_learning_paths_difficulty', 'learning_paths', ['difficulty_level'])
    op.create_index('idx_learning_paths_category', 'learning_paths', ['category'])
    op.create_index('idx_learning_paths_is_published', 'learning_paths', ['is_published'])
    op.create_index('idx_learning_path_modules_path_id', 'learning_path_modules', ['learning_path_id'])
    op.create_index('idx_user_learning_progress_user_id', 'user_learning_progress', ['user_id'])
    op.create_index('idx_user_learning_progress_path_id', 'user_learning_progress', ['learning_path_id'])
    op.create_index('idx_user_learning_progress_status', 'user_learning_progress', ['status'])
    op.create_index('idx_learning_certificates_user_id', 'learning_certificates', ['user_id'])
    op.create_index('idx_learning_certificates_path_id', 'learning_certificates', ['learning_path_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_learning_certificates_path_id', table_name='learning_certificates')
    op.drop_index('idx_learning_certificates_user_id', table_name='learning_certificates')
    op.drop_index('idx_user_learning_progress_status', table_name='user_learning_progress')
    op.drop_index('idx_user_learning_progress_path_id', table_name='user_learning_progress')
    op.drop_index('idx_user_learning_progress_user_id', table_name='user_learning_progress')
    op.drop_index('idx_learning_path_modules_path_id', table_name='learning_path_modules')
    op.drop_index('idx_learning_paths_is_published', table_name='learning_paths')
    op.drop_index('idx_learning_paths_category', table_name='learning_paths')
    op.drop_index('idx_learning_paths_difficulty', table_name='learning_paths')

    # Drop tables (reverse order due to foreign key constraints)
    op.drop_table('learning_path_tools')
    op.drop_table('learning_certificates')
    op.drop_table('user_learning_progress')
    op.drop_table('learning_path_modules')
    op.drop_table('learning_paths')
