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
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('name_zh', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_zh', sa.Text(), nullable=True),
        sa.Column('tier', sa.String(50), nullable=False),
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
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create indexes for subscription_plans
    op.create_index('idx_subscription_plans_slug', 'subscription_plans', ['slug'], unique=True)
    op.create_index('idx_subscription_plans_tier', 'subscription_plans', ['tier'])
    op.create_index('idx_subscription_plans_is_active', 'subscription_plans', ['is_active'])
    op.create_index('idx_subscription_plans_display_order', 'subscription_plans', ['display_order'])

    # Create user_subscriptions table
    op.create_table(
        'user_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('stripe_payment_method_id', sa.String(255), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_method_last4', sa.String(4), nullable=True),
        sa.Column('payment_method_brand', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('billing_cycle', sa.String(20), nullable=True, server_default='monthly'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('trial_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
    )

    # Create indexes for user_subscriptions
    op.create_index('idx_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    op.create_index('idx_user_subscriptions_stripe_customer_id', 'user_subscriptions', ['stripe_customer_id'], unique=True)
    op.create_index('idx_user_subscriptions_stripe_subscription_id', 'user_subscriptions', ['stripe_subscription_id'], unique=True)
    op.create_index('idx_user_subscriptions_status', 'user_subscriptions', ['status'])
    op.create_index('idx_user_subscriptions_current_period_end', 'user_subscriptions', ['current_period_end'])

    # Create usage_records table
    op.create_table(
        'usage_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('day', sa.Integer(), nullable=True),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('workflow_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )

    # Create indexes for usage_records
    op.create_index('idx_usage_records_user_id', 'usage_records', ['user_id'])
    op.create_index('idx_usage_records_record_date', 'usage_records', ['record_date'])
    op.create_index('idx_usage_records_period_type', 'usage_records', ['period_type'])
    op.create_index('idx_usage_records_year', 'usage_records', ['year'])
    op.create_index('idx_usage_records_month', 'usage_records', ['month'])

    # Create payment_transactions table
    op.create_table(
        'payment_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('stripe_charge_id', sa.String(255), nullable=True),
        sa.Column('stripe_invoice_id', sa.String(255), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='CNY'),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('payment_method_brand', sa.String(50), nullable=True),
        sa.Column('payment_method_last4', sa.String(4), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('billing_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('billing_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('refunded_amount', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('provider', sa.String(50), nullable=True, server_default='stripe'),
        sa.Column('provider_transaction_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'], ),
    )

    # Create indexes for payment_transactions
    op.create_index('idx_payment_transactions_user_id', 'payment_transactions', ['user_id'])
    op.create_index('idx_payment_transactions_stripe_payment_intent_id', 'payment_transactions', ['stripe_payment_intent_id'], unique=True)
    op.create_index('idx_payment_transactions_stripe_charge_id', 'payment_transactions', ['stripe_charge_id'], unique=True)
    op.create_index('idx_payment_transactions_stripe_invoice_id', 'payment_transactions', ['stripe_invoice_id'], unique=True)
    op.create_index('idx_payment_transactions_status', 'payment_transactions', ['status'])


def downgrade() -> None:
    # Drop payment_transactions table and indexes
    op.drop_index('idx_payment_transactions_status', table_name='payment_transactions')
    op.drop_index('idx_payment_transactions_stripe_invoice_id', table_name='payment_transactions')
    op.drop_index('idx_payment_transactions_stripe_charge_id', table_name='payment_transactions')
    op.drop_index('idx_payment_transactions_stripe_payment_intent_id', table_name='payment_transactions')
    op.drop_index('idx_payment_transactions_user_id', table_name='payment_transactions')
    op.drop_table('payment_transactions')

    # Drop usage_records table and indexes
    op.drop_index('idx_usage_records_month', table_name='usage_records')
    op.drop_index('idx_usage_records_year', table_name='usage_records')
    op.drop_index('idx_usage_records_period_type', table_name='usage_records')
    op.drop_index('idx_usage_records_record_date', table_name='usage_records')
    op.drop_index('idx_usage_records_user_id', table_name='usage_records')
    op.drop_table('usage_records')

    # Drop user_subscriptions table and indexes
    op.drop_index('idx_user_subscriptions_current_period_end', table_name='user_subscriptions')
    op.drop_index('idx_user_subscriptions_status', table_name='user_subscriptions')
    op.drop_index('idx_user_subscriptions_stripe_subscription_id', table_name='user_subscriptions')
    op.drop_index('idx_user_subscriptions_stripe_customer_id', table_name='user_subscriptions')
    op.drop_index('idx_user_subscriptions_user_id', table_name='user_subscriptions')
    op.drop_table('user_subscriptions')

    # Drop subscription_plans table and indexes
    op.drop_index('idx_subscription_plans_display_order', table_name='subscription_plans')
    op.drop_index('idx_subscription_plans_is_active', table_name='subscription_plans')
    op.drop_index('idx_subscription_plans_tier', table_name='subscription_plans')
    op.drop_index('idx_subscription_plans_slug', table_name='subscription_plans')
    op.drop_table('subscription_plans')
