import asyncio
import sys
import os

# Add the ainav-backend directory and automation-service to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "automation-service")))

from app.clients.github import GitHubClient

async def test_github():
    client = GitHubClient()
    url = "https://github.com/fastapi/fastapi"
    print(f"Testing GitHub stats for: {url}")
    stats = await client.get_repo_stats(url)
    if stats:
        print(f"Stars: {stats['stars']}")
        print(f"Language: {stats['language']}")
    else:
        print("Failed to fetch stats.")

if __name__ == "__main__":
    asyncio.run(test_github())
