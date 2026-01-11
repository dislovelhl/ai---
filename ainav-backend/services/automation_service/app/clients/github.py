import httpx
from shared.config import settings
import logging
import re

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self):
        self.api_url = "https://api.github.com/repos"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if settings.GITHUB_TOKEN and "your_" not in settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    def _extract_repo_path(self, url: str):
        """Extract 'owner/repo' from various GitHub URL formats."""
        match = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git|/|$)", url)
        if match:
            return match.group(1)
        return None

    async def get_repo_stats(self, url: str):
        repo_path = self._extract_repo_path(url)
        if not repo_path:
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/{repo_path}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "last_updated": data.get("updated_at"),
                    "license": data.get("license", {}).get("name") if data.get("license") else None,
                    "language": data.get("language")
                }
            except Exception as e:
                logger.error(f"Error fetching GitHub stats for {url}: {e}")
                return None
