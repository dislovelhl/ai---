"""
Cache Service for Multi-Agent Optimizations

Provides:
1. SkillCache - TTL cache for external API call results
2. LLMCache - Semantic cache for LLM responses
3. SkillSelector - Semantic skill selection with pre-indexed embeddings
"""
import json
import logging
import hashlib
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import numpy as np

from shared.config import settings

logger = logging.getLogger(__name__)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))


class SkillCache:
    """
    TTL cache for external skill/tool API call results.

    Reduces redundant API calls by caching results based on:
    - skill_slug + input_args hash
    - Configurable TTL per skill type
    """

    # Default TTL by skill type (seconds)
    DEFAULT_TTL: int = 300  # 5 minutes
    SKILL_TTL_MAP: Dict[str, int] = {
        "search": 60,           # Search results change frequently
        "weather": 1800,        # Weather updates every 30 mins
        "translation": 86400,   # Translations are stable
        "code": 3600,           # Code generation can be cached
        "data": 300,            # Data queries
    }

    _pool: Optional[ConnectionPool] = None

    @classmethod
    async def get_pool(cls) -> ConnectionPool:
        """Get or create Redis connection pool."""
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=10,
                decode_responses=True
            )
        return cls._pool

    async def get_redis(self) -> redis.Redis:
        """Get Redis client from connection pool."""
        pool = await self.get_pool()
        return redis.Redis(connection_pool=pool)

    def _compute_cache_key(self, skill_slug: str, args: Dict[str, Any]) -> str:
        """Compute deterministic cache key."""
        args_str = json.dumps(args, sort_keys=True, ensure_ascii=False)
        args_hash = hashlib.md5(args_str.encode('utf-8')).hexdigest()
        return f"skill:{skill_slug}:{args_hash}"

    def _get_ttl(self, skill_slug: str) -> int:
        """Get TTL for skill based on type."""
        for skill_type, ttl in self.SKILL_TTL_MAP.items():
            if skill_type in skill_slug.lower():
                return ttl
        return self.DEFAULT_TTL

    async def get(self, skill_slug: str, args: Dict[str, Any]) -> Optional[Any]:
        """
        Get cached skill result if available.

        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._compute_cache_key(skill_slug, args)

        try:
            redis_client = await self.get_redis()
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Skill cache hit: {skill_slug}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Skill cache get failed: {e}")

        return None

    async def set(self, skill_slug: str, args: Dict[str, Any], result: Any) -> bool:
        """
        Cache skill result with appropriate TTL.

        Returns:
            True if cached successfully
        """
        cache_key = self._compute_cache_key(skill_slug, args)
        ttl = self._get_ttl(skill_slug)

        try:
            redis_client = await self.get_redis()
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, ensure_ascii=False)
            )
            logger.debug(f"Skill cache set: {skill_slug} (TTL={ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Skill cache set failed: {e}")
            return False

    async def get_or_execute(
        self,
        skill_slug: str,
        args: Dict[str, Any],
        execute_fn
    ) -> Any:
        """
        Get from cache or execute function and cache result.

        Args:
            skill_slug: Skill identifier
            args: Skill arguments
            execute_fn: Async function to call if not cached

        Returns:
            Cached or freshly computed result
        """
        cached = await self.get(skill_slug, args)
        if cached is not None:
            return cached

        result = await execute_fn()
        await self.set(skill_slug, args, result)
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "default_ttl": self.DEFAULT_TTL,
            "ttl_config": self.SKILL_TTL_MAP,
            "description": "TTL-based skill result cache"
        }


class LLMCache:
    """
    Semantic cache for LLM responses.

    Caches LLM responses based on semantic similarity of prompts.
    Uses embedding comparison to find similar queries.
    """

    SIMILARITY_THRESHOLD: float = 0.95
    MAX_CACHE_ENTRIES: int = 500
    TTL: int = 3600  # 1 hour

    _pool: Optional[ConnectionPool] = None

    # In-memory index for fast similarity search
    _prompt_embeddings: Dict[str, Tuple[List[float], str]] = {}  # hash -> (embedding, response)

    @classmethod
    async def get_pool(cls) -> ConnectionPool:
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=10,
                decode_responses=True
            )
        return cls._pool

    async def get_redis(self) -> redis.Redis:
        pool = await self.get_pool()
        return redis.Redis(connection_pool=pool)

    def _compute_prompt_hash(self, prompt: str, model: str) -> str:
        """Compute hash for exact match lookup."""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    async def get_exact(self, prompt: str, model: str) -> Optional[str]:
        """
        Get cached response for exact prompt match.

        Returns:
            Cached response or None
        """
        cache_key = f"llm:{self._compute_prompt_hash(prompt, model)}"

        try:
            redis_client = await self.get_redis()
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("LLM cache hit (exact)")
                return cached
        except Exception as e:
            logger.warning(f"LLM cache get failed: {e}")

        return None

    async def get_semantic(
        self,
        prompt: str,
        prompt_embedding: List[float],
        model: str
    ) -> Optional[str]:
        """
        Get cached response for semantically similar prompt.

        Args:
            prompt: User prompt
            prompt_embedding: Pre-computed embedding
            model: LLM model name

        Returns:
            Cached response if similar prompt found, else None
        """
        # First try exact match
        exact = await self.get_exact(prompt, model)
        if exact:
            return exact

        # Search in-memory embeddings for similar prompts
        for cached_hash, (cached_emb, cached_response) in self._prompt_embeddings.items():
            similarity = cosine_similarity(prompt_embedding, cached_emb)
            if similarity >= self.SIMILARITY_THRESHOLD:
                logger.debug(f"LLM cache hit (semantic, similarity={similarity:.3f})")
                return cached_response

        return None

    async def set(
        self,
        prompt: str,
        prompt_embedding: List[float],
        response: str,
        model: str
    ) -> bool:
        """
        Cache LLM response with both exact and semantic indexing.
        """
        prompt_hash = self._compute_prompt_hash(prompt, model)
        cache_key = f"llm:{prompt_hash}"

        try:
            redis_client = await self.get_redis()
            await redis_client.setex(cache_key, self.TTL, response)

            # Add to in-memory semantic index
            if len(self._prompt_embeddings) >= self.MAX_CACHE_ENTRIES:
                # Evict oldest entry
                oldest = next(iter(self._prompt_embeddings))
                del self._prompt_embeddings[oldest]

            self._prompt_embeddings[prompt_hash] = (prompt_embedding, response)
            logger.debug(f"LLM cache set: {prompt_hash[:8]}...")
            return True

        except Exception as e:
            logger.warning(f"LLM cache set failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "semantic_index_size": len(self._prompt_embeddings),
            "max_entries": self.MAX_CACHE_ENTRIES,
            "ttl": self.TTL,
            "similarity_threshold": self.SIMILARITY_THRESHOLD
        }


class SkillSelector:
    """
    Semantic skill selector for efficient tool binding.

    Pre-indexes skill embeddings at startup and selects relevant
    skills based on semantic similarity to user query.
    """

    TOP_K_DEFAULT: int = 5

    def __init__(self):
        self.skill_embeddings: Dict[str, Tuple[List[float], Dict]] = {}
        self._initialized: bool = False

    async def initialize(self, skills: List[Dict[str, Any]], embed_fn) -> None:
        """
        Initialize skill index with embeddings.

        Args:
            skills: List of skill dictionaries with name, description, slug
            embed_fn: Async function to compute embeddings
        """
        if self._initialized:
            return

        logger.info(f"Initializing SkillSelector with {len(skills)} skills...")

        # Batch embed all skill descriptions
        texts = [f"{s['name']}: {s.get('description', '')}" for s in skills]
        embeddings = await embed_fn(texts)

        for skill, emb in zip(skills, embeddings):
            self.skill_embeddings[skill['id']] = (emb, skill)

        self._initialized = True
        logger.info(f"SkillSelector initialized with {len(self.skill_embeddings)} skills")

    async def select_relevant(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Select top-k most relevant skills for a query.

        Args:
            query: User query text
            query_embedding: Pre-computed query embedding
            top_k: Number of skills to return

        Returns:
            List of relevant skill dictionaries, sorted by relevance
        """
        if not self._initialized:
            logger.warning("SkillSelector not initialized, returning all skills")
            return [s for _, s in self.skill_embeddings.values()]

        top_k = top_k or self.TOP_K_DEFAULT

        # Compute similarities
        similarities: List[Tuple[float, str, Dict]] = []
        for skill_id, (skill_emb, skill) in self.skill_embeddings.items():
            sim = cosine_similarity(query_embedding, skill_emb)
            similarities.append((sim, skill_id, skill))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[0], reverse=True)

        # Return top-k skills
        selected = [skill for _, _, skill in similarities[:top_k]]
        logger.debug(f"Selected {len(selected)} skills for query (top_k={top_k})")
        return selected

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Get all indexed skills."""
        return [skill for _, skill in self.skill_embeddings.values()]


# Singleton instances
skill_cache = SkillCache()
llm_cache = LLMCache()
skill_selector = SkillSelector()
