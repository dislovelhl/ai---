import httpx
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class GitHubTrendingClient:
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def get_trending_repos(self, language: str = "python") -> List[Dict]:
        """Scrape GitHub trending page for AI related projects."""
        url = f"{self.base_url}/{language}?since=daily"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=20.0)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")
                
                repos = []
                # GitHub trending repo items are in <article class="Box-row">
                items = soup.find_all("article", class_="Box-row")
                
                for item in items:
                    # Get repo name and owner
                    h2 = item.find("h2", class_="h3")
                    if not h2: continue
                    a_tag = h2.find("a")
                    if not a_tag: continue
                    full_name = a_tag.get_text(strip=True).replace(" ", "")
                    # owner, name = full_name.split("/")
                    
                    # Get description
                    p = item.find("p", class_="col-9")
                    description = p.get_text(strip=True) if p else ""
                    
                    # GitHub Trending doesn't have a direct "topic" filter in HTML, 
                    # but we can filter description for AI keywords
                    ai_keywords = ["ai", "llm", "gpt", "model", "inference", "agent", "rag", "intelligence", "transformer"]
                    is_ai = any(kw in description.lower() or kw in full_name.lower() for kw in ai_keywords)
                    
                    if not is_ai:
                        continue

                    # Get stars today
                    stars_today_span = item.find("span", class_="d-inline-block float-sm-right")
                    stars_today_text = stars_today_span.get_text(strip=True) if stars_today_span else "0"
                    # "123 stars today" -> 123
                    try:
                        stars_today = int(stars_today_text.split()[0].replace(",", ""))
                    except:
                        stars_today = 0

                    repos.append({
                        "name": full_name.split("/")[-1],
                        "full_name": full_name,
                        "description": description,
                        "url": f"https://github.com/{full_name}",
                        "stars_today": stars_today
                    })
                
                return repos
            except Exception as e:
                logger.error(f"Error scraping GitHub trending: {e}")
                return []
