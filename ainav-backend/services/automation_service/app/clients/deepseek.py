import httpx
from shared.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_url = settings.DEEPSEEK_API_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def enrich_tool_info(self, name: str, description: str):
        prompt = f"""
        As an AI tool expert, please enrich the following tool information for a Chinese AI navigation platform.
        Tool Name: {name}
        Description: {description}

        Please provide the response in a JSON format with the following fields:
        - name_zh: A concise and professional Chinese name for the tool.
        - description_zh: A high-quality Chinese translation of the description.
        - tags: A list of 3-5 relevant Chinese keywords/tags.
        - pricing_type: One of 'free', 'freemium', 'paid'.
        - summary: A one-sentence Chinese summary.
        - suggested_category: The most appropriate category slug from this list: 'ai-chatbots', 'image-generation', 'code-assistants', 'writing-content', 'video-generation', 'audio-music', 'productivity', 'research-analysis', 'content-creation', 'marketing', 'development', 'education', 'business', 'personal-use', 'design', 'research'. If none fit well, use 'productivity'.
        - category_confidence: A float between 0.0 and 1.0 indicating your confidence in the category assignment.
        - is_ai_tool: A boolean (true/false) indicating whether this is an AI-powered tool or service.
        - ai_tool_confidence: A float between 0.0 and 1.0 indicating your confidence that this is an AI tool.

        JSON Response Only:
        """

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception as e:
                logger.error(f"Error enriching with DeepSeek: {e}")
                return None
