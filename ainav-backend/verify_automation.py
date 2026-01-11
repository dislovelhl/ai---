import asyncio
import sys
import os

# Add /app to sys.path
sys.path.append("/app")

async def test_scrapers():
    print("--- Testing GitHub Trending Scraper ---")
    try:
        from services.automation_service.app.clients.github_trending import GitHubTrendingClient
        gt_client = GitHubTrendingClient()
        repos = await gt_client.get_trending_repos()
        print(f"Found {len(repos)} trending AI repos.")
        if repos:
            print(f"Sample: {repos[0]['full_name']} - {repos[0]['stars_today']} stars today")
    except Exception as e:
        print(f"GitHub Trending failed: {e}")

    print("\n--- Testing ArXiv Miner ---")
    try:
        from services.automation_service.app.clients.arxiv_miner import ArXivMiner
        arxiv_miner = ArXivMiner()
        papers = await arxiv_miner.get_latest_papers()
        print(f"Found {len(papers)} latest AI papers.")
        if papers:
            print(f"Sample: {papers[0]['name']}")
    except Exception as e:
        print(f"ArXiv Miner failed: {e}")

    print("\n--- Testing Product Hunt (filtered) ---")
    try:
        from services.automation_service.app.clients.producthunt import ProductHuntClient
        ph_client = ProductHuntClient()
        ph_tools = await ph_client.get_daily_ai_tools()
        print(f"Found {len(ph_tools)} tools on Product Hunt.")
        count_above_100 = sum(1 for edge in ph_tools if edge["node"].get("votesCount", 0) >= 100)
        print(f"Tools with votes >= 100: {count_above_100}")
    except Exception as e:
        # Might fail due to missing token
        print(f"Product Hunt failed (check token): {e}")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
