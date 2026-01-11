import httpx
from shared.config import settings
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ProductHuntClient:
    def __init__(self):
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {settings.PRODUCTHUNT_TOKEN}",
            "Content-Type": "application/json",
        }

        # Enhanced AI-related keywords categorized by relevance
        self.ai_keywords_high_priority = [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "llm", "large language model", "gpt", "bert",
            "transformer", "diffusion model", "stable diffusion", "midjourney",
            "chatgpt", "claude", "gemini", "agent", "autonomous agent",
            "rag", "retrieval augmented", "vector database", "embedding",
            "ai assistant", "ai chatbot", "ai agent", "generative ai"
        ]
        self.ai_keywords_medium_priority = [
            "ai", "ml", "nlp", "natural language processing", "computer vision",
            "gen ai", "inference", "model training", "fine-tuning",
            "prompt engineering", "langchain", "llamaindex", "openai",
            "huggingface", "pytorch", "tensorflow", "automation",
            "ai-powered", "ai-driven", "smart assistant", "intelligent"
        ]
        self.ai_keywords_low_priority = [
            "intelligence", "prediction", "classification", "regression",
            "clustering", "reinforcement learning", "supervised learning",
            "unsupervised learning", "data science", "model", "algorithm",
            "personalization", "recommendation", "optimization"
        ]

        # AI-related topics to query from ProductHunt
        self.ai_topics = [
            "artificial-intelligence",
            "machine-learning",
            "developer-tools",
            "productivity",
            "no-code",
            "saas"
        ]

    def _calculate_ai_score(self, text: str, topics: List[str] = None) -> float:
        """
        Calculate AI relevance score based on keywords and topics.
        Returns a score between 0.0 and 1.0.
        """
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Check high priority keywords (0.3 points each, max 0.6)
        high_matches = sum(1 for kw in self.ai_keywords_high_priority if kw in text_lower)
        score += min(high_matches * 0.3, 0.6)

        # Check medium priority keywords (0.15 points each, max 0.3)
        medium_matches = sum(1 for kw in self.ai_keywords_medium_priority if kw in text_lower)
        score += min(medium_matches * 0.15, 0.3)

        # Check low priority keywords (0.05 points each, max 0.1)
        low_matches = sum(1 for kw in self.ai_keywords_low_priority if kw in text_lower)
        score += min(low_matches * 0.05, 0.1)

        # Bonus for AI-related topics from ProductHunt (0.2 points)
        if topics:
            ai_topic_keywords = [
                "artificial-intelligence", "machine-learning", "ai", "ml",
                "automation", "chatbot", "assistant", "generative"
            ]
            topic_matches = sum(1 for topic in topics if any(kw in topic.lower() for kw in ai_topic_keywords))
            if topic_matches > 0:
                score += 0.2

        return min(score, 1.0)

    async def _fetch_posts_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Fetch posts from a specific topic using GraphQL API.

        Args:
            topic: ProductHunt topic slug (e.g., "artificial-intelligence")
            limit: Maximum number of posts to fetch

        Returns:
            List of post nodes from GraphQL response
        """
        query = """
        query($topic: String!, $limit: Int!) {
          posts(topic: $topic, first: $limit) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                website
                votesCount
                createdAt
                topics {
                  edges {
                    node {
                      name
                      slug
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            "topic": topic,
            "limit": limit
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Check for GraphQL errors
                if "errors" in data:
                    logger.error(f"GraphQL errors for topic {topic}: {data['errors']}")
                    return []

                edges = data.get("data", {}).get("posts", {}).get("edges", [])
                return [edge["node"] for edge in edges]

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching ProductHunt topic {topic}: {e}")
                return []
            except Exception as e:
                logger.error(f"Error fetching ProductHunt topic {topic}: {e}")
                return []

    async def get_daily_ai_tools(self, min_ai_score: float = 0.3, limit_per_topic: int = 10) -> List[Dict]:
        """
        Fetch AI-related tools from ProductHunt across multiple topics.

        Uses enhanced AI detection including:
        - Multi-tier keyword matching with scoring
        - Multiple AI-related topic filters
        - Topic analysis from ProductHunt data

        Args:
            min_ai_score: Minimum AI relevance score (0.0-1.0, default: 0.3)
            limit_per_topic: Maximum posts to fetch per topic (default: 10)

        Returns:
            List of AI tool dicts with AI score, topics, and metadata
        """
        all_tools = []
        seen_ids = set()  # Deduplicate across topics

        logger.info(f"Fetching ProductHunt posts from {len(self.ai_topics)} topics")

        for topic in self.ai_topics:
            posts = await self._fetch_posts_by_topic(topic, limit_per_topic)
            logger.info(f"Found {len(posts)} posts in topic: {topic}")

            for post in posts:
                # Skip duplicates (same post can appear in multiple topics)
                post_id = post.get("id")
                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                # Extract post data
                name = post.get("name", "")
                tagline = post.get("tagline", "")
                description = post.get("description", "")

                # Extract topics
                topic_edges = post.get("topics", {}).get("edges", [])
                post_topics = [edge["node"]["slug"] for edge in topic_edges]

                # Combine text for AI scoring
                combined_text = f"{name} {tagline} {description}"

                # Calculate AI relevance score
                ai_score = self._calculate_ai_score(combined_text, post_topics)

                # Filter by minimum AI score
                if ai_score < min_ai_score:
                    logger.debug(f"Skipping {name} (AI score: {ai_score:.2f} < {min_ai_score})")
                    continue

                logger.info(f"Found AI tool: {name} (score: {ai_score:.2f}, topics: {post_topics})")

                all_tools.append({
                    "id": post_id,
                    "name": name,
                    "tagline": tagline,
                    "description": description,
                    "url": post.get("url", ""),
                    "website": post.get("website", ""),
                    "votes_count": post.get("votesCount", 0),
                    "created_at": post.get("createdAt", ""),
                    "topics": post_topics,
                    "ai_score": ai_score
                })

        logger.info(f"Filtered to {len(all_tools)} AI-related tools (min score: {min_ai_score})")
        return all_tools
