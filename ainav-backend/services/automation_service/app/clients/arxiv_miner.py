import httpx
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ArXivMiner:
    def __init__(self):
        self.base_url = "https://export.arxiv.org/api/query"

    async def get_latest_papers(self, category: str = "cs.AI", days: int = 1) -> List[Dict]:
        """Fetch latest AI papers from ArXiv."""
        # Query for papers in category, sorted by last updated date
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": 10,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params, timeout=20.0)
                response.raise_for_status()
                
                # Parse Atom feed (XML)
                root = ET.fromstring(response.text)
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                
                papers = []
                for entry in root.findall('atom:entry', namespace):
                    title = entry.find('atom:title', namespace).text.strip()
                    summary = entry.find('atom:summary', namespace).text.strip()
                    url = entry.find('atom:id', namespace).text.strip()
                    published = entry.find('atom:published', namespace).text.strip()
                    
                    # Convert to Tool-like structure
                    papers.append({
                        "name": title[:100], # Name might be too long
                        "title": title,
                        "description": summary,
                        "url": url,
                        "published_at": published,
                        "category": "Scientific Paper"
                    })
                
                return papers
            except Exception as e:
                logger.error(f"Error mining ArXiv: {e}")
                return []
