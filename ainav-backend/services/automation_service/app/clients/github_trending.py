import httpx
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from shared.config import settings

logger = logging.getLogger(__name__)

class GitHubTrendingClient:
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.api_base_url = "https://api.github.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.api_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AI-Navigation-Platform"
        }
        if settings.GITHUB_TOKEN:
            self.api_headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

        # Enhanced AI-related keywords categorized by relevance
        self.ai_keywords_high_priority = [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "llm", "large language model", "gpt", "bert",
            "transformer", "diffusion model", "stable diffusion", "midjourney",
            "chatgpt", "claude", "gemini", "agent", "autonomous agent",
            "rag", "retrieval augmented", "vector database", "embedding"
        ]
        self.ai_keywords_medium_priority = [
            "ai", "ml", "nlp", "natural language processing", "computer vision",
            "generative ai", "gen ai", "inference", "model training", "fine-tuning",
            "prompt engineering", "langchain", "llamaindex", "openai",
            "huggingface", "pytorch", "tensorflow", "keras", "scikit-learn"
        ]
        self.ai_keywords_low_priority = [
            "intelligence", "prediction", "classification", "regression",
            "clustering", "reinforcement learning", "supervised learning",
            "unsupervised learning", "data science", "model", "algorithm"
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

        # Bonus for AI-related topics from GitHub (0.2 points)
        if topics:
            ai_topics = [
                "artificial-intelligence", "machine-learning", "deep-learning",
                "neural-network", "llm", "gpt", "nlp", "computer-vision",
                "generative-ai", "transformers", "pytorch", "tensorflow",
                "chatbot", "ai-agent", "rag", "embeddings", "langchain"
            ]
            topic_matches = sum(1 for topic in topics if topic.lower() in ai_topics)
            if topic_matches > 0:
                score += 0.2

        return min(score, 1.0)

    async def _fetch_repo_details(self, full_name: str) -> Optional[Dict]:
        """
        Fetch repository details from GitHub API including topics and README.
        Returns dict with topics, language, description, and readme_content.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Fetch repository metadata
                repo_url = f"{self.api_base_url}/repos/{full_name}"
                response = await client.get(repo_url, headers=self.api_headers, timeout=10.0)
                response.raise_for_status()
                repo_data = response.json()

                topics = repo_data.get("topics", [])
                language = repo_data.get("language", "")
                description = repo_data.get("description", "")

                # Fetch README content
                readme_content = await self._fetch_readme(client, full_name)

                return {
                    "topics": topics,
                    "language": language,
                    "description": description,
                    "readme_content": readme_content
                }
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.warning(f"Repository {full_name} not found via API")
                elif e.response.status_code == 403:
                    logger.warning(f"Rate limit exceeded or access forbidden for {full_name}")
                else:
                    logger.error(f"HTTP error fetching repo details for {full_name}: {e}")
                return None
            except Exception as e:
                logger.error(f"Error fetching repo details for {full_name}: {e}")
                return None

    async def _fetch_readme(self, client: httpx.AsyncClient, full_name: str) -> str:
        """
        Fetch and parse README content from GitHub API.
        Returns plain text content (first 5000 chars for analysis).
        """
        try:
            readme_url = f"{self.api_base_url}/repos/{full_name}/readme"
            response = await client.get(readme_url, headers=self.api_headers, timeout=10.0)
            response.raise_for_status()
            readme_data = response.json()

            # README is base64 encoded
            import base64
            content_encoded = readme_data.get("content", "")
            if content_encoded:
                content_bytes = base64.b64decode(content_encoded)
                content_text = content_bytes.decode("utf-8", errors="ignore")
                # Return first 5000 characters for analysis (enough to identify AI tools)
                return content_text[:5000]
            return ""
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:  # README not found is common
                logger.debug(f"README not found for {full_name}")
            return ""
        except Exception as e:
            logger.error(f"Error fetching README for {full_name}: {e}")
            return ""

    async def get_trending_repos(self, language: str = "python", min_ai_score: float = 0.3) -> List[Dict]:
        """
        Scrape GitHub trending page and return AI-related projects.

        Uses enhanced AI detection including:
        - Multi-tier keyword matching with scoring
        - GitHub API topic analysis
        - README content analysis

        Args:
            language: Programming language filter (default: "python")
            min_ai_score: Minimum AI relevance score (0.0-1.0, default: 0.3)

        Returns:
            List of repo dicts with AI score, topics, and metadata
        """
        url = f"{self.base_url}/{language}?since=daily"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=20.0)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")

                repos = []
                # GitHub trending repo items are in <article class="Box-row">
                items = soup.find_all("article", class_="Box-row")

                logger.info(f"Found {len(items)} trending repositories to analyze")

                for item in items:
                    # Get repo name and owner
                    h2 = item.find("h2", class_="h3")
                    if not h2:
                        continue
                    a_tag = h2.find("a")
                    if not a_tag:
                        continue
                    full_name = a_tag.get_text(strip=True).replace(" ", "")

                    # Get description from trending page
                    p = item.find("p", class_="col-9")
                    description = p.get_text(strip=True) if p else ""

                    # Get stars today
                    stars_today_span = item.find("span", class_="d-inline-block float-sm-right")
                    stars_today_text = stars_today_span.get_text(strip=True) if stars_today_span else "0"
                    try:
                        stars_today = int(stars_today_text.split()[0].replace(",", ""))
                    except:
                        stars_today = 0

                    # Fetch detailed repo information from GitHub API
                    repo_details = await self._fetch_repo_details(full_name)

                    # If API fetch failed, use basic description for scoring
                    if repo_details:
                        topics = repo_details.get("topics", [])
                        api_description = repo_details.get("description", "")
                        readme_content = repo_details.get("readme_content", "")
                        language_detected = repo_details.get("language", "")

                        # Use API description if available, otherwise use scraped description
                        full_description = api_description or description

                        # Combine all text for AI scoring
                        combined_text = f"{full_name} {full_description} {readme_content}"
                    else:
                        topics = []
                        full_description = description
                        combined_text = f"{full_name} {description}"
                        language_detected = ""

                    # Calculate AI relevance score
                    ai_score = self._calculate_ai_score(combined_text, topics)

                    # Filter by minimum AI score
                    if ai_score < min_ai_score:
                        logger.debug(f"Skipping {full_name} (AI score: {ai_score:.2f} < {min_ai_score})")
                        continue

                    logger.info(f"Found AI repo: {full_name} (score: {ai_score:.2f}, topics: {topics})")

                    repos.append({
                        "name": full_name.split("/")[-1],
                        "full_name": full_name,
                        "description": full_description,
                        "url": f"https://github.com/{full_name}",
                        "stars_today": stars_today,
                        "ai_score": ai_score,
                        "topics": topics,
                        "language": language_detected,
                        "has_readme": bool(repo_details and repo_details.get("readme_content"))
                    })

                logger.info(f"Filtered to {len(repos)} AI-related repositories (min score: {min_ai_score})")
                return repos

            except Exception as e:
                logger.error(f"Error scraping GitHub trending: {e}")
                return []
