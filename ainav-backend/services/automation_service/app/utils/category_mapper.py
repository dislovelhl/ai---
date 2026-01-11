"""
Category Mapping Utility for Automated Content Crawlers

Provides methods to map LLM-suggested category slugs to existing database categories,
with validation and fallback mechanisms for robust categorization.
"""

import logging
from typing import Optional, Dict, List
from difflib import get_close_matches

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from shared.models import Category

logger = logging.getLogger(__name__)


# Standard category slugs expected from LLM (from DeepSeek prompt)
STANDARD_CATEGORY_SLUGS = {
    'ai-chatbots',
    'image-generation',
    'code-assistants',
    'writing-content',
    'video-generation',
    'audio-music',
    'productivity',
    'research-analysis',
    'content-creation',
    'marketing',
    'development',
    'education',
    'business',
    'personal-use',
    'design',
    'research'
}

# Mapping of common variations/aliases to standard slugs
CATEGORY_ALIASES = {
    'chat': 'ai-chatbots',
    'chatbot': 'ai-chatbots',
    'chatbots': 'ai-chatbots',
    'conversation': 'ai-chatbots',
    'conversational-ai': 'ai-chatbots',

    'image': 'image-generation',
    'images': 'image-generation',
    'art': 'image-generation',
    'art-generation': 'image-generation',
    'image-gen': 'image-generation',

    'code': 'code-assistants',
    'coding': 'code-assistants',
    'programming': 'code-assistants',
    'developer-tools': 'code-assistants',
    'dev-tools': 'development',

    'writing': 'writing-content',
    'content-writing': 'writing-content',
    'text-generation': 'writing-content',
    'copywriting': 'writing-content',

    'video': 'video-generation',
    'videos': 'video-generation',
    'video-gen': 'video-generation',
    'video-editing': 'video-generation',

    'audio': 'audio-music',
    'music': 'audio-music',
    'sound': 'audio-music',
    'voice': 'audio-music',
    'tts': 'audio-music',
    'text-to-speech': 'audio-music',

    'research': 'research-analysis',
    'analysis': 'research-analysis',
    'analytics': 'research-analysis',
    'data-analysis': 'research-analysis',

    'content': 'content-creation',
    'creator': 'content-creation',

    'seo': 'marketing',
    'advertising': 'marketing',
    'social-media': 'marketing',

    'dev': 'development',
    'developer': 'development',
    'engineering': 'development',

    'learning': 'education',
    'teaching': 'education',
    'training': 'education',

    'enterprise': 'business',
    'corporate': 'business',
    'b2b': 'business',

    'personal': 'personal-use',
    'lifestyle': 'personal-use',

    'ui': 'design',
    'ux': 'design',
    'graphic-design': 'design',
    'visual': 'design'
}

# Default fallback category
DEFAULT_CATEGORY_SLUG = 'productivity'


