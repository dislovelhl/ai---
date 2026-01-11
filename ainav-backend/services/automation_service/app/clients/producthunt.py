import httpx
from shared.config import settings
import logging

logger = logging.getLogger(__name__)

class ProductHuntClient:
    def __init__(self):
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {settings.PRODUCTHUNT_TOKEN}",
            "Content-Type": "application/json",
        }

    async def get_daily_ai_tools(self):
        query = """
        query($cursor: String) {
          posts(topic: "artificial-intelligence", first: 10, after: $cursor) {
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
              }
            }
          }
        }
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url, 
                    json={"query": query}, 
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("posts", {}).get("edges", [])
            except Exception as e:
                logger.error(f"Error fetching from Product Hunt: {e}")
                return []
