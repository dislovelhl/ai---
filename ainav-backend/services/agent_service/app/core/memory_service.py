"""
Optimized MemoryService with async embeddings, connection pooling, and caching.

Optimizations Applied:
1. Async embedding computation using ThreadPoolExecutor (non-blocking)
2. Redis connection pooling for concurrent request handling
3. LRU cache for embedding results to avoid recomputation
4. Embedding cache with Redis for distributed caching
"""
import json
import logging
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from datetime import datetime

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from shared.config import settings
from shared.models import AgentMemory

logger = logging.getLogger(__name__)


class MemoryService:
    """
    MemoryService manages short-term (Redis) and long-term (pgvector) memory.

    Optimizations:
    - Async embedding with ThreadPoolExecutor (prevents blocking event loop)
    - Redis connection pooling (handles concurrent requests efficiently)
    - Local LRU cache + Redis cache for embeddings (avoids recomputation)
    """

    _pool: Optional[ConnectionPool] = None
    _executor: Optional[ThreadPoolExecutor] = None
    _embedder: Optional[SentenceTransformer] = None

    # Local embedding cache (in-memory LRU)
    _embedding_cache: Dict[str, List[float]] = {}
    _cache_max_size: int = 1000

    # Cache TTL for Redis embedding cache (1 hour)
    EMBEDDING_CACHE_TTL: int = 3600

    def __init__(self):
        pass  # Lazy initialization via class methods

    @classmethod
    def get_executor(cls) -> ThreadPoolExecutor:
        """Get or create thread pool executor for CPU-bound embedding tasks."""
        if cls._executor is None:
            # Use 4 workers for embedding - balances parallelism vs memory
            cls._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="embedding")
            logger.info("Created ThreadPoolExecutor for embeddings (4 workers)")
        return cls._executor

    @classmethod
    def get_embedder(cls) -> SentenceTransformer:
        """Get or create sentence transformer model (lazy loading)."""
        if cls._embedder is None:
            logger.info("Loading SentenceTransformer model...")
            cls._embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("SentenceTransformer model loaded successfully")
        return cls._embedder

    @classmethod
    async def get_pool(cls) -> ConnectionPool:
        """Get or create Redis connection pool."""
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                decode_responses=True
            )
            logger.info("Created Redis connection pool (max_connections=20)")
        return cls._pool

    async def get_redis(self) -> redis.Redis:
        """Get Redis client from connection pool."""
        pool = await self.get_pool()
        return redis.Redis(connection_pool=pool)

    def _compute_cache_key(self, text: str) -> str:
        """Compute cache key for embedding."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    async def _get_embedding_async(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Compute embedding asynchronously using thread pool.

        This prevents blocking the async event loop during CPU-intensive
        embedding computation.

        Args:
            text: Text to embed
            use_cache: Whether to use local + Redis cache

        Returns:
            List of floats representing the embedding vector
        """
        cache_key = self._compute_cache_key(text)

        if use_cache:
            # Check local LRU cache first (fastest)
            if cache_key in self._embedding_cache:
                logger.debug(f"Embedding cache hit (local): {cache_key[:8]}...")
                return self._embedding_cache[cache_key]

            # Check Redis cache (distributed)
            try:
                redis_client = await self.get_redis()
                cached = await redis_client.get(f"emb:{cache_key}")
                if cached:
                    embedding = json.loads(cached)
                    # Populate local cache
                    self._add_to_local_cache(cache_key, embedding)
                    logger.debug(f"Embedding cache hit (Redis): {cache_key[:8]}...")
                    return embedding
            except Exception as e:
                logger.warning(f"Redis embedding cache lookup failed: {e}")

        # Compute embedding in thread pool (non-blocking)
        loop = asyncio.get_event_loop()
        embedder = self.get_embedder()
        executor = self.get_executor()

        embedding = await loop.run_in_executor(
            executor,
            lambda: embedder.encode(text).tolist()
        )

        if use_cache:
            # Store in local cache
            self._add_to_local_cache(cache_key, embedding)

            # Store in Redis cache (async, fire-and-forget)
            try:
                redis_client = await self.get_redis()
                await redis_client.setex(
                    f"emb:{cache_key}",
                    self.EMBEDDING_CACHE_TTL,
                    json.dumps(embedding)
                )
            except Exception as e:
                logger.warning(f"Redis embedding cache store failed: {e}")

        return embedding

    def _add_to_local_cache(self, key: str, embedding: List[float]):
        """Add embedding to local LRU cache with size limit."""
        if len(self._embedding_cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO, not true LRU but good enough)
            oldest_key = next(iter(self._embedding_cache))
            del self._embedding_cache[oldest_key]
        self._embedding_cache[key] = embedding

    async def add_chat_message(self, workflow_id: str, session_id: str, role: str, content: str):
        """
        Store a message in the Redis chat history.
        Key format: chat_history:{workflow_id}:{session_id}
        """
        key = f"chat_history:{workflow_id}:{session_id}"
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        redis_client = await self.get_redis()
        await redis_client.rpush(key, json.dumps(message))
        # Set expiration to 7 days
        await redis_client.expire(key, 7 * 24 * 3600)

    async def get_chat_history(self, workflow_id: str, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve chat history from Redis."""
        key = f"chat_history:{workflow_id}:{session_id}"
        redis_client = await self.get_redis()
        messages = await redis_client.lrange(key, -limit, -1)
        return [json.loads(m) for m in messages]

    async def clear_chat_history(self, workflow_id: str, session_id: str):
        """Clear chat history for a session."""
        key = f"chat_history:{workflow_id}:{session_id}"
        redis_client = await self.get_redis()
        await redis_client.delete(key)

    async def store_long_term_memory(
        self,
        db: AsyncSession,
        workflow_id: str,
        content: str,
        content_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store content in the long-term vector memory."""
        # Use async embedding computation
        embedding = await self._get_embedding_async(content)

        memory = AgentMemory(
            workflow_id=workflow_id,
            content=content,
            content_type=content_type,
            meta_data=metadata or {},
            embedding=embedding
        )

        db.add(memory)
        await db.commit()

    async def search_memory(
        self,
        db: AsyncSession,
        workflow_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories using vector similarity."""
        # Use async embedding computation
        query_embedding = await self._get_embedding_async(query)

        # Convert embedding to string format for postgres vector
        emb_str = str(query_embedding).replace(" ", "")

        sql = text("""
            SELECT id, content, content_type, meta_data
            FROM agent_memories
            WHERE workflow_id = :workflow_id
            ORDER BY embedding <=> :emb::vector
            LIMIT :limit
        """)

        result = await db.execute(
            sql,
            {"workflow_id": workflow_id, "emb": emb_str, "limit": limit}
        )

        memories = []
        for row in result:
            memories.append({
                "id": row.id,
                "content": row.content,
                "content_type": row.content_type,
                "metadata": row.meta_data
            })

        return memories

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """
        Batch embed multiple texts efficiently.

        Uses thread pool for parallel computation and caches results.
        """
        # Check cache for all texts
        results = []
        texts_to_compute = []
        indices_to_compute = []

        for i, text in enumerate(texts):
            cache_key = self._compute_cache_key(text)
            if cache_key in self._embedding_cache:
                results.append((i, self._embedding_cache[cache_key]))
            else:
                texts_to_compute.append(text)
                indices_to_compute.append(i)

        if texts_to_compute:
            # Batch compute missing embeddings
            loop = asyncio.get_event_loop()
            embedder = self.get_embedder()
            executor = self.get_executor()

            new_embeddings = await loop.run_in_executor(
                executor,
                lambda: embedder.encode(texts_to_compute).tolist()
            )

            # Cache and collect results
            for idx, emb in zip(indices_to_compute, new_embeddings):
                cache_key = self._compute_cache_key(texts[idx])
                self._add_to_local_cache(cache_key, emb)
                results.append((idx, emb))

        # Sort by original index and return embeddings only
        results.sort(key=lambda x: x[0])
        return [emb for _, emb in results]

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics for monitoring."""
        return {
            "local_cache_size": len(self._embedding_cache),
            "local_cache_max": self._cache_max_size,
            "executor_workers": self.get_executor()._max_workers if self._executor else 0
        }


# Singleton instance
memory_service = MemoryService()