class CategoryMapper:
    """
    Maps LLM-suggested category slugs to existing database categories.
    Provides validation, alias resolution, and fuzzy matching capabilities.
    """

    def __init__(self):
        """Initialize the category mapper."""
        self._category_cache: Optional[Dict[str, str]] = None  # slug -> id mapping

    @staticmethod
    def normalize_slug(slug: str) -> str:
        """
        Normalize a category slug by converting to lowercase and trimming.

        Args:
            slug: The category slug to normalize

        Returns:
            Normalized slug string
        """
        if not slug:
            return ""
        return slug.lower().strip()

    @staticmethod
    def is_standard_slug(slug: str) -> bool:
        """
        Check if a slug is in the standard category list.

        Args:
            slug: The category slug to check

        Returns:
            True if slug is standard, False otherwise
        """
        normalized = CategoryMapper.normalize_slug(slug)
        return normalized in STANDARD_CATEGORY_SLUGS

    @staticmethod
    def resolve_alias(slug: str) -> str:
        """
        Resolve a category alias to its standard slug.

        Args:
            slug: The category slug or alias

        Returns:
            Standard category slug (returns input if no alias found)
        """
        normalized = CategoryMapper.normalize_slug(slug)

        # Return as-is if it's already a standard slug
        if normalized in STANDARD_CATEGORY_SLUGS:
            return normalized

        # Try to resolve from aliases
        resolved = CATEGORY_ALIASES.get(normalized)
        if resolved:
            logger.info(f"Resolved category alias '{slug}' to '{resolved}'")
            return resolved

        # Return original if no resolution found
        return normalized

    @staticmethod
    def find_similar_slug(slug: str, cutoff: float = 0.6) -> Optional[str]:
        """
        Find similar category slug using fuzzy matching.

        Args:
            slug: The category slug to match
            cutoff: Similarity threshold (0.0 to 1.0)

        Returns:
            Most similar standard slug if found, None otherwise
        """
        normalized = CategoryMapper.normalize_slug(slug)

        if not normalized:
            return None

        # Use difflib to find close matches
        matches = get_close_matches(
            normalized,
            STANDARD_CATEGORY_SLUGS,
            n=1,
            cutoff=cutoff
        )

        if matches:
            match = matches[0]
            logger.info(f"Found similar category slug '{match}' for '{slug}'")
            return match

        return None

    async def get_category_id_by_slug(
        self,
        session: AsyncSession,
        slug: str
    ) -> Optional[str]:
        """
        Get category ID from database by slug.

        Args:
            session: SQLAlchemy async session
            slug: Category slug to look up

        Returns:
            Category UUID as string if found, None otherwise
        """
        normalized = self.normalize_slug(slug)

        if not normalized:
            return None

        try:
            query = select(Category).where(
                func.lower(Category.slug) == normalized
            )
            result = await session.execute(query)
            category = result.scalar_one_or_none()

            if category:
                return str(category.id)
            else:
                logger.warning(f"Category not found in database: {slug}")
                return None

        except Exception as e:
            logger.error(f"Error fetching category by slug '{slug}': {e}")
            return None

    async def load_category_cache(self, session: AsyncSession) -> None:
        """
        Load all categories from database into cache for faster lookups.

        Args:
            session: SQLAlchemy async session
        """
        try:
            query = select(Category)
            result = await session.execute(query)
            categories = result.scalars().all()

            self._category_cache = {
                cat.slug.lower(): str(cat.id)
                for cat in categories
            }

            logger.info(f"Loaded {len(self._category_cache)} categories into cache")

        except Exception as e:
            logger.error(f"Error loading category cache: {e}")
            self._category_cache = {}

    async def map_to_category_id(
        self,
        session: AsyncSession,
        suggested_slug: str,
        use_fallback: bool = True
    ) -> Optional[str]:
        """
        Map a suggested category slug to an actual database category ID.

        Uses the following resolution strategy:
        1. Check if slug is standard and exists in DB
        2. Try to resolve as an alias
        3. Try fuzzy matching to find similar slug
        4. Fall back to default category if enabled

        Args:
            session: SQLAlchemy async session
            suggested_slug: The category slug suggested by LLM
            use_fallback: Whether to use default category if no match found

        Returns:
            Category UUID as string if found, None if no match and fallback disabled
        """
        if not suggested_slug:
            if use_fallback:
                logger.warning("Empty category slug, using fallback")
                return await self.get_category_id_by_slug(session, DEFAULT_CATEGORY_SLUG)
            return None

        # Try direct lookup first
        category_id = await self.get_category_id_by_slug(session, suggested_slug)
        if category_id:
            return category_id

        # Try resolving as alias
        resolved_slug = self.resolve_alias(suggested_slug)
        if resolved_slug != suggested_slug:
            category_id = await self.get_category_id_by_slug(session, resolved_slug)
            if category_id:
                return category_id

        # Try fuzzy matching
        similar_slug = self.find_similar_slug(suggested_slug)
        if similar_slug:
            category_id = await self.get_category_id_by_slug(session, similar_slug)
            if category_id:
                return category_id

        # Use fallback if enabled
        if use_fallback:
            logger.warning(
                f"Could not map category slug '{suggested_slug}', "
                f"using fallback '{DEFAULT_CATEGORY_SLUG}'"
            )
            return await self.get_category_id_by_slug(session, DEFAULT_CATEGORY_SLUG)

        return None

    async def get_all_categories(
        self,
        session: AsyncSession
    ) -> List[Dict[str, str]]:
        """
        Get all categories from database.

        Args:
            session: SQLAlchemy async session

        Returns:
            List of category dicts with id, slug, and name
        """
        try:
            query = select(Category).order_by(Category.order, Category.name)
            result = await session.execute(query)
            categories = result.scalars().all()

            return [
                {
                    "id": str(cat.id),
                    "slug": cat.slug,
                    "name": cat.name,
                    "description": cat.description
                }
                for cat in categories
            ]

        except Exception as e:
            logger.error(f"Error fetching all categories: {e}")
            return []

    async def validate_and_map(
        self,
        session: AsyncSession,
        suggested_slug: str,
        confidence: float = 0.0
    ) -> Dict[str, any]:
        """
        Validate a suggested category and map to database ID with metadata.

        Args:
            session: SQLAlchemy async session
            suggested_slug: The category slug suggested by LLM
            confidence: LLM's confidence score (0.0 to 1.0)

        Returns:
            Dict with:
                - category_id: Database UUID (or None)
                - original_slug: Original suggested slug
                - mapped_slug: Actual slug used (after resolution)
                - confidence: Original confidence score
                - mapping_method: How the slug was resolved
                - success: Whether mapping was successful
        """
        result = {
            "category_id": None,
            "original_slug": suggested_slug,
            "mapped_slug": None,
            "confidence": confidence,
            "mapping_method": None,
            "success": False
        }

        if not suggested_slug:
            result["mapping_method"] = "fallback"
            result["mapped_slug"] = DEFAULT_CATEGORY_SLUG
            result["category_id"] = await self.get_category_id_by_slug(
                session, DEFAULT_CATEGORY_SLUG
            )
            result["success"] = result["category_id"] is not None
            return result

        # Try direct lookup
        category_id = await self.get_category_id_by_slug(session, suggested_slug)
        if category_id:
            result["category_id"] = category_id
            result["mapped_slug"] = suggested_slug
            result["mapping_method"] = "direct"
            result["success"] = True
            return result

        # Try alias resolution
        resolved_slug = self.resolve_alias(suggested_slug)
        if resolved_slug != suggested_slug:
            category_id = await self.get_category_id_by_slug(session, resolved_slug)
            if category_id:
                result["category_id"] = category_id
                result["mapped_slug"] = resolved_slug
                result["mapping_method"] = "alias"
                result["success"] = True
                return result

        # Try fuzzy matching
        similar_slug = self.find_similar_slug(suggested_slug)
        if similar_slug:
            category_id = await self.get_category_id_by_slug(session, similar_slug)
            if category_id:
                result["category_id"] = category_id
                result["mapped_slug"] = similar_slug
                result["mapping_method"] = "fuzzy"
                result["success"] = True
                return result

        # Fall back to default
        result["mapping_method"] = "fallback"
        result["mapped_slug"] = DEFAULT_CATEGORY_SLUG
        result["category_id"] = await self.get_category_id_by_slug(
            session, DEFAULT_CATEGORY_SLUG
        )
        result["success"] = result["category_id"] is not None

        return result
