import os
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime, timedelta
import google.generativeai as genai
from duckduckgo_search import DDGS

class SentimentEngine:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-flash-latest" 
        self._cache = None
        self._cache_time = None
        self._cache_ttl = timedelta(minutes=15)
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
        else:
            self.model = None

    async def get_market_mood(self) -> Dict[str, Any]:
        # Caching logic
        if self._cache and self._cache_time and (datetime.now() - self._cache_time) < self._cache_ttl:
            print("DEBUG: Returning cached sentiment data")
            return self._cache

        try:
            # 1. Fetch top 5 news URLs
            urls = []
            with DDGS() as ddgs:
                results = list(ddgs.news(keywords="gold price market analysis", max_results=5))
                urls = [r['url'] for r in results if 'url' in r]

            if not urls:
                return self._fallback_response("No recent news found for analysis")

            # 2. Scrape content asynchronously
            contents = await self._scrape_urls(urls)
            aggregated_text = "\n\n".join([c for c in contents if c.strip()])[:8000]

            if not aggregated_text.strip():
                return self._fallback_response("Failed to retrieve content from news articles")

            # 3. Analyze with Gemini
            prompt = f"""
            Analyze the sentiment of the following news articles regarding Gold prices.
            Return a STRICT JSON object with these fields:
            - sentiment_score: int (0 to 100, where 0 is extremely bearish and 100 is extremely bullish)
            - mood_label: string (one of: 'Bearish', 'Neutral', 'Bullish')
            - key_factors: list of strings (top 3-5 factors driving this sentiment)

            Articles Content:
            {aggregated_text}
            """

            response = self.model.generate_content(prompt)
            import json
            result = json.loads(response.text.strip())
            
            # Update cache
            self._cache = result
            self._cache_time = datetime.now()
            
            return result

        except Exception as e:
            print(f"Sentiment Error: {e}")
            return self._fallback_response(f"Analysis Error: {str(e)}")

    async def _scrape_urls(self, urls: List[str]) -> List[str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
            tasks = [self._fetch_content(client, url) for url in urls]
            return await asyncio.gather(*tasks)

    async def _fetch_content(self, client: httpx.AsyncClient, url: str) -> str:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.extract()
                return soup.get_text(separator=' ', strip=True)[:2000]
            return ""
        except:
            return ""

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        return {
            "sentiment_score": 50,
            "mood_label": "Neutral",
            "key_factors": [message],
            "error": True
        }
