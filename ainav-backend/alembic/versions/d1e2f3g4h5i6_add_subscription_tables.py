"""add subscription tables

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
    # Create subscription_plans table
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('name_zh', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('tier', sa.String(50), nullable=False, index=True),
        sa.Column('daily_execution_limit', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('monthly_execution_limit', sa.Integer(), nullable=False, server_default='1500'),
        sa.Column('price_monthly', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('price_yearly', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('stripe_price_id_monthly', sa.String(255), nullable=True),
        sa.Column('stripe_price_id_yearly', sa.String(255), nullable=True),
        sa.Column('stripe_product_id', sa.String(255), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('features_zh', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('supports_alipay', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('supports_wechat_pay', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_popular', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('priority_level', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create indexes for better query performance
    op.create_index('idx_subscription_plans_tier', 'subscription_plans', ['tier'])
    op.create_index('idx_subscription_plans_is_active', 'subscription_plans', ['is_active'])
    op.create_index('idx_subscription_plans_display_order', 'subscription_plans', ['display_order'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_subscription_plans_display_order', table_name='subscription_plans')
    op.drop_index('idx_subscription_plans_is_active', table_name='subscription_plans')
    op.drop_index('idx_subscription_plans_tier', table_name='subscription_plans')

    # Drop table
    op.drop_table('subscription_plans')
