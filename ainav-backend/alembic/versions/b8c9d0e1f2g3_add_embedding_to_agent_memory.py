"""add embedding to agent memory

Revision ID: b8c9d0e1f2g3
Revises: a7b8c9d0e1f2
Create Date: 2026-01-09 19:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2g3'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Add embedding column to agent_memories table using raw SQL
    # Vector(384) is pgvector type for 384-dimensional embeddings
    op.execute('ALTER TABLE agent_memories ADD COLUMN embedding vector(384)')
    
    # Create an HNSW index for better search performance
    # Note: Using op.execute for custom pgvector index syntax
    op.execute(
        'CREATE INDEX idx_agent_memories_embedding ON agent_memories USING hnsw (embedding vector_cosine_ops)'
    )

def downgrade() -> None:
    # Drop index
    op.drop_index('idx_agent_memories_embedding', table_name='agent_memories')
    
    # Drop column
    op.drop_column('agent_memories', 'embedding')
