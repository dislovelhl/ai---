"""
Duplicate Detection Utility for Automated Content Crawlers

Provides methods to detect duplicate tools across existing tools and pending crawled content
using exact URL matching, normalized name matching, and fuzzy string matching.
"""

import re
import logging
from difflib import SequenceMatcher
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func

from shared.models import Tool, CrawledContent

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """
    Detects duplicate tools using multiple strategies:
    1. Exact URL matching (normalized)
    2. Normalized name matching (case-insensitive, special chars removed)
    3. Fuzzy name matching (using difflib with configurable threshold)
    """

    def __init__(self, fuzzy_threshold: float = 0.85):
        """
        Initialize the duplicate detector.

        Args:
            fuzzy_threshold: Similarity threshold for fuzzy matching (0.0 to 1.0).
                            Default is 0.85 (85% similar)
        """
        self.fuzzy_threshold = fuzzy_threshold

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize a URL for comparison by:
        - Converting to lowercase
        - Removing trailing slashes
        - Removing www. prefix
        - Removing query parameters and fragments
        - Standardizing http/https

        Args:
            url: The URL to normalize

        Returns:
            Normalized URL string
        """
        if not url:
            return ""

        # Parse URL
        parsed = urlparse(url.lower().strip())

        # Remove www. from netloc
        netloc = parsed.netloc.replace("www.", "")

        # Remove trailing slash from path
        path = parsed.path.rstrip("/")

        # Reconstruct URL without query params and fragments
        normalized = urlunparse((
            "https",  # Standardize to https
            netloc,
            path,
            "",  # params
            "",  # query
            ""   # fragment
        ))

        return normalized

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a name for comparison by:
        - Converting to lowercase
        - Removing special characters (keeping only alphanumeric and spaces)
        - Stripping extra whitespace
        - Removing common prefixes/suffixes

        Args:
            name: The name to normalize

        Returns:
            Normalized name string
        """
        if not name:
            return ""

        # Convert to lowercase and strip
        normalized = name.lower().strip()

        # Remove common prefixes/suffixes
        prefixes = ["the ", "a ", "an "]
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]

        # Remove special characters, keep only alphanumeric and spaces
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings using SequenceMatcher.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        if not str1 or not str2:
            return 0.0

        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    async def check_url_duplicate(
        self,
        session: AsyncSession,
        url: str
    ) -> Optional[Dict[str, any]]:
        """
        Check if a tool with the same URL already exists.

        Args:
            session: SQLAlchemy async session
            url: URL to check

        Returns:
            Dict with duplicate info if found, None otherwise
            Format: {"type": "tool" | "crawled", "id": uuid, "name": str}
        """
        normalized_url = self.normalize_url(url)

        # Check existing tools
        tool_query = select(Tool).where(
            func.lower(Tool.url) == normalized_url
        )
        result = await session.execute(tool_query)
        existing_tool = result.scalar_one_or_none()

        if existing_tool:
            logger.info(f"Found duplicate tool by URL: {existing_tool.name} ({existing_tool.id})")
            return {
                "type": "tool",
                "id": str(existing_tool.id),
                "name": existing_tool.name,
                "match_type": "exact_url"
            }

        # Check pending crawled content
        crawled_query = select(CrawledContent).where(
            func.lower(CrawledContent.url) == normalized_url,
            CrawledContent.status == "pending"
        )
        result = await session.execute(crawled_query)
        existing_crawled = result.scalar_one_or_none()

        if existing_crawled:
            logger.info(f"Found duplicate in crawled content by URL: {existing_crawled.name} ({existing_crawled.id})")
            return {
                "type": "crawled",
                "id": str(existing_crawled.id),
                "name": existing_crawled.name,
                "match_type": "exact_url"
            }

        return None

    async def check_name_duplicate(
        self,
        session: AsyncSession,
        name: str
    ) -> Optional[Dict[str, any]]:
        """
        Check if a tool with the same normalized name already exists.

        Args:
            session: SQLAlchemy async session
            name: Name to check

        Returns:
            Dict with duplicate info if found, None otherwise
        """
        normalized_name = self.normalize_name(name)

        if not normalized_name:
            return None

        # Check existing tools
        tool_query = select(Tool)
        result = await session.execute(tool_query)
        tools = result.scalars().all()

        for tool in tools:
            if self.normalize_name(tool.name) == normalized_name:
                logger.info(f"Found duplicate tool by normalized name: {tool.name} ({tool.id})")
                return {
                    "type": "tool",
                    "id": str(tool.id),
                    "name": tool.name,
                    "match_type": "normalized_name"
                }

        # Check pending crawled content
        crawled_query = select(CrawledContent).where(
            CrawledContent.status == "pending"
        )
        result = await session.execute(crawled_query)
        crawled_items = result.scalars().all()

        for item in crawled_items:
            if self.normalize_name(item.name) == normalized_name:
                logger.info(f"Found duplicate in crawled content by normalized name: {item.name} ({item.id})")
                return {
                    "type": "crawled",
                    "id": str(item.id),
                    "name": item.name,
                    "match_type": "normalized_name"
                }

        return None

    async def check_fuzzy_duplicate(
        self,
        session: AsyncSession,
        name: str,
        threshold: Optional[float] = None
    ) -> Optional[Dict[str, any]]:
        """
        Check if a similar tool name exists using fuzzy matching.

        Args:
            session: SQLAlchemy async session
            name: Name to check
            threshold: Optional custom threshold (overrides instance default)

        Returns:
            Dict with duplicate info if found, None otherwise
            Includes 'similarity' score in the result
        """
        threshold = threshold or self.fuzzy_threshold
        normalized_name = self.normalize_name(name)

        if not normalized_name:
            return None

        best_match = None
        best_similarity = 0.0

        # Check existing tools
        tool_query = select(Tool)
        result = await session.execute(tool_query)
        tools = result.scalars().all()

        for tool in tools:
            tool_normalized = self.normalize_name(tool.name)
            similarity = self.calculate_similarity(normalized_name, tool_normalized)

            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = {
                    "type": "tool",
                    "id": str(tool.id),
                    "name": tool.name,
                    "match_type": "fuzzy_name",
                    "similarity": round(similarity, 3)
                }

        # Check pending crawled content
        crawled_query = select(CrawledContent).where(
            CrawledContent.status == "pending"
        )
        result = await session.execute(crawled_query)
        crawled_items = result.scalars().all()

        for item in crawled_items:
            item_normalized = self.normalize_name(item.name)
            similarity = self.calculate_similarity(normalized_name, item_normalized)

            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = {
                    "type": "crawled",
                    "id": str(item.id),
                    "name": item.name,
                    "match_type": "fuzzy_name",
                    "similarity": round(similarity, 3)
                }

        if best_match:
            logger.info(
                f"Found fuzzy duplicate: {best_match['name']} "
                f"(similarity: {best_match['similarity']})"
            )

        return best_match

    async def find_duplicates(
        self,
        session: AsyncSession,
        name: str,
        url: str,
        check_fuzzy: bool = True
    ) -> List[Dict[str, any]]:
        """
        Comprehensive duplicate check using all available methods.
        Returns all potential duplicates found.

        Args:
            session: SQLAlchemy async session
            name: Tool name to check
            url: Tool URL to check
            check_fuzzy: Whether to include fuzzy matching (slower)

        Returns:
            List of duplicate matches, each with type, id, name, and match_type
            Returns empty list if no duplicates found
        """
        duplicates = []

        # Check URL first (fastest and most reliable)
        url_dup = await self.check_url_duplicate(session, url)
        if url_dup:
            duplicates.append(url_dup)

        # Check normalized name
        name_dup = await self.check_name_duplicate(session, name)
        if name_dup:
            # Only add if not already found by URL
            if not url_dup or url_dup['id'] != name_dup['id']:
                duplicates.append(name_dup)

        # Check fuzzy matching if enabled and no exact matches found
        if check_fuzzy and not duplicates:
            fuzzy_dup = await self.check_fuzzy_duplicate(session, name)
            if fuzzy_dup:
                duplicates.append(fuzzy_dup)

        return duplicates

    async def is_duplicate(
        self,
        session: AsyncSession,
        name: str,
        url: str,
        check_fuzzy: bool = True
    ) -> bool:
        """
        Simple boolean check if any duplicate exists.

        Args:
            session: SQLAlchemy async session
            name: Tool name to check
            url: Tool URL to check
            check_fuzzy: Whether to include fuzzy matching

        Returns:
            True if any duplicate found, False otherwise
        """
        duplicates = await self.find_duplicates(session, name, url, check_fuzzy)
        return len(duplicates) > 0
